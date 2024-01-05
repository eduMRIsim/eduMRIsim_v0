from image_synthesiser import ImageSynthesiser
from signal_calculator import SESignalCalculator, GESignalCalculator

class ScanItem: 
    def __init__(self, name, scan_parameters):
        self._name = name
        self._scan_parameters = {}
        for key, value in scan_parameters.items():
            self._scan_parameters[key] = value 

        self._image_synthesiser = ImageSynthesiser()

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
        
        try: scan_parameters["TE"] = float(scan_parameters["TE"])
        except: 
            valid = False
            messages['TE'] = "TE must be a real number."
        
        try: scan_parameters["TR"] = float(scan_parameters["TR"])
        except: 
            valid = False
            messages['TR'] = "TR must be a real number."
        
        try: scan_parameters["TI"] = float(scan_parameters["TI"])
        except: 
            valid = False
            messages["TI"] = "TI must be a real number."
        
        try: scan_parameters["slice"] = int(scan_parameters["slice"])
        except: 
            valid = False
            messages["slice"] = "Slice must be an integer."
        
        if valid == True:
            for key, value in scan_parameters.items():
                self._scan_parameters[key] = value 

        return valid, messages 

    def run(self, model):
        if self.scan_parameters["scan_technique"] == "SE": 
            self._image_synthesiser.set_signal_calculator(SESignalCalculator())
        elif self.scan_parameters["scan_technique"] == "GE": 
            self._image_synthesiser.set_signal_calculator(GESignalCalculator())
        return self._image_synthesiser.synthesise_image(self.scan_parameters, model)
        