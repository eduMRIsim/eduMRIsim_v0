from enum import Enum, auto

class Scanlist:
    def __init__(self):
        self.scanlist_elements = []
        self.active_idx = 0 

    def add_scanlist_element(self, name, scan_parameters):
        new_scanlist_element = ScanlistElement(name, scan_parameters)
        self.scanlist_elements.append(new_scanlist_element)
    
    @property
    def active_scanlist_element(self):
        return self.scanlist_elements[self.active_idx]
    
    @property
    def active_scan_item(self):
        return self.scanlist_elements[self.active_idx].scan_item

class ScanlistElementStatusEnum(Enum):
    READY_TO_SCAN = auto()
    BEING_MODIFIED = auto()
    INVALID = auto()
    COMPLETE = auto()

class ScanlistElement:
    def __init__(self, name, scan_parameters):
        self.scan_item = ScanItem(name, scan_parameters, self)
        self.acquired_data = None
        self.status = ScanlistElementStatusEnum.READY_TO_SCAN

    @property
    def name(self):
        return self.scan_item.name

class ScanItem: 
    def __init__(self, name, scan_parameters, scanlist_element):
        self.name = name
        self._scan_parameters = scan_parameters
        self._scan_parameters_original = {}
        for key, value in scan_parameters.items():
            self._scan_parameters_original[key] = value
        self.scanlist_element = scanlist_element
        self.messages = {}
        self.valid = True

    @property
    def status(self):
        return self.scanlist_element.status
    
    @status.setter
    def status(self, status):
        print("setting scanlist_element status to", status)
        self.scanlist_element.status = status
        print("scanlist_element status is now", self.scanlist_element.status)

    @property
    def scan_parameters(self):
        return self._scan_parameters
    
    @scan_parameters.setter
    def scan_parameters(self, scan_parameters):
        for key, value in scan_parameters.items():
            try: 
                self._scan_parameters[key] = float(value) 
            except: 
                self._scan_parameters[key] = value

    @property
    def scan_parameters_original(self):
        return self._scan_parameters_original
    
    @scan_parameters_original.setter
    def scan_parameters_original(self, scan_parameters):
        for key, value in scan_parameters.items():
            try: self._scan_parameters_original[key] = float(value)   
            except: self._scan_parameters_original[key] = value       
    
    def cancel_changes(self):
        if self.valid == True:
            self.status = ScanlistElementStatusEnum.READY_TO_SCAN
        else:
            self.status = ScanlistElementStatusEnum.INVALID

    def reset_parameters(self):
        for key, value in self.scan_parameters_original.items():
            print(key, value)        
        self.scan_parameters = self.scan_parameters_original
        self.valid = True
        self.messages = {}
        self.status = ScanlistElementStatusEnum.READY_TO_SCAN

    def validate_scan_parameters(self, scan_parameters):
        self.valid = True
        self.messages = {}
        
        try: scan_parameters["TE"] = float(scan_parameters["TE"])
        except: 
            self.valid = False
            self.messages['TE'] = "TE must be a number."
        
        try: scan_parameters["TR"] = float(scan_parameters["TR"])
        except: 
            self.valid = False
            self.messages['TR'] = "TR must be a number."
        
        try: scan_parameters["TI"] = float(scan_parameters["TI"])
        except: 
            self.valid = False
            self.messages["TI"] = "TI must be a number."

        try: scan_parameters["FA"] = float(scan_parameters["FA"])
        except: 
            self.valid = False
            self.messages["FA"] = "FA must be a number."

        self.scan_parameters = scan_parameters
  

        if self.valid == True:
            self.status = ScanlistElementStatusEnum.READY_TO_SCAN
            
        else:
            self.status = ScanlistElementStatusEnum.INVALID
            


        