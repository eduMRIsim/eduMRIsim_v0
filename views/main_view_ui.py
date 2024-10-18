from PyQt6.QtCore import QByteArray
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsView,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
)

from controllers.settings_mgr import SettingsManager
from utils.logger import log

from views.items.acquired_series_viewer_2d import (
    AcquiredSeriesViewer2D,
    DropAcquiredSeriesViewer2D,
)
from views.UI_MainWindowState import (
    ExamState,
)
from views.UI_MainWindowState import (
    ReadyToScanState,
    BeingModifiedState,
    BeingScannedState,
    ScanCompleteState,
    IdleState,
)
from views.ui.exam_card_ui import ExamCardTabWidget, ExamCardTab
from views.ui.examination_info_ui import (
    ExaminationInfoStackedLayout,
    PreExaminationInfoFrame,
)
from views.ui.scan_parameters_ui import ScanParametersWidget
from views.ui.scan_progress_ui import ScanProgressInfoFrame
from views.ui.scanlist_ui import ScanlistInfoFrame
from views.styled_widgets import (
    PrimaryActionButton,
    TertiaryActionButton,
    InfoFrame,
)
from views.ui.viewing_view_ui import gridViewingWindowLayout

"""Note about naming: PyQt uses camelCase for method names and variable names. This unfortunately conflicts with the 
naming convention used in Python. Most of the PyQt related code in eduRMIsim uses the PyQt naming convention. 
However, I've noticed that I haven't been fully consistent with this so I realise some of the naming might be 
confusing. I might change the names in the future. For the SEP project feel free to use whichever convention you find 
most convenient when adding new PyQt related code."""


