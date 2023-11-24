from scanlist import Scanlist

class Examination:
    def __init__(self, exam_name):
        self._exam_name = exam_name 
        self._model = None
        self._scanlist = Scanlist() 

    @property
    def scanlist(self):
        return self._scanlist 

    @property
    def exam_name(self):
        return self._exam_name
    
    @exam_name.setter
    def exam_name(self, name):
        self._exam_name = name

    @property
    def model(self):
        return self._model

    @model.setter    
    def model(self, new_model):
        self._model = new_model