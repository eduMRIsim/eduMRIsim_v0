from simulator.signal_calculator_factory import SignalCalculatorFactory

class MRIDataSynthesiser:
    def __init__(self):
        self._signal_calculator_factory = SignalCalculatorFactory()

    @property
    def signal_calculator_factory(self):
        return self._signal_calculator_factory

    def synthesise_MRI_data(self, scan_parameters, model):
        signal_calculator = self.signal_calculator_factory.create_signal_calculator(scan_parameters)
        if signal_calculator:
            return signal_calculator.calculate_signal(scan_parameters, model)
        else:
            raise ValueError("Invalid scan technique")
