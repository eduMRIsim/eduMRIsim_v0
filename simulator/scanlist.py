from simulator.scan_item import ScanItem

class Scanlist:
    def __init__(self):
        self._scan_items = []
        self._current_scan_item_index = 0 

    def add_scan_item(self, name, scan_parameters):
        new_scan_item = ScanItem(name, scan_parameters)
        self._scan_items.append(new_scan_item)

    @property 
    def scan_items(self):
        return self._scan_items
    
    @property
    def current_scan_item(self):
        return self._scan_items[self._current_scan_item_index]
    
    @property
    def current_scan_item_index(self):
        return self._current_scan_item_index
    
    @current_scan_item_index.setter
    def current_scan_item_index(self, new_index):
        self._current_scan_item_index = new_index