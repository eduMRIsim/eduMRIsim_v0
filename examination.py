from scanlist import Scanlist

class Examination:
    def __init__(self, name, model):
        self._name = name 
        self._model = model 
        self._scanlist = Scanlist()

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