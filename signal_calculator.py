from abc import ABC, abstractmethod
import numpy as np

class SignalCalculator(ABC):
    @abstractmethod
    def calculate_signal(self):
        pass 

class SESignalCalculator(SignalCalculator): 
    def calculate_signal(self, scan_parameters, model):
        TE = scan_parameters['TE']
        TR = scan_parameters['TR']
        TI = scan_parameters['TI']
        #slice_idx = scan_parameters['slice'] - 1
        
        # PD = model.PDmap[:, :, slice_idx]
        # T1 = model.T1map[:, :, slice_idx]
        # T2 = model.T2map[:, :, slice_idx]

        PD = model.PDmap[:, :]
        T1 = model.T1map[:, :]
        T2 = model.T2map[:, :]

        signal_array = np.abs(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1))))        
        return signal_array

class GESignalCalculator(SignalCalculator):
    def calculate_signal(self):
        pass 
