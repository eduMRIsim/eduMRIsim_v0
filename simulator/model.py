class Model:
    def __init__(self, name, description, T1map_ms, T2map_ms, T2smap_ms, PDmap):
        self.name = name
        self.description = description
        self.T1map_ms = T1map_ms
        self.T2map_ms = T2map_ms
        self.T2smap_ms = T2smap_ms
        self.PDmap = PDmap
