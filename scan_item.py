class ScanItem: 
    def __init__(self, name, scan_parameters):
        self._name = name
        self._scan_parameters = {}
        for key, value in scan_parameters.items():
            self._scan_parameters[key] = value 

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name 

    @property
    def scan_parameters(self):
        return self._scan_parameters
    
    def validate_scan_parameters(self, scan_parameters):
        valid = True 
        messages = {}
        
        try: TE = float(scan_parameters["TE"])
        except: 
            valid = False
            messages['TE'] = "TE must be a real number."
        
        try: TR = float(scan_parameters["TR"])
        except: 
            valid = False
            messages['TR'] = "TR must be a real number."
        
        try: TI = float(scan_parameters["TI"])
        except: 
            valid = False
            messages["TI"] = "TI must be a real number."
        
        try: slice = int(scan_parameters["slice"])
        except: 
            valid = False
            messages["slice"] = "Slice must be an integer."
        
        if valid == True:
            for key, value in scan_parameters.items():
                self._scan_parameters[key] = value 

        return valid, messages 
