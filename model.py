class Model:
    def __init__(self, model_name, description, T1map, T2map, PDmap):
        self._model_name = model_name
        self._description = description
        self._T1map = T1map
        self._T2map = T2map
        self._PDmap = PDmap 

    def get_model_name(self):
        return self._model_name