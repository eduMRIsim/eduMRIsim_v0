from scan_item import ScanItem

class Scanlist:
    def __init__(self):
        self._scanlist = [] 

    @property
    def scanlist(self):
        return self._scanlist

    def add_scan_item(self, key, scan_item):
        new_scan_item = ScanItem(key, scan_item)
        self._scanlist.append(new_scan_item)