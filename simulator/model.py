class Model:
    def __init__(self, name, description, T1map_ms, T2map_ms, T2smap_ms, PDmap_ms):
        self._name = name
        self._description = description
        self._T1map_ms = T1map_ms
        self._T2map_ms = T2map_ms
        self._T2smap_ms = T2smap_ms
        self._PDmap_ms = PDmap_ms 

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name 

    @property
    def T1map_ms(self):
        return self._T1map_ms
    
    @property
    def T2map_ms(self):
        return self._T2map_ms
    
    @property
    def T2smap_ms(self):
        return self._T2smap_ms
    
    @property
    def PDmap_ms(self):
        return self._PDmap_ms 