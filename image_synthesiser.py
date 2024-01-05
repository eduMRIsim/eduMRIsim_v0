class ImageSynthesiser:
    def __init__(self):
        self._signal_calculator = None
    
    def set_signal_calculator(self, signal_calculator):
        self._signal_calculator = signal_calculator

    def synthesise_image(self, scan_parameters, model):
        return self._signal_calculator.calculate_signal(scan_parameters, model)