from scan_item import ScanItem

class Examination:
    def __init__(self, name, model):
        self._name = name 
        self._model = model 
        self._scanlist = []

    def add_scan_item(self, name, scan_parameters):
        new_scan_item = ScanItem(name, scan_parameters)
        self._scanlist.append(new_scan_item)

    @property
    def scanlist(self):
        return self._scanlist 

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def model(self):
        return self._model

    @model.setter    
    def model(self, new_model):
        self._model = new_model