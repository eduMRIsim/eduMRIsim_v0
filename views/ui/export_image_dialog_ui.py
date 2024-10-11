import numpy as np
from PIL import Image
from PyQt6.QtWidgets import QDialog, QFileDialog
import pydicom
from pydicom.dataset import FileDataset
from pydicom.fileset import FileSet
from pydicom.uid import ExplicitVRLittleEndian
import nibabel as nib
import os

from simulator.examination import Examination
from utils.logger import log
from simulator.scanlist import AcquiredImage, ImageGeometry, AcquiredSeries


class ExportImageDialog(QDialog):
    """
    This class represents a dialog to export acquired images to image files.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choose a file location")
        self.instance_number = 1

    def export_file_dialog(self, image: AcquiredImage | None, series: AcquiredSeries, study: Examination, parameters: dict) -> None:
        """
        This method exports (acquired) image data to an image file through a file save dialog.
        """

        if image is None:
            raise ValueError("No image found to export")

        image_data: np.ndarray = image.image_data
        image_geometry: ImageGeometry = image.image_geometry

        if image_data is None:
            raise ValueError(
                "No image data found; at least one scan should be performed before attempting to export an image"
            )
        if image_geometry is None:
            raise ValueError(
                "No image geometry found; at least one scan should be performed before attempting to export an image"
            )

        # Open a save file dialog so that the user can save the image.
        file_name: str
        selected_filter: str
        file_name, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export image to file",
            filter="JPEG Files (*.jpeg);;PNG Files (*.png);;DICOM Files (*.dcm);;NIfTI Files (*.nii);;Compressed (Zipped) NIfTI Files (*.nii.gz)",
        )

        # If the user specified a file name, save the image in that file name and using the filter that they selected.
        if file_name:
            if selected_filter == "JPEG Files (*.jpeg)":
                # Convert the normalized image data to a grayscale JPEG image.
                # The mode, "L", is for 8-bit pixels, grayscale.
                # This may be something to change in the future if we want different color scales.
                ExportImageDialog.export_to_standard_image_file(
                    file_name, image_data, "jpeg"
                )
                log.info(f"JPEG file saved as {file_name}")
            elif selected_filter == "PNG Files (*.png)":
                # Convert the normalized image data to a grayscale PNG image.
                # The mode, "L", is for 8-bit pixels, grayscale.
                # This may be something to change in the future if we want different color scales.
                ExportImageDialog.export_to_standard_image_file(
                    file_name, image_data, "png"
                )
                log.info(f"PNG file saved as {file_name}")
            elif selected_filter == "DICOM Files (*.dcm)":
                self.export_to_dicom_file(
                    file_name, image, series, study, parameters
                )
                log.info(f"DICOM file saved as {file_name}")
            elif (
                selected_filter == "NIfTI Files (*.nii)"
                or selected_filter == "Compressed (Zipped) NIfTI Files (*.nii.gz)"
            ):
                ExportImageDialog.export_to_nifti_file(file_name, image_data)
                log.info(f"NIfTI file saved as {file_name}")
            else:
                raise ValueError(
                    f"Unknown file format filter selected: {selected_filter}"
                )

    @staticmethod
    def export_to_standard_image_file(
        file_name: str, image_data: np.ndarray, file_filter: str
    ) -> None:
        """
        Static method to export image data to a standard image file, e.g. JPEG or PNG files.
        """

        # Normalize the image data array by scaling it down to a floating point value in range [0.0, 1.0]
        # and multiplying by 255.0.
        # Also, set the type of the normalized data array to np.uint8.
        max_val: float = np.max(image_data)
        min_val: float = np.min(image_data)
        image_data_normalized = ((image_data - min_val) / (max_val - min_val)) * 255.0
        image_data_normalized = image_data_normalized.astype(np.uint8)

        image = Image.fromarray(image_data_normalized, mode="L")
        image.save(file_name, filter=file_filter)

    def export_to_dicom_with_dicomdir(
            self, image: AcquiredImage, series: AcquiredSeries, study: Examination, parameters: dict
    ) -> None:

        dicomdir_path = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Choose a directory for the DICOM folder with DICOMDIR file",
        )
        if dicomdir_path:
            dicomdir_path = os.path.join(dicomdir_path, "DICOM").replace("\\", "/")
            fs = FileSet()
            if os.path.exists(dicomdir_path):
                fs.load(os.path.join(dicomdir_path, "DICOMDIR").replace("\\", "/"))
                log.info(f"Loaded existing DICOMDIR file from {dicomdir_path}")

            image_data: np.ndarray = image.image_data
            image_geometry: ImageGeometry = image.image_geometry

            image_data_normalized = ExportImageDialog._normalize_image_data_for_dicom(image_data)

            # Create a FileDataset instance and set some DICOM attributes on it
            file_meta = ExportImageDialog._create_file_meta_for_dicom()
            ds = FileDataset("this_is_the_file_name", {}, file_meta=file_meta, preamble=b"\0" * 128)

            self._set_dicom_attributes(ds, file_meta, image, image_data_normalized, image_geometry, parameters, series,
                                       study)

            fs.add(ds)

            if os.path.exists(os.path.join(dicomdir_path, "DICOMDIR").replace("\\", "/")):
                fs.write()
                log.info(f"Wrote to existing DICOMDIR file to {dicomdir_path}")
            else:
                fs.write(dicomdir_path)
                log.info(f"Wrote to new DICOMDIR file at {dicomdir_path}")

    def export_to_dicom_file(
        self, file_name: str, image: AcquiredImage, series: AcquiredSeries, study: Examination, parameters: dict
    ) -> None:
        """
        Export image data to a DICOM file.
        For reference, the following websites were used for the DICOM attributes that are set within this method:
            https://dicom.innolitics.com/ciods/mr-image
            http://dicomlookup.com/

        Args:
            file_name: The name of and path to the DICOM file to save.
            image: The acquired image to save to the DICOM file.
            series: The acquired series to which the image belongs.
            study: The examination study to which the series belongs.
            parameters: The scan parameters of the acquired image.
        """
        image_data: np.ndarray = image.image_data
        image_geometry: ImageGeometry = image.image_geometry

        image_data_normalized = ExportImageDialog._normalize_image_data_for_dicom(image_data)

        # Create a FileDataset instance and set some DICOM attributes on it
        file_meta = ExportImageDialog._create_file_meta_for_dicom()
        ds = FileDataset(file_name, {}, file_meta=file_meta, preamble=b"\0" * 128)

        self._set_dicom_attributes(ds, file_meta, image, image_data_normalized, image_geometry, parameters, series,
                                   study)

        # Save the DICOM file
        ds.save_as(file_name)

    @staticmethod
    def _create_file_meta_for_dicom():
        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.MRImageStorage
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        file_meta.ImplementationClassUID = pydicom.uid.generate_uid()
        return file_meta

    @staticmethod
    def _normalize_image_data_for_dicom(image_data):
        # Normalize the image data array
        max_val: float = np.max(image_data)
        min_val: float = np.min(image_data)
        image_data_normalized = ((image_data - min_val) / (max_val - min_val)) * 4095.0
        image_data_normalized = image_data_normalized.astype(np.uint16)
        return image_data_normalized

    def _set_dicom_attributes(self, ds, file_meta, image, image_data_normalized, image_geometry, parameters, series,
                              study) -> None:
        # Set some required DICOM attributes
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        # Set DICOM attributes either referring to image data, or referring to one of the scan parameters
        ds.Modality = "MR"
        ds.Rows, ds.Columns = image_data_normalized.shape
        ds.BitsAllocated = 16  # Should be correct now, but may still need to be changed in the future
        ds.BitsStored = 12  # Should be correct now, but may still need to be changed in the future
        ds.HighBit = 11  # Should be correct now, but may still need to be changed in the future
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1  # This may be changed in the future
        ds.PhotometricInterpretation = "MONOCHROME2"  # Set this to a different value if a different color scale is used
        ds.RescaleIntercept = 0
        ds.RescaleSlope = 1
        ds.RescaleType = "US"
        ds.PixelData = image_data_normalized.tobytes()
        ds.SliceThickness = parameters["SliceThickness_mm"]
        ds.SpacingBetweenSlices = parameters[
            "SliceGap_mm"
        ]  # This is referred to as "Slice gap" in the scan parameters
        ds.ScanningSequence = parameters[
            "ScanTechnique"
        ]  # This is referred to as "Scan technique" in the scan parameters
        ds.EchoTime = parameters["TE_ms"]
        ds.RepetitionTime = parameters["TR_ms"]
        ds.InversionTime = parameters["TI_ms"]
        ds.ImagePositionPatient = list(image_geometry.origin_LPS)
        ds.ImageOrientationPatient = image_geometry.axisX_LPS.tolist()
        ds.ImageOrientationPatient.extend(image_geometry.axisY_LPS.tolist())
        ds.PatientName = "Test^Patient"
        ds.PatientID = "PT000000"
        ds.StudyID = str(study.study_id)
        ds.SeriesNumber = str(series.series_number)
        if image.instance_number:
            ds.InstanceNumber = image.instance_number
        else:
            ds.InstanceNumber = self.instance_number
            self.instance_number += 1
        ds.StudyDate = study.study_date
        ds.StudyTime = study.study_time
        ds.SeriesDate = series.series_date
        ds.SeriesTime = series.series_time
        ds.StudyInstanceUID = study.study_instance_uid
        ds.SeriesInstanceUID = series.series_instance_uid
        ds.AcquisitionDate = image.acquisition_date
        ds.AcquisitionTime = image.acquisition_time
        ds.ContentDate = image.content_date
        ds.ContentTime = image.content_time

    @staticmethod
    def export_to_nifti_file(file_name: str, image_data: np.ndarray) -> None:
        """
        Static method to export image data to a (compressed) NIfTI file.
        """
        # Create an affine transformation matrix
        # Currently, this is just the identity matrix, but this may be changed in the future.
        transformation_matrix: np.ndarray = np.eye(4)

        # if file_name.endswith(".nii"):
        image_data = np.rot90(image_data)
        image_data = np.flip(image_data, axis=0)

        # Create a NIfTI image
        nifti_img = nib.Nifti1Image(image_data, transformation_matrix)

        # Save the NIfTI image to a file.
        nib.save(nifti_img, file_name)
