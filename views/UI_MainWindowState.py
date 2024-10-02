from abc import ABC


class UI_MainWindowState(ABC):
    def update_UI(self, context) -> None:
        MRIfortheBrainState().update_UI(
            context
        )  # all states will call this method first to implement the UI configuration for the MRI for the brain course.
        # This hides buttons whose functionalities have not been implemented yet.


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


class ReadyToScanAgainState(ExamState):
    name = "ReadyToScanState"

    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.examinationInfoStackedLayout.setCurrentIndex(1)
        context.scanlistListWidget.setVisible(True)
        context.scanlistListWidget.setEnabled(True)
        context.addScanItemButton.setVisible(True)
        context.addScanItemButton.setEnabled(True)
        context.startScanButton.setEnabled(True)
        context.stopScanButton.setEnabled(True)
        context.parameterFormLayout.setReadOnly(False)
        context.scanParametersResetButton.setEnabled(True)
        context.scanProgressBar.setValue(0)
        context.scannedImageFrame.setAcquiredSeries(None)
        context.scanPlanningWindow1.setAcquiredSeries(None)
        context.scanPlanningWindow2.setAcquiredSeries(None)
        context.scanPlanningWindow3.setAcquiredSeries(None)


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
        context.scannedImageWidget.acquiredImageExportButton.setEnabled(True)


class ViewState(UI_MainWindowState):
    name = "ViewState"

    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.examinationInfoStackedLayout.setCurrentIndex(0)
        context.scanningModeButton.setVisible(False)
        context.viewingModeButton.setVisible(False)
        context.scanningModeButton.setEnabled(False)
        context.viewingModeButton.setEnabled(False)
        context.scanlistListWidget.setVisible(True)
        context.scanlistListWidget.setEnabled(True)
        context.addScanItemButton.setVisible(False)
        context.addScanItemButton.setEnabled(False)
        context.startScanButton.setEnabled(False)
        context.stopScanButton.setEnabled(False)


class IdleState(UI_MainWindowState):
    name = "IdleState"

    def update_UI(self, context) -> None:
        super().update_UI(context)
        context.scanningModeButton.setEnabled(False)
        context.viewingModeButton.setEnabled(False)
        context.examinationInfoStackedLayout.setCurrentIndex(0)
        context.editingStackedLayout.setCurrentIndex(0)
        context.scanlistListWidget.setVisible(False)
        context.scanlistListWidget.clear()
        context.addScanItemButton.setVisible(False)
        context.startScanButton.setEnabled(False)
        context.stopScanButton.setEnabled(False)
        context.parameterFormLayout.setReadOnly(True)
        context.parameterFormLayout.clearForm()
        context.scanParametersCancelChangesButton.setEnabled(False)
        context.scanParametersSaveChangesButton.setEnabled(False)
        context.scanParametersResetButton.setEnabled(False)
        context.scanProgressBar.setValue(0)
        context.scannedImageFrame.setAcquiredSeries(None)
        context.scanPlanningWindow1.setAcquiredSeries(None)
        context.scanPlanningWindow2.setAcquiredSeries(None)
        context.scanPlanningWindow3.setAcquiredSeries(None)
        context.scanPlanningWindow1ExportButton.setEnabled(False)
        context.scanPlanningWindow2ExportButton.setEnabled(False)
        context.scanPlanningWindow3ExportButton.setEnabled(False)


class MRIfortheBrainState(UI_MainWindowState):
    def update_UI(self, context) -> None:
        context.loadExaminationButton.setVisible(True)
        context.stopScanButton.setVisible(False)
        context.scanningModeButton.setVisible(False)
        context.viewingModeButton.setVisible(False)
        context.scanPlanningWindow1ExportButton.setEnabled(False)
        context.scanPlanningWindow2ExportButton.setEnabled(False)
        context.scanPlanningWindow3ExportButton.setEnabled(False)
        context.scannedImageWidget.acquiredImageExportButton.setEnabled(False)

        if (
            context.scanPlanningWindow1.acquired_series is not None
            and context.scanPlanningWindow1.acquired_series.list_acquired_images
            is not None
        ):
            context.scanPlanningWindow1ExportButton.setEnabled(True)
        if (
            context.scanPlanningWindow2.acquired_series is not None
            and context.scanPlanningWindow2.acquired_series.list_acquired_images
            is not None
        ):
            context.scanPlanningWindow2ExportButton.setEnabled(True)
        if (
            context.scanPlanningWindow3.acquired_series is not None
            and context.scanPlanningWindow3.acquired_series.list_acquired_images
            is not None
        ):
            context.scanPlanningWindow3ExportButton.setEnabled(True)
