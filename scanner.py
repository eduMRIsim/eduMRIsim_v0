class Scanner:
    def __init__(self,scanner_name,field_strength):
        self._scanner_name = scanner_name
        self._field_strength = field_strength 
        self._examination = None 
    
    def scan(self):
        pass 

    @property 
    def examination(self):
        return self._examination

    @examination.setter
    def examination(self, new_examination):
        self._examination = new_examination

    @property
    def scanner_name(self):
        return self._scanner_name 
    
    @scanner_name.setter
    def scanner_name(self, new_scanner_name):
        self._scanner_name = new_scanner_name

    @property
    def field_strength(self):
        return self._field_strength 
    
    @field_strength.setter
    def field_strength(self, new_field_strength):
        self._field_strength = new_field_strength 