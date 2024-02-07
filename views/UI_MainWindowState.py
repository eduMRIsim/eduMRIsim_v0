class UI_MainWindowState():
    def enter_state(self, context) -> None:
        pass

    def enter_exam_state(self, context) -> None:
        pass

    def enter_idle_state(self, context) -> None:
        pass

class ExamState(UI_MainWindowState):
    def enter_state(self, context) -> None:
        context.examinationInfoStackedLayout.setCurrentIndex(1)
        context.scanningModeButton.setEnabled(True)
        context.viewingModeButton.setEnabled(True)
        context.scanlistListWidget.setVisible(True)
        context.addScanItemButton.setVisible(True)

    def enter_idle_state(self, context) -> None:
        context.state = IdleState()
        context.state.enter_state(context)

class IdleState(UI_MainWindowState):
    def enter_state(self, context) -> None:
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

    def enter_exam_state(self, context) -> None:
        context.state = ExamState()
        context.state.enter_state(context)
