class ScanParameters:
    def __init__(self, scan_parameters):
        self._TE = scan_parameters["TE"]
        self._TR = scan_parameters["TR"]
        self._TI = scan_parameters["TI"]
        self._slice = scan_parameters["slice"]