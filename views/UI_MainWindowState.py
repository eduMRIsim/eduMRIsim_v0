# Will make UI_MainWindowState an abstract class and create subclasses for each state
# This will make the code more readable and maintainable

from abc import ABC, abstractmethod

class UI_MainWindowState(ABC):
    def update_UI(self, context) -> None:
        MRIfortheBrainState().update_UI(context) # all states will call this method first to implement the UI configuration for the MRI for the brain course

class ExamState(UI_MainWindowState):
    name = "ExamState"
    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.scanningModeButton.setEnabled(True)
        context.viewingModeButton.setEnabled(False)
        context.examinationInfoStackedLayout.setCurrentIndex(1)
        context.scanlistListWidget.setVisible(True)
        context.scanlistListWidget.setEnabled(True)
        context.addScanItemButton.setVisible(True)
        context.addScanItemButton.setEnabled(True)
        context.startScanButton.setEnabled(False)
        context.stopScanButton.setEnabled(False)
        context.parameterFormLayout.setReadOnly(True)
        context.scanParametersCancelChangesButton.setEnabled(False) 
        context.scanParametersSaveChangesButton.setEnabled(False)
        context.scanParametersResetButton.setEnabled(False)

class ReadyToScanState(ExamState):
    name = "ReadyToScanState"
    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.startScanButton.setEnabled(True)
        context.stopScanButton.setEnabled(True)
        context.parameterFormLayout.setReadOnly(False)
        context.scanParametersResetButton.setEnabled(True)


class BeingModifiedState(ExamState):
    name = "BeingModifiedState"
    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.scanningModeButton.setEnabled(False)
        context.viewingModeButton.setEnabled(False)
        context.scanlistListWidget.setEnabled(False)
        context.addScanItemButton.setEnabled(False)
        context.startScanButton.setEnabled(False)
        context.stopScanButton.setEnabled(False)
        context.parameterFormLayout.setReadOnly(False)
        context.scanParametersCancelChangesButton.setEnabled(True)
        context.scanParametersResetButton.setEnabled(True) 
        context.scanParametersSaveChangesButton.setEnabled(True)


class InvalidParametersState(ExamState):
    name = "InvalidParametersState"
    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.parameterFormLayout.setReadOnly(False)
        context.scanParametersResetButton.setEnabled(True)


class ScanCompleteState(ExamState):
    name = "ScanCompleteState"
    def update_UI(self, context) -> None: 
        super().update_UI(context)        

class IdleState(UI_MainWindowState):
    name = "IdleState"
    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.scanningModeButton.setEnabled(False)
        context.viewingModeButton.setEnabled(False)
        context.examinationInfoStackedLayout.setCurrentIndex(0)
        context.scanlistListWidget.setVisible(False)
        context.addScanItemButton.setVisible(False)
        context.startScanButton.setEnabled(False)
        context.stopScanButton.setEnabled(False)
        context.parameterFormLayout.setReadOnly(True)
        context.scanParametersCancelChangesButton.setEnabled(False) 
        context.scanParametersSaveChangesButton.setEnabled(False)
        context.scanParametersResetButton.setEnabled(False)
        context.scanProgressBar.setValue(0)

class MRIfortheBrainState(UI_MainWindowState):
    def update_UI(self, context) -> None:
        context.loadExaminationButton.setVisible(False)
        context.stopScanButton.setVisible(False)
        context.scanningModeButton.setVisible(False)
        context.viewingModeButton.setVisible(False)