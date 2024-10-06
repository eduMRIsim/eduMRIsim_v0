from abc import ABC, abstractmethod

import numpy as np

from simulator.model import Model


class MRIDataSynthesiser:
    def __init__(self):
        self._signal_calculator_factory = SignalCalculatorFactory()

    @property
    def signal_calculator_factory(self):
        return self._signal_calculator_factory

    def synthesise_MRI_data(self, scan_parameters: dict, model: Model) -> np.ndarray:
        signal_calculator = self.signal_calculator_factory.create_signal_calculator(
            scan_parameters
        )
        if signal_calculator:
            return signal_calculator.calculate_signal(scan_parameters, model)
        else:
            raise ValueError("Invalid scan technique")


class SignalCalculatorFactory:
    def __init__(self):
        self._cache = {}
        self._calculator_registry = {"SE": SESignalCalculator, "GE": GESignalCalculator}

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
        scan_technique = scan_parameters.get("ScanTechnique")
        if scan_technique in self.cache:
            return self.cache[scan_technique]

        calculator_class = self.calculator_registry.get(scan_technique)
        if calculator_class:
            signal_calculator = calculator_class()
            self.cache[scan_technique] = signal_calculator
            return signal_calculator
        else:
            raise ValueError("Invalid scan technique")


class SignalCalculator(ABC):
    @abstractmethod
    def calculate_signal(self):
        pass


class SESignalCalculator(SignalCalculator):
    def calculate_signal(self, scan_parameters: dict, model: Model) -> np.ndarray:
        TE = scan_parameters["TE_ms"]
        TR = scan_parameters["TR_ms"]
        TI = scan_parameters["TI_ms"]

        PD = model.PDmap[:, :]
        T1 = model.T1map_msec[:, :]
        T2 = model.T2map_msec[:, :]

        with np.errstate(
            divide="ignore", invalid="ignore"
        ):  # supress warnings about division by zero and invalid values since these are handled in the code
            signal_array = np.abs(
                PD
                * np.exp(np.divide(-TE, T2))
                * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1)))
            )

        signal_array = np.nan_to_num(
            signal_array, nan=0
        )  # replace all nan values with 0. This is necessary because the signal_array can contain nan values, for example if both TI and T1 are 0.

        return signal_array


class GESignalCalculator(SignalCalculator):
    def calculate_signal(self, scan_parameters: dict, model: Model) -> np.ndarray:
        TE = scan_parameters["TE_ms"]
        TR = scan_parameters["TR_ms"]
        FA = np.deg2rad(scan_parameters["FA_deg"])

        PD = model.PDmap[:, :]
        T1 = model.T1map_msec[:, :]
        T2s = model.T2smap_msec[:, :]

        with np.errstate(
            divide="ignore", invalid="ignore"
        ):  # supress warnings about division by zero and invalid values since these are handled in the code
            E1 = np.exp(np.divide(-TR, T1))
            E2 = np.exp(np.divide(-TE, T2s))

            signal_array = np.abs(
                np.divide(PD * E2 * np.sin(FA) * (1 - E1), 1 - E1 * np.cos(FA))
            )

        signal_array = np.nan_to_num(
            signal_array, nan=0
        )  # replace all nan values with 0. This is necessary because the signal_array can contain nan values, for example if both TI and T1 are 0.

        return signal_array
