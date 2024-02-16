from simulator.examination import Examination
from simulator.MRI_data_synthesiser import MRIDataSynthesiser

class Scanner:
    def __init__(self, name, field_strength):
        self._name = name
        self._field_strength = field_strength 
        self._MRI_data_synthesiser = MRIDataSynthesiser()
        self._examination = None 
    
    def scan(self):
        return self.MRI_data_synthesiser.synthesise_MRI_data(self.current_scan_item.scan_parameters, self.model)     

    def start_examination(self, exam_name, model):
        self.examination = Examination(exam_name, model)

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
    def scan_items(self):
        try:
            return self.examination.scanlist.scan_items
        except AttributeError:
            return None

    @property
    def current_scan_item(self):
        try:
            return self.examination.scanlist.current_scan_item
        except AttributeError:
            return None
        