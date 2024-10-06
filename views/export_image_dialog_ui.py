import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QDialog, QFileDialog
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import nibabel as nib
import datetime
from utils.logger import log
from simulator.scanlist import AcquiredImage


class ExportImageDialog(QDialog):
    """
    This class represents a dialog to export acquired images to image files.
    """

    def __init__(self, button_index: int | None):
        super().__init__()
        self.setWindowTitle("Choose a file location")

    def export_file_dialog(self, image: AcquiredImage | None) -> None:
        """
        This method exports acquired image data to an image file through a file save dialog.
        """

        if image is None:
            raise ValueError("No acquired image")

        image_data: np.ndarray = image.image_data

        if image_data is None:
            raise ValueError(
                "At least one scan should be performed before trying to export an image"
            )

        # Normalize the image data array by scaling it down to a floating point value in range [0.0, 1.0]
        # and multiplying by 255.0.
        # Also, set the type of the normalized data array to np.uint8.
        max_val: float = np.max(image_data)
        min_val: float = np.min(image_data)
        image_data_normalized = ((image_data - min_val) / (max_val - min_val)) * 255.0
        image_data_normalized = image_data_normalized.astype(np.uint8)

        # Open a save file dialog so that the user can save the image.
        options = QFileDialog.Options()
        file_name: str
        selected_filter: str
        file_name, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export acquired image to file",
            filter="JPEG Files (*.jpeg);;PNG Files (*.png);;DICOM Files (*.dcm);;NIfTI Files (*.nii);;Compressed (Zipped) NIfTI Files (*.nii.gz)",
            options=options,
        )

        # If the user specified a file name, save the image in that file name and using the filter that they selected.
        if file_name:
            if selected_filter == "JPEG Files (*.jpeg)":
                # Convert the normalized image data to a grayscale JPEG image.
                # The mode, "L", is for 8-bit pixels, grayscale.
                # This may be something to change in the future if we want different color scales.
                ExportImageDialog.export_to_standard_image_file(
                    file_name, image_data_normalized, "jpeg"
                )
                log.info(f"JPEG file saved as {file_name}")
            elif selected_filter == "PNG Files (*.png)":
                # Convert the normalized image data to a grayscale PNG image.
                # The mode, "L", is for 8-bit pixels, grayscale.
                # This may be something to change in the future if we want different color scales.
                ExportImageDialog.export_to_standard_image_file(
                    file_name, image_data_normalized, "png"
                )
                log.info(f"PNG file saved as {file_name}")
            elif selected_filter == "DICOM Files (*.dcm)":
                ExportImageDialog.export_to_dicom_file(image_data_normalized, file_name)
                log.info(f"DICOM file saved as {file_name}")
            elif (
                selected_filter == "NIfTI Files (*.nii)"
                or selected_filter == "Compressed NIfTI Files (*.nii.gz)"
            ):
                ExportImageDialog.export_to_nifti_file(image_data_normalized, file_name)
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
        image = Image.fromarray(image_data, mode="L")
        image.save(file_name, filter=file_filter)

    @staticmethod
    def export_to_dicom_file(image_data: np.ndarray, file_name: str) -> None:
        """
        Static method to export image data to a DICOM file.
        """
        # Create a FileDataset instance
        file_meta = pydicom.dataset.FileMetaDataset()
        ds = FileDataset(file_name, {}, file_meta=file_meta, preamble=b"\0" * 128)

        # Set the transfer syntax.
        # Commented out for now, will be implemented properly in the near future.
        # file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        # Add the necessary DICOM tags.
        # These tags should be changed in the future to reflect the actual DICOM tags that are to be used.
        ds.PatientName = "Test^Firstname"
        ds.PatientID = "123456"
        ds.Modality = "CT"
        ds.StudyInstanceUID = "1.2.3.4"
        ds.SeriesInstanceUID = "1.2.3.4.5"
        ds.SOPInstanceUID = "1.2.3.4.5.6"
        ds.SOPClassUID = pydicom.uid.CTImageStorage

        # Set the image data
        ds.Rows, ds.Columns = image_data.shape
        ds.PixelData = image_data.tobytes()

        # Set additional metadata.
        # This metadata may not be correct, and may be changed in the future.
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1
        ds.InstanceCreationDate = datetime.datetime.now().strftime("%Y%m%d")
        ds.InstanceCreationTime = datetime.datetime.now().strftime("%H%M%S")

        # Save the DICOM file.
        ds.save_as(file_name)

    @staticmethod
    def export_to_nifti_file(image_data: np.ndarray, file_name: str) -> None:
        """
        Static method to export image data to a (compressed) NIfTI file.
        """
        # Create an affine transformation matrix.
        # Currently, this is just the identity matrix, but this may be changed in the future.
        transformation_matrix: np.ndarray = np.eye(4)

        # Create a NIfTI image.
        nifti_img = nib.Nifti1Image(image_data, transformation_matrix)

        # Save the NIfTI image to a file.
        nib.save(nifti_img, file_name)
