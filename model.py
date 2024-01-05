class Model:
    def __init__(self, model_name, description, T1map, T2map, PDmap):
        self._model_name = model_name
        self._description = description
        self._T1map = T1map
        self._T2map = T2map
        self._PDmap = PDmap 

    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, name):
        self._model_name = name 

    @property
    def T1map(self):
        return self._T1map
    
    @property
    def T2map(self):
        return self._T2map
    
    @property
    def PDmap(self):
        return self._PDmap 