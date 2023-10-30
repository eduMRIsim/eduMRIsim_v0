class Scanner:
    def __init__(self,scanner_name,field_strength):
        self._scanner_name = scanner_name
        self._field_strength = field_strength 
        self._examination = None 
    
    def scan(self):
        pass 

    def set_examination(self, examination):
        self._examination = examination

    def get_examination(self):
        return self._examination

    def get_name(self):
        return self._scanner_name 

    def get_field_strength(self):
        return self._field_strength 