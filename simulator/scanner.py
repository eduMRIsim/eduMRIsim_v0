from simulator.examination import Examination
from simulator.MRI_data_synthesiser import MRIDataSynthesiser

class Scanner:
    """
    Represents an MRI scanner. 
    """
    def __init__(self, name, field_strength):
        """
        Initializes a Scanner object.

        :param name: The name of the scanner.
        :type name: str
        :param field_strength: The field strength of the scanner in Tesla.
        :type field_strength: float
        """
        self._name = name
        self._field_strength = field_strength 
        self._MRI_data_synthesiser = MRIDataSynthesiser()
        self._examination = None 
    
    def scan(self):
        """
        Performs a scan using the scanner's MRIDataSynthesiser.

        :return: Data synthesized from the active scan item and model.
        :rtype: np.array
        """
        acquired_data = self.MRI_data_synthesiser.synthesise_MRI_data(self.active_scan_item.scan_parameters, self.model)     
        self.scanlist.active_scanlist_element.acquired_data = acquired_data
        return acquired_data

    def start_examination(self, exam_name, model):
        """_summary_

        :param exam_name: _description_
        :type exam_name: _type_
        :param model: _description_
        :type model: _type_
        """
        self.examination = Examination(exam_name, model)

    @property
    def MRI_data_synthesiser(self):
        return self._MRI_data_synthesiser

    @property
    def examination(self):
        try :
            return self._examination
        except AttributeError:
            return None

    @examination.setter
    def examination(self, new_examination):
        self._examination = new_examination

    @property
    def name(self):
        return self._name 
    
    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def field_strength(self):
        return self._field_strength 
    
    @field_strength.setter
    def field_strength(self, new_field_strength):
        self._field_strength = new_field_strength 

    @property 
    def model(self):
        try:
            return self.examination.model
        except AttributeError:
            return None

    @property
    def scanlist(self):
        try:
            return self.examination.scanlist
        except AttributeError:  
            return None 
        

    @property
    def active_scan_item(self):
        try:
            return self.examination.scanlist.active_scan_item
        except AttributeError:
            return None
        