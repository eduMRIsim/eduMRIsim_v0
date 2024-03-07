from enum import Enum, auto

class ScanItemStatusEnum(Enum):
    READY_TO_SCAN = auto()
    BEING_MODIFIED = auto()
    INVALID = auto()
    COMPLETE = auto()

# class ScanItemDataTuple:
#     def __init__(self, name, scan_parameters):
#         self.scan_item = ScanItem(name, scan_parameters)
#         self._acquired_data = None

#     @property
#     def status(self):
#         return self.scan_item.status
    
#     @status.setter
#     def status(self, status):
#         self.scan_item.status = status

#     @property
#     def scan_parameters(self):
#         return self.scan_item.scan_parameters

#     @property
#     def acquired_data(self):
#         return self.acquired_data
    
#     @acquired_data.setter
#     def acquired_data(self, acquired_data):
#         self._acquired_data = acquired_data

#     @property
#     def name(self):
#         return self.scan_item.name

class ScanItem: 
    def __init__(self, name, scan_parameters):
        self._name = name
        self._scan_parameters = scan_parameters
        self._status = ScanItemStatusEnum.READY_TO_SCAN
        self.valid = True
        self._scan_parameters_original = {}
        for key, value in scan_parameters.items():
            self._scan_parameters_original[key] = value
        self.messages = {}
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name 

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, status):
        self._status = status

    @property
    def scan_parameters(self):
        return self._scan_parameters
    
    @scan_parameters.setter
    def scan_parameters(self, scan_parameters):
        for key, value in scan_parameters.items():
            self._scan_parameters[key] = value 
    
    @property
    def scan_parameters_original(self):
        return self._scan_parameters_original
    
    def validate_scan_parameters(self, scan_parameters):
        self.valid = True
        self.messages = {}
        
        try: scan_parameters["TE"] = float(scan_parameters["TE"])
        except: 
            self.valid = False
            self.messages['TE'] = "TE must be a real number."
        
        try: scan_parameters["TR"] = float(scan_parameters["TR"])
        except: 
            self.valid = False
            self.messages['TR'] = "TR must be a real number."
        
        try: scan_parameters["TI"] = float(scan_parameters["TI"])
        except: 
            self.valid = False
            self.messages["TI"] = "TI must be a real number."
        
        #try: scan_parameters["slice"] = int(scan_parameters["slice"])
        #except: 
            #valid = False
            #messages["slice"] = "Slice must be an integer."

        self.scan_parameters = scan_parameters
        
        if self.valid == True:
            self.status = ScanItemStatusEnum.READY_TO_SCAN
            
        else:
            self.status = ScanItemStatusEnum.INVALID
            


        