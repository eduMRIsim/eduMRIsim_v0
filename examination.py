class Examination:
    def __init__(self, exam_name):
        self._exam_name = exam_name 
        self._model = None

    def get_exam_name(self):
        return self._exam_name
    
    def set_model(self, model):
        self._model = model