class UI_MainWindowState():
    def enter_state(self, context) -> None:
        pass

    def enter_exam_state(self, context) -> None:
        pass

    def enter_idle_state(self, context) -> None:
        pass

    def enter_ready_to_scan_state(self, context) -> None:
        pass

    def enter_being_modified_state(self, context) -> None:
        pass

    def enter_invalid_parameters_state(self, context) -> None:
        pass

    def enter_scan_complete_state(self, context) -> None:
        pass

class ExamState(UI_MainWindowState):
    name = "ExamState"
    def enter_state(self, context) -> None:
        super().enter_state(context)
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

    def enter_idle_state(self, context) -> None:
        context.state = IdleState()
        context.state.enter_state(context)

    def enter_ready_to_scan_state(self, context) -> None:
        context.state = ReadyToScanState()
        context.state.enter_state(context)

class ReadyToScanState(ExamState):
    name = "ReadyToScanState"
    def enter_state(self, context) -> None:
        super().enter_state(context)
        context.startScanButton.setEnabled(True)
        context.stopScanButton.setEnabled(True)
        context.parameterFormLayout.setReadOnly(False)
        context.scanParametersResetButton.setEnabled(True)

    def enter_being_modified_state(self, context) -> None:
        context.state = BeingModifiedState()
        context.state.enter_state(context)

    def enter_invalid_parameters_state(self, context) -> None:
        context.state = InvalidParametersState()
        context.state.enter_state(context)

    def enter_scan_complete_state(self, context) -> None:
        context.state = ScanCompleteState()
        context.state.enter_state(context)

class BeingModifiedState(ExamState):
    name = "BeingModifiedState"
    def enter_state(self, context) -> None:
        super().enter_state(context)
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

    def enter_ready_to_scan_state(self, context) -> None:
        context.state = ReadyToScanState()
        context.state.enter_state(context)

    def enter_invalid_parameters_state(self, context) -> None:
        context.state = InvalidParametersState()
        context.state.enter_state(context)

class InvalidParametersState(ExamState):
    name = "InvalidParametersState"
    def enter_state(self, context) -> None:
        super().enter_state(context)
        context.parameterFormLayout.setReadOnly(False)
        context.scanParametersResetButton.setEnabled(True)

    def enter_being_modified_state(self, context) -> None:
        context.state = BeingModifiedState()
        context.state.enter_state(context)

class ScanCompleteState(ExamState):
    name = "ScanCompleteState"
    def enter_state(self, context) -> None: 
        super().enter_state(context)        

class IdleState(UI_MainWindowState):
    name = "IdleState"
    def enter_state(self, context) -> None:
        super().enter_state(context)
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

    def enter_exam_state(self, context) -> None:
        context.state = ExamState()
        context.state.enter_state(context)
