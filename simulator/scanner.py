from simulator.examination import Examination
from simulator.scanlist import AcquiredSeries, AcquiredImage, ImageGeometry, ScanVolume
from simulator.model import Model
import numpy as np
from scipy import interpolate

class Scanner:
    """
    Represents an MRI scanner. 
    """
    def __init__(self, name, field_strength):
        """
        Initializes a Scanner object.

        :param name: The name of the scanner.
        :type name: str
        :param field_strength: The field strength of the scanner in Tesla.
        :type field_strength: float
        """
        self._name = name
        self._field_strength = field_strength 
        #self._MRI_data_synthesiser = MRIDataSynthesiser()
        self._examination = None 
    
    # def scan(self):
    #     """
    #     Performs a scan using the scanner's MRIDataSynthesiser.

    #     :return: Data synthesized from the active scan item and model.
    #     :rtype: np.array
    #     """
    #     acquired_data = self.MRI_data_synthesiser.synthesise_MRI_data(self.active_scan_item.scan_parameters, self.model)     
    #     self.scanlist.active_scanlist_element.acquired_data = acquired_data
    #     return acquired_data

      
    def scan(self) -> AcquiredSeries:
        '''Scan the model with the scan parameters defined in the scan item and return an acquired series. The acquired series is a list of acquired 2D images that represent the slices of the scanned volume.'''
        scan_item = self.active_scan_item
        print("scan item parameters", scan_item.scan_parameters)
        signal_array = self._calculate_signal(scan_item.scan_parameters, self.model)
        list_acquired_images = [] 
        n_slices = int(scan_item.scan_parameters['NSlices'])
        for i in range(n_slices):
            # for each slice create an acquired image
            # Step 1: create image geometry of slice
            image_geometry = scan_item.scan_volume.get_image_geometry_of_slice(i)
            # Step 2: get image data of slice
            image_data = self._get_image_data_from_signal_array(image_geometry, self.model, signal_array)
            # careful because _get_image_data_from_signal_array might change image geometry slightly (resolution)
            # Step 3: create acquired image
            acquired_image = AcquiredImage(image_data, image_geometry)
            list_acquired_images.append(acquired_image)
        # Create an acquired series from the list of acquired images
        acquired_series = AcquiredSeries(list_acquired_images)
        self.scanlist.active_scanlist_element.acquired_data = acquired_series
        return acquired_series

    def _calculate_signal(self, scan_parameters: dict, model: Model) -> np.ndarray:
        '''Calculate the signal intensity given the scan parameters for each voxel of the model. Note that the signal intensity is calculated using the signal equation for a spin echo sequence. 
        
        Args: 
        scan_parameters (dict): A dictionary containing the scan parameters
        model (Model): The model to scan'''

        TE = float(scan_parameters['TE_ms'])
        TR = float(scan_parameters['TR_ms'])
        TI = float(scan_parameters['TI_ms'])

        T1map = model.T1map_msec
        T2map = model.T2map_msec
        PDmap = model.PDmap

        signal_array = np.abs(PDmap * np.exp(np.divide(-TE,T2map)) * (1 - 2 * np.exp(np.divide(-TI, T1map)) + np.exp(np.divide(-TR, T1map)))) # calculate the signal intensity using the signal equation for a spin echo sequence.  
        signal_array = np.nan_to_num(signal_array, nan=0) # replace all nan values with 0. This is necessary because the signal_array can contain nan values, for example if both TI and T1 are 0.         

        return signal_array

    def _get_image_data_from_signal_array(self, image_geometry: ImageGeometry, model: Model, signal_array: np.ndarray) -> np.ndarray:
        # The signal array was created by calculating the signal at the points on the meshgrid defined below
        model_extentX = model.XDimRes_mm * model.XDim
        model_extentY = model.YDimRes_mm * model.YDim
        model_extentZ = model.ZDimRes_mm * model.ZDim
        x_sample = np.linspace(-(model_extentX / 2) + (model.XDimRes_mm / 2), (model_extentX / 2) - (model.XDimRes_mm / 2), int(model.XDim))    
        y_sample = np.linspace(-(model_extentY / 2) + (model.YDimRes_mm / 2), (model_extentY / 2) - (model.YDimRes_mm / 2), int(model.YDim))
        z_sample = np.linspace(-(model_extentZ / 2) + (model.ZDimRes_mm / 2), (model_extentZ / 2) - (model.ZDimRes_mm / 2), int(model.ZDim))

        inter_func = interpolate.RegularGridInterpolator((y_sample, x_sample, z_sample), signal_array, method = 'linear', bounds_error=False, fill_value=0) # Create an interpolation function that can be used to sample the signal array at any point in the FOV. The fill_value is set to 0, which means that if the point is outside the FOV, the signal intensity will be 0. The x and y coordinates are swapped in the interpolation function because the x-coordinate corresponds to the columns of the signal array and the y-coordinate corresponds to the rows.

        # Create a meshgrid of points in the FOV to sample the signal array in FOV coordinates
        image_geometry = image_geometry
        NFOVx = np.ceil(image_geometry.extentX_mm / model.XDimRes_mm).astype(int)
        NFOVy = np.ceil(image_geometry.extentY_mm / model.YDimRes_mm).astype(int)
        NFOVz = 1 # This is temporary until slice selection is implemented

        dFOVx = image_geometry.extentX_mm / NFOVx
        dFOVy = image_geometry.extentY_mm / NFOVy
        dFOVz = 1 # This is temporary until slice selection is implemented. Pretend slice thickness is 1 mm
        x_FOV = np.linspace(- image_geometry.extentX_mm / 2 + dFOVx / 2, image_geometry.extentX_mm / 2 - dFOVx / 2, NFOVx)
        y_FOV = np.linspace(- image_geometry.extentY_mm / 2 + dFOVy / 2, image_geometry.extentY_mm / 2 - dFOVy / 2, NFOVy)
        z_FOV = np.linspace(- 1 / 2 + dFOVz / 2, 1/ 2 - dFOVz / 2, NFOVz) # This is temporary until slice selection is implemented. Pretend slice thickness is 1 mm


        X_FOV, Y_FOV, Z_FOV = np.meshgrid(x_FOV, y_FOV, z_FOV) 
        # Convert the FOV coordinates to LPS coordinates
        X_FOV_LPS = X_FOV * image_geometry.axisX_LPS[0] + Y_FOV * image_geometry.axisY_LPS[0] + Z_FOV * image_geometry.axisZ_LPS[0] + image_geometry.origin_LPS[0] 
        Y_FOV_LPS = X_FOV * image_geometry.axisX_LPS[1] + Y_FOV * image_geometry.axisY_LPS[1] + Z_FOV * image_geometry.axisZ_LPS[1] + image_geometry.origin_LPS[1]
        Z_FOV_LPS = X_FOV * image_geometry.axisX_LPS[2] + Y_FOV * image_geometry.axisY_LPS[2] + Z_FOV * image_geometry.axisZ_LPS[2] + image_geometry.origin_LPS[2]
        image_data = inter_func((Y_FOV_LPS, X_FOV_LPS, Z_FOV_LPS)) # Sample the signal array at the points in the FOV
        return image_data[:,:,0] # image_data is a 3D array. The third dimension is 1 because the z dimension is 1. We remove the third dimension to get a 2D array.


    def start_examination(self, exam_name, model):
        """_summary_

        :param exam_name: _description_
        :type exam_name: _type_
        :param model: _description_
        :type model: _type_
        """
        self.examination = Examination(exam_name, model)

    def stop_examination(self):
        self.examination = None

    @property
    def MRI_data_synthesiser(self):
        return self._MRI_data_synthesiser

    @property
    def examination(self):
        try :
            return self._examination
        except AttributeError:
            return None

    @examination.setter
    def examination(self, new_examination):
        self._examination = new_examination

    @property
    def name(self):
        return self._name 
    
    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def field_strength(self):
        return self._field_strength 
    
    @field_strength.setter
    def field_strength(self, new_field_strength):
        self._field_strength = new_field_strength 

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
        