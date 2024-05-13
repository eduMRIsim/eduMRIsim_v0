class Model:
    def __init__(self, name, description, T1map, T2map, T2smap, PDmap):
        self._name = name
        self._description = description
        self._T1map = T1map
        self._T2map = T2map
        self._T2smap = T2smap
        self._PDmap = PDmap 

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name 

    @property
    def T1map(self):
        return self._T1map
    
    @property
    def T2map(self):
        return self._T2map
    
    @property
    def T2smap(self):
        return self._T2smap
    
    @property
    def PDmap(self):
        return self._PDmap 