class Ui_MainWindow(QMainWindow):
    def __init__(self, scanner):
        super().__init__()

        self.centralWidget = QWidget(self)

        self.layout = QHBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("eduMRIsim")

        self.scanner = scanner

        # stacked layout for the right side
        self._stackedLayout = QStackedLayout()
        self.layout.addLayout(self._stackedLayout)

        self._createMainWindow()
        self._state = IdleState()
        self.update_UI()

    def update_UI(self):
        self.state.update_UI(self)

    @property
    def stackedLayout(self):
        return self._stackedLayout

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self.update_UI()

    @property
    def scanningModeButton(self):
        return self._modeSwitchButtonsLayout.scanningModeButton

    @property
    def viewingModeButton(self):
        self._modeSwitchButtonsLayout.viewingModeButton
        return self._modeSwitchButtonsLayout.viewingModeButton

    @property
    def examinationInfoStackedLayout(self):
        return self._examinationInfoStackedLayout

    @property
    def newExaminationButton(self):
        return self._preExaminationInfoFrame.newExaminationButton

    @property
    def loadExaminationButton(self):
        return self._preExaminationInfoFrame.loadExaminationButton

    @property
    def examinationNameLabel(self):
        return self._examinationInfoFrame.section1_text

    @property
    def modelNameLabel(self):
        return self._examinationInfoFrame.section2_text

    @property
    def viewModelButton(self):
        return self._examinationInfoFrame.section2_view_button

    @property
    def stopExaminationButton(self):
        return self._examinationInfoFrame.section1_stop_button

    @property
    def addScanItemButton(self):
        return self._scanlistInfoFrame.addScanItemButton

    @property
    def scanlistListWidget(self):
        return self._scanlistInfoFrame.scanlistListWidget

    @property
    def scanProgressBar(self):
        return self._scanProgressInfoFrame.scanProgressBar

    @property
    def startScanButton(self):
        return self._scanProgressInfoFrame.startScanButton

    @property
    def stopScanButton(self):
        return self._scanProgressInfoFrame.stopScanButton

    @property
    def editingStackedLayout(self):
        return self._editingStackedLayout

    @property
    def parameterFormLayout(self):
        return self._scanParametersWidget.parameterFormLayout

    @property
    def scanParametersSaveChangesButton(self):
        return self._scanParametersWidget.scanParametersSaveChangesButton

    @property
    def scanParametersExportButton(self):
        return self._scanParametersWidget.scanParametersExportButton

    @property
    def scanParametersCancelChangesButton(self):
        return self._scanParametersWidget.scanParametersCancelChangesButton

    @property
    def scanParametersResetButton(self):
        return self._scanParametersWidget.scanParametersResetButton

    @property
    def examCardListView(self):
        return self._examCardTab.examCardListView

    @property
    def scannedImageFrame(self):
        return self._scannedImageFrame

    @property
    def scannedImageWidget(self):
        return self._scannedImageWidget

    @property
    def scanPlanningWindow1(self):
        return self.scanPlanningWindow.ImageLabelTuple[0]

    @property
    def scanPlanningWindow2(self):
        return self.scanPlanningWindow.ImageLabelTuple[1]

    @property
    def scanPlanningWindow3(self):
        return self.scanPlanningWindow.ImageLabelTuple[2]

    @property
    def scanPlanningWindow1ExportButton(self):
        return self.scanPlanningWindow.viewingPortExportButtonTuple[0]

    @property
    def scanPlanningWindow2ExportButton(self):
        return self.scanPlanningWindow.viewingPortExportButtonTuple[1]

    @property
    def scanPlanningWindow3ExportButton(self):
        return self.scanPlanningWindow.viewingPortExportButtonTuple[2]

    @property
    def gridViewingWindowLayout(self):
        return self.gridViewingWindowLayout

    @property
    def GridCell(self):
        return self.GridCell

    def _createMainWindow(self):
        leftLayout = self._createLeftLayout()
        self.layout.addLayout(leftLayout, stretch=1)

        # Create a stacked layout for the right section
        self._stackedLayout = QStackedLayout()

        # the scanning layout
        rightWidget = QWidget()
        rightLayout = self._createRightLayout()
        rightWidget.setLayout(rightLayout)

        # the view layout
        viewWidget = QWidget()
        rightViewLayout = self._createRightViewLayout()
        viewWidget.setLayout(rightViewLayout)

        # stacked layout with right side of view/scanning
        self.stackedLayout.addWidget(rightWidget)
        self.stackedLayout.addWidget(viewWidget)
        rightLayoutContainer = QVBoxLayout()
        rightLayoutContainer.addLayout(self.stackedLayout)
        self.layout.addLayout(rightLayoutContainer, stretch=3)

    def _createLeftLayout(self) -> QHBoxLayout:
        leftLayout = QVBoxLayout()

        self._modeSwitchButtonsLayout = ModeSwitchButtonsLayout()

        self._preExaminationInfoFrame = PreExaminationInfoFrame()
        self._examinationInfoFrame = InfoFrame("Examination", "Model")
        self._examinationInfoStackedLayout = ExaminationInfoStackedLayout(
            self._preExaminationInfoFrame, self._examinationInfoFrame
        )
        leftLayout.addLayout(self._examinationInfoStackedLayout, stretch=1)

        self._scanlistInfoFrame = ScanlistInfoFrame()
        leftLayout.addWidget(self._scanlistInfoFrame, stretch=2)

        self._scanProgressInfoFrame = ScanProgressInfoFrame(self.scanner)
        leftLayout.addWidget(self._scanProgressInfoFrame, stretch=1)

        return leftLayout

    def _createRightLayout(self) -> QVBoxLayout:
        rightLayout = QVBoxLayout()

        self.scanPlanningWindow = ScanPlanningWindow(self)
        rightLayout.addWidget(self.scanPlanningWindow, stretch=1)

        bottomLayout = QHBoxLayout()

        self._examCardTab = ExamCardTab()
        self._scanParametersWidget = ScanParametersWidget()
        self._examCardTabWidget = ExamCardTabWidget(self._examCardTab)
        self._editingStackedLayout = EditingStackedLayout(
            self._scanParametersWidget, self._examCardTabWidget
        )
        self._editingStackedLayout.setCurrentIndex(0)
        bottomLayout.addLayout(self._editingStackedLayout, stretch=1)

        self._scannedImageFrame = AcquiredSeriesViewer2D()
        self._scannedImageFrame.zooming_enabled = True
        # TODO change back to true
        self._scannedImageWidget = ScannedImageWidget(self._scannedImageFrame)
        bottomLayout.addWidget(self._scannedImageWidget, stretch=1)

        rightLayout.addLayout(bottomLayout, stretch=1)

        return rightLayout

    def _createRightViewLayout(self) -> QVBoxLayout:

        rightlayout = QVBoxLayout()

        self.gridViewingWindow = gridViewingWindowLayout()
        rightlayout.addWidget(self.gridViewingWindow)

        return rightlayout

    def save_widget_state(self):
        settings = SettingsManager.get_instance().settings
        settings.beginGroup("WidgetState")

        # Scan parameters
        settings.setValue(
            "_parameterFormLayout_params", self.parameterFormLayout.save_state()
        )

        # UI labels
        settings.setValue("examinationNameLabel", self.examinationNameLabel.text())
        settings.setValue("modelNameLabel", self.modelNameLabel.text())
        settings.setValue("scanProgressBar", self.scanProgressBar.value())

        # AcquiredSeries widgets
        settings.setValue("acquiredSeries1", self.scanPlanningWindow1.acquired_series)
        settings.setValue("acquiredSeries2", self.scanPlanningWindow2.acquired_series)
        settings.setValue("acquiredSeries3", self.scanPlanningWindow3.acquired_series)

        if self.scanPlanningWindow1.acquired_series is not None:
            settings.setValue(
                "acquiredSeriesIDX1", self.scanPlanningWindow1.displayed_image_index
            )
        if self.scanPlanningWindow2.acquired_series is not None:
            settings.setValue(
                "acquiredSeriesIDX2", self.scanPlanningWindow2.displayed_image_index
            )
        if self.scanPlanningWindow3.acquired_series is not None:
            settings.setValue(
                "acquiredSeriesIDX3", self.scanPlanningWindow3.displayed_image_index
            )

        settings.endGroup()

    def restore_widget_states(self):
        settings = SettingsManager.get_instance().settings

        settings.beginGroup("WidgetState")

        # Scan parameters
        self.parameterFormLayout.set_parameters(
            settings.value("_parameterFormLayout_params", type=dict)
        )

        # UI labels
        self.examinationNameLabel.setText(
            settings.value("examinationNameLabel", "", type=str)
        )
        self.modelNameLabel.setText(settings.value("modelNameLabel", "", type=str))
        self.scanProgressBar.setValue(
            int(settings.value("scanProgressBar", 0, type=int))
        )

        # AcquiredSeries widgets
        self.scanPlanningWindow1.setAcquiredSeries(
            acquired_series=settings.value("acquiredSeries1")
        )
        self.scanPlanningWindow2.setAcquiredSeries(
            acquired_series=settings.value("acquiredSeries2")
        )
        self.scanPlanningWindow3.setAcquiredSeries(
            acquired_series=settings.value("acquiredSeries3")
        )
        self.scanPlanningWindow1.displayed_image_index = settings.value(
            "acquiredSeriesIDX1", type=int
        )
        self.scanPlanningWindow2.displayed_image_index = settings.value(
            "acquiredSeriesIDX2", type=int
        )
        self.scanPlanningWindow3.displayed_image_index = settings.value(
            "acquiredSeriesIDX3", type=int
        )

        settings.endGroup()

    # Save the state of the main window
    def save_settings(self):
        settings = SettingsManager.get_instance().settings

        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("currentState", self.state.name)
        settings.setValue("scannerState", self.scanner.save_state())
        self.save_widget_state()

    # This function executes automatically right before the main window is closed
    def closeEvent(self, a0):
        self.save_settings()
        log.info("Settings saved")
        super().closeEvent(a0)

    def restore_settings(self):
        settings = SettingsManager.get_instance().settings

        self.restoreGeometry(settings.value("geometry", type=QByteArray))
        self.restoreState(settings.value("windowState", type=QByteArray))
        state_name = settings.value("currentState", defaultValue="IdleState", type=str)
        state_class = globals().get(state_name)

        if state_class:
            self.state = state_class()
        elif state_name == "ScanCompleteState":
            self.state = ScanCompleteState()
        elif state_name == "BeingModifiedState":
            self.state = BeingModifiedState()
        elif state_name == "BeingScannedState":
            self.state = BeingScannedState()
        elif state_name == "ReadyToScanState":
            self.state = ReadyToScanState()
        elif state_name == "ExamState":
            self.state = ExamState()
        else:
            log.warning(f"State '{state_name}' not found. Defaulting to IdleState.")
            self.state = IdleState()

        self.restore_widget_states()


class ModeSwitchButtonsLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self._scanningModeButton = TertiaryActionButton("Scanning Mode")
        self._viewingModeButton = TertiaryActionButton("Viewing Mode")
        self.addWidget(self._scanningModeButton)
        self.addWidget(self._viewingModeButton)

    @property
    def scanningModeButton(self):
        return self._scanningModeButton

    @property
    def viewingModeButton(self):
        return self._viewingModeButton


class ScanPlanningWindow(QFrame):
    def __init__(self, ui: Ui_MainWindow):
        super().__init__()
        layout = QGridLayout()
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(7)
        self.setLayout(layout)
        self.ui = ui
        self.ImageLabelTuple = tuple(DropAcquiredSeriesViewer2D(ui) for i in range(3))
        for i, label in enumerate(self.ImageLabelTuple):
            layout.addWidget(label, 0, i)
        self.viewingPortExportButtonTuple = tuple(
            PrimaryActionButton(f"Export this viewing port to file") for i in range(3)
        )
        for i, button in enumerate(self.viewingPortExportButtonTuple):
            layout.addWidget(button, 1, i)


class EditingStackedLayout(QStackedLayout):
    def __init__(self, scanParametersWidget, examCardTabWidget):
        super().__init__()
        self.addWidget(scanParametersWidget)
        self.addWidget(examCardTabWidget)


class ScannedImageWidget(QWidget):
    def __init__(self, scannedImageFrame: QGraphicsView):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.addWidget(scannedImageFrame)
        self._acquiredImageExportButton: QPushButton = PrimaryActionButton(
            "Export acquired image to file"
        )
        self._layout.addWidget(self.acquiredImageExportButton)

    @property
    def acquiredImageExportButton(self):
        return self._acquiredImageExportButton
