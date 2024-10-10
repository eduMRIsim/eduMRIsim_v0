import numpy as np
from scipy import interpolate
from utils.logger import log
from simulator.MRI_data_synthesiser import MRIDataSynthesiser
from simulator.examination import Examination
from simulator.model import Model
from simulator.scanlist import (
    AcquiredSeries,
    AcquiredImage,
    ImageGeometry,
    ScanItemStatusEnum,
)


class Scanner:

    def __init__(self):

        self.MRI_data_synthesiser = (
            MRIDataSynthesiser()
        )  # Create an instance of the MRIDataSynthesiser class. The MRIDataSynthesiser class is responsible for synthesising MRI data from the model and scan parameters. Not relevant for SEP project.
        self.examination = None

    def scan(self) -> AcquiredSeries:
        """Scan the model with the scan parameters defined in the scan item and return an acquired series. The acquired series is a list of acquired 2D images that represent the slices of the scanned volume."""
        scan_item = self.active_scan_item
        series_name = scan_item.name

        active_params = scan_item.get_current_active_parameters()
        # scan_plane = scan_item.scan_parameters["ScanPlane"]
        scan_plane = active_params["ScanPlane"]

        signal_array = self.MRI_data_synthesiser.synthesise_MRI_data(
            # scan_item.scan_parameters, self.model
            active_params, self.model
        )
        list_acquired_images = []
        # n_slices = int(scan_item.scan_parameters["NSlices"])
        n_slices = int(active_params["NSlices"])
        for i in range(n_slices):
            # for each slice create an acquired image
            # Step 1: create image geometry of slice
            # image_geometry = scan_item.scan_volume.get_image_geometry_of_slice(i)
            scan_vol = scan_item.get_current_active_scan_volume()
            image_geometry = scan_vol.get_image_geometry_of_slice(i)
            # Step 2: get image data of slice
            image_data = self._get_image_data_from_signal_array(
                image_geometry, self.model, signal_array
            )
            # Step 3: create acquired image
            acquired_image = AcquiredImage(image_data, image_geometry)
            list_acquired_images.append(acquired_image)
        # Create an acquired series from the list of acquired images
        acquired_series = AcquiredSeries(series_name, scan_plane, list_acquired_images)
        self.active_scanlist_element.acquired_data = acquired_series
        self.active_scan_item.status = ScanItemStatusEnum.COMPLETE
        return acquired_series

    def _get_image_data_from_signal_array(
        self, image_geometry: ImageGeometry, model: Model, signal_array: np.ndarray
    ) -> np.ndarray:
        # The signal array was created by calculating the signal at the points on the meshgrid defined below
        model_extentX = model.XDimRes_mm * model.XDim
        model_extentY = model.YDimRes_mm * model.YDim
        model_extentZ = model.ZDimRes_mm * model.ZDim
        x_sample = np.linspace(
            -(model_extentX / 2) + (model.XDimRes_mm / 2),
            (model_extentX / 2) - (model.XDimRes_mm / 2),
            int(model.XDim),
        )
        y_sample = np.linspace(
            -(model_extentY / 2) + (model.YDimRes_mm / 2),
            (model_extentY / 2) - (model.YDimRes_mm / 2),
            int(model.YDim),
        )
        z_sample = np.linspace(
            -(model_extentZ / 2) + (model.ZDimRes_mm / 2),
            (model_extentZ / 2) - (model.ZDimRes_mm / 2),
            int(model.ZDim),
        )

        inter_func = interpolate.RegularGridInterpolator(
            (y_sample, x_sample, z_sample),
            signal_array,
            method="linear",
            bounds_error=False,
            fill_value=0,
        )  # Create an interpolation function that can be used to sample the signal array at any point in the FOV. The fill_value is set to 0, which means that if the point is outside the FOV, the signal intensity will be 0. The x and y coordinates are swapped in the interpolation function because the x-coordinate corresponds to the columns of the signal array and the y-coordinate corresponds to the rows.

        # Create a meshgrid of points in the FOV to sample the signal array in FOV coordinates
        image_geometry = image_geometry
        NFOVx = np.ceil(image_geometry.extentX_mm / model.XDimRes_mm).astype(int)
        NFOVy = np.ceil(image_geometry.extentY_mm / model.YDimRes_mm).astype(int)
        NFOVz = 1  # This is temporary until slice selection is implemented

        dFOVx = image_geometry.extentX_mm / NFOVx
        image_geometry.resX_mm = dFOVx
        dFOVy = image_geometry.extentY_mm / NFOVy
        image_geometry.resY_mm = dFOVy
        dFOVz = 1  # This is temporary until slice selection is implemented. Pretend slice thickness is 1 mm
        x_FOV = np.linspace(
            -image_geometry.extentX_mm / 2 + dFOVx / 2,
            image_geometry.extentX_mm / 2 - dFOVx / 2,
            NFOVx,
        )
        y_FOV = np.linspace(
            -image_geometry.extentY_mm / 2 + dFOVy / 2,
            image_geometry.extentY_mm / 2 - dFOVy / 2,
            NFOVy,
        )
        z_FOV = np.linspace(
            -1 / 2 + dFOVz / 2, 1 / 2 - dFOVz / 2, NFOVz
        )  # This is temporary until slice selection is implemented. Pretend slice thickness is 1 mm

        X_FOV, Y_FOV, Z_FOV = np.meshgrid(x_FOV, y_FOV, z_FOV)
        # Convert the FOV coordinates to LPS coordinates
        X_FOV_LPS = (
            X_FOV * image_geometry.axisX_LPS[0]
            + Y_FOV * image_geometry.axisY_LPS[0]
            + Z_FOV * image_geometry.axisZ_LPS[0]
            + image_geometry.origin_LPS[0]
        )
        Y_FOV_LPS = (
            X_FOV * image_geometry.axisX_LPS[1]
            + Y_FOV * image_geometry.axisY_LPS[1]
            + Z_FOV * image_geometry.axisZ_LPS[1]
            + image_geometry.origin_LPS[1]
        )
        Z_FOV_LPS = (
            X_FOV * image_geometry.axisX_LPS[2]
            + Y_FOV * image_geometry.axisY_LPS[2]
            + Z_FOV * image_geometry.axisZ_LPS[2]
            + image_geometry.origin_LPS[2]
        )
        image_data = inter_func(
            (Y_FOV_LPS, X_FOV_LPS, Z_FOV_LPS)
        )  # Sample the signal array at the points in the FOV
        return image_data[
            :, :, 0
        ]  # image_data is a 3D array. The third dimension is 1 because the z dimension is 1. We remove the third dimension to get a 2D array.

    def start_examination(self, exam_name, model):
        self.examination = Examination(exam_name, model)

    def stop_examination(self):
        self.examination = None

    @property
    def model(self):
        try:
            return self.examination.model
        except AttributeError:
            return None

    @property
    def scanlist(self):
        try:
            return self.examination.scanlist
        except AttributeError:
            return None

    @property
    def active_scan_item(self):
        try:
            return self.examination.scanlist.active_scan_item
        except AttributeError:
            return None

    @property
    def active_scanlist_element(self):
        try:
            return self.examination.scanlist.active_scanlist_element
        except AttributeError:
            return None

    def save_state(self):
        if self.examination is not None:

            scanlist_names = [
                ele.name for ele in self.examination.scanlist.scanlist_elements
            ]
            # TODO: ele.scan_item._scan_parameters is now list, does it change something for saving state 
            scnalist_params = [
                ele.scan_item._scan_parameters
                for ele in self.examination.scanlist.scanlist_elements
            ]
            scanlist_data = [
                ele.acquired_data for ele in self.examination.scanlist.scanlist_elements
            ]
            scanlist_status = [
                ele.scan_item._status
                for ele in self.examination.scanlist.scanlist_elements
            ]

            # Serialize the state of the scanner
            state = {
                "scanlist": scanlist_names,
                "params": scnalist_params,
                "data": scanlist_data,
                "status": scanlist_status,
                # 'model': self.model,
            }
            return state
        else:
            log.warning("No examination to save state for")
