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

        PD = model.PDmap_ms[:, :] 
        T1 = model.T1map_ms[:, :]
        T2 = model.T2map_ms[:, :]

        with np.errstate(divide='ignore', invalid='ignore'): # supress warnings about division by zero and invalid values since these are handled in the code
            signal_array = np.abs(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1))))   

        signal_array = np.nan_to_num(signal_array, nan=0) # replace all nan values with 0. This is necessary because the signal_array can contain nan values, for example if both TI and T1 are 0. 

        return signal_array

class GESignalCalculator(SignalCalculator):
    def calculate_signal(self, scan_parameters, model):
        TE = scan_parameters['TE']
        TR = scan_parameters['TR']
        FA = np.deg2rad(scan_parameters['FA'])

        PD = model.PDmap_ms[:, :] 
        T1 = model.T1map_ms[:, :]
        T2s = model.T2smap_ms[:, :]


        with np.errstate(divide='ignore', invalid='ignore'): # supress warnings about division by zero and invalid values since these are handled in the code
            E1 = np.exp(np.divide(-TR, T1))
            E2 = np.exp(np.divide(-TE, T2s))

            signal_array = np.abs(np.divide(PD * E2 * np.sin(FA) * (1 - E1), 1 - E1 * np.cos(FA)))

        signal_array = np.nan_to_num(signal_array, nan=0) # replace all nan values with 0. This is necessary because the signal_array can contain nan values, for example if both TI and T1 are 0. 

        return signal_array

        
