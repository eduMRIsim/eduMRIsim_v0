from examination import Examination

class Scanner:
    def __init__(self, name, field_strength):
        self._name = name
        self._field_strength = field_strength 
        self._examination = None 
        self._model = None 
        self._scanlist = None 
        self._current_scan_item = None 
    
    def scan(self):
        pass     

    def start_examination(self, exam_name, model):
        self.examination = Examination(exam_name, model)
        self.model = model 
        self.scanlist = self.examination.scanlist 

    @property 
    def examination(self):
        return self._examination

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
        return self._model
    
    @model.setter
    def model(self, new_model):
        self._model = new_model

    @property
    def scanlist(self):
        return self._scanlist
    
    @scanlist.setter
    def scanlist(self, new_scanlist):
        self._scanlist = new_scanlist

    @property
    def current_scan_item(self):
        return self._current_scan_item
    
    @current_scan_item.setter
    def current_scan_item(self, new_current_scan_item):
        self._current_scan_item = new_current_scan_item 