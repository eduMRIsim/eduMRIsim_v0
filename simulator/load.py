import json
import numpy as np
from scipy.io import loadmat

def load_json(jsonFilePath):
        with open(jsonFilePath, 'r') as json_file:
            data = json.load(json_file)
        return data
    
   
def load_model_data(path_to_data):
    '''Load the data from the .mat file and return a dictionary of the fields in the .mat file. The .mat file contains a 1x1 struct called VObj (stands for Virtual Object). VObj contains the 16 fields described in https://mrilab.sourceforge.net/manual/MRiLab_User_Guide_v1_3/MRiLab_User_Guidech3.html#x8-120003.1
    
    Args:
    path_to_data (str): The path to the .mat file containing the data
    
    Returns:
    data_dict (dict): A dictionary containing the 16 fields in the VObj struct'''


    # Load the .mat file. 
    mat_contents = loadmat(path_to_data)

    # Access the VObj struct
    VObj = mat_contents['VObj']

    # Create a dictionary of the fields
    data_dict = {}
    for field_name in VObj.dtype.names:
        if VObj[0, 0][field_name].shape[0] == 1:
            try:
                data_dict[field_name] = VObj[0, 0][field_name][0][0]
            except:
                data_dict[field_name] = VObj[0, 0][field_name][0]
        else:
            data_dict[field_name] = VObj[0, 0][field_name]


    # Rotate the T1map, T2map, T2smap, and PDmap 180 degrees around the x-axis. This is necessary because the data is stored in RAS orientation in the .mat file compared to the orientation expected by the scan function: LPS orientation.

    T1map = data_dict['T1']
    T2map = data_dict['T2']
    T2smap = data_dict['T2Star']
    PDmap = data_dict['Rho']

    # Rotate T1map 180 degrees around the x-axis
    for x_idx in range(T1map.shape[0]):
        T1map[x_idx,:,:] = np.rot90(T1map[x_idx,:,:], 2)
    # Rotate T2map 180 degrees around the x-axis
    for x_idx in range(T2map.shape[0]):
        T2map[x_idx,:,:] = np.rot90(T2map[x_idx,:,:], 2)
    # Rotate T2smap 180 degrees around the x-axis
    for x_idx in range(T2smap.shape[0]):
        T2smap[x_idx,:,:] = np.rot90(T2smap[x_idx,:,:], 2)
    # Rotate PDmap 180 degrees around the x-axis
    for x_idx in range(PDmap.shape[0]):
        PDmap[x_idx,:,:] = np.rot90(PDmap[x_idx,:,:], 2) 

    data_dict['T1'] = T1map
    data_dict['T2'] = T2map
    data_dict['T2Star'] = T2smap
    data_dict['Rho'] = PDmap

    # Convert T1, T2, T2s from seconds to milliseconds. This is necessary because the scan function expects the values in milliseconds.
    data_dict['T1'] =   data_dict['T1']*1000
    data_dict['T2'] =   data_dict['T2']*1000
    data_dict['T2Star'] =   data_dict['T2Star']*1000
    data_dict['Rho'] =  data_dict['Rho']*1000
    # Convert the resolution from meters to millimeters. This is necessary because the scan function expects the values in millimeters. 
    data_dict['XDimRes'] =  data_dict['XDimRes']*1000
    data_dict['YDimRes'] =  data_dict['YDimRes']*1000
    data_dict['ZDimRes'] =  data_dict['ZDimRes']*1000

    return data_dict    