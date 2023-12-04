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