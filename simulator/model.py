class Model:
    '''Anatomical model made up of 3D maps which define the tissue properties T1, T2, T2s and PD for each voxel of the model. The dimensions of the model are defined by the XDim, YDim and ZDim parameters. The resolution of the model is defined by the XDimRes, YDimRes and ZDimRes parameters.'''
    def __init__(self, name: str, data_dict: dict):
        self.name = name
        self.T1map_msec = data_dict['T1']
        self.T2map_msec = data_dict['T2']
        self.T2smap_msec = data_dict['T2Star']
        self.PDmap = data_dict['Rho']
        self.XDim = int(data_dict['XDim'])
        self.YDim = int(data_dict['YDim'])
        self.ZDim = int(data_dict['ZDim'])
        self.XDimRes_mm = float(data_dict['XDimRes'])
        self.YDimRes_mm = float(data_dict['YDimRes'])
        self.ZDimRes_mm = float(data_dict['ZDimRes'])