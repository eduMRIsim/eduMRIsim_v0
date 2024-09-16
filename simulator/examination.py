from simulator.scanlist import Scanlist

class Examination:
    def __init__(self, name, model):
        self.name = name 
        self.model = model 
        self.scanlist = Scanlist()
