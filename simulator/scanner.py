from simulator.examination import Examination
from simulator.MRI_data_synthesiser import MRIDataSynthesiser

class Scanner:
    """
    Represents an MRI scanner. 
    """
    def __init__(self):

        self._MRI_data_synthesiser = MRIDataSynthesiser()
        self._examination = None 
    
    def scan(self):
        """
        Performs a scan using the scanner's MRIDataSynthesiser.

        :return: Data synthesized from the active scan item and model.
        :rtype: np.array
        """
        acquired_data = self._MRI_data_synthesiser.synthesise_MRI_data(self.active_scan_item.scan_parameters, self.model)     
        self.scanlist.active_scanlist_element.acquired_data = acquired_data
        return acquired_data

    def start_examination(self, exam_name, model):
        self.examination = Examination(exam_name, model)

    def stop_examination(self):
        self.examination = None

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
        
    @property
    def active_scanlist_element(self):
        try:
            return self.examination.scanlist.active_scanlist_element
        except AttributeError:
            return None