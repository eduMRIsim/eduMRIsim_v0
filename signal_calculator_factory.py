from signal_calculator import SESignalCalculator, GESignalCalculator

class SignalCalculatorFactory:
    def __init__(self):
        self._cache = {}
        self._calculator_registry = {
            "SE": SESignalCalculator,
            "GE": GESignalCalculator
        }

    @property
    def cache(self):
        return self._cache
    
    @cache.setter
    def cache(self, new_cache):
        self._cache = new_cache

    @property
    def calculator_registry(self):
        return self._calculator_registry
    
    def create_signal_calculator(self, scan_parameters):
        scan_technique = scan_parameters.get("scan_technique")
        if scan_technique in self.cache:
            return self.cache[scan_technique]
        
        calculator_class = self.calculator_registry.get(scan_technique)
        if calculator_class:
            signal_calculator = calculator_class()
            self.cache[scan_technique] = signal_calculator
            return signal_calculator
        else:
            raise ValueError("Invalid scan technique")
        