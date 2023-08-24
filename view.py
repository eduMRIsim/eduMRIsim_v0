from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QComboBox, QDialog, QFormLayout, QFrame, QProgressBar, QPushButton, QMainWindow, QLabel, QLineEdit, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("eduMRIsim_V0_UI")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QHBoxLayout()
        central_widget.setLayout(self.layout)

        self._createMainWindow()
    
    def _createMainWindow(self):
        leftLayout = self._createLeftLayout()
        self.layout.addLayout(leftLayout, stretch = 1)

        rightLayout = self._createRightLayout()
        self.layout.addLayout(rightLayout, stretch = 3)
 
    def _createLeftLayout(self) -> QHBoxLayout:

        leftLayout = QVBoxLayout()

        mode_switch_buttons_layout = ModeSwitchButtonsLayout()
        leftLayout.addLayout(mode_switch_buttons_layout, stretch=1)

        self.examination_info_frame = ExaminationInfoFrame()
        leftLayout.addWidget(self.examination_info_frame, stretch=1)

        exam_card_info_frame = ExamCardInfoFrame()
        leftLayout.addWidget(exam_card_info_frame, stretch=2)

        scan_progress_info_frame = ScanProgressInfoFrame()
        leftLayout.addWidget(scan_progress_info_frame, stretch=1)

        self.state_label = StateLabel()
        leftLayout.addWidget(self.state_label)

        return leftLayout
    
    def _createRightLayout(self) -> QVBoxLayout:

        rightLayout = QVBoxLayout() 

        scan_planning_frame = ScanPlanningFrame()
        rightLayout.addWidget(scan_planning_frame,stretch=1)

        bottomLayout = QHBoxLayout()

        scan_parameters_tab_widget = ScanParametersTabWidget()
        bottomLayout.addWidget(scan_parameters_tab_widget, stretch=1)
        scanned_image_frame = ScannedImageFrame()
        bottomLayout.addWidget(scanned_image_frame, stretch=1)

        rightLayout.addLayout(bottomLayout,stretch=1)

        return rightLayout

    def getNewExaminationButton(self):
        return self.examination_info_frame.getNewExaminationButton()
    
    def getLoadExaminationButton(self):
        return self.examination_info_frame.getLoadExaminationButton()

class ModeSwitchButtonsLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.scanningModeButton = QPushButton("Scanning Mode")
        self.viewingModeButton = QPushButton("Viewing Mode")
        self.addWidget(self.scanningModeButton)
        self.addWidget(self.viewingModeButton)

class ExaminationInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self._createNewExaminationButton()
        self._createLoadExaminationButton()

    def _createNewExaminationButton(self):
        self.newExaminationButton = QPushButton("New Examination")
        self.newExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        self.layout.addWidget(self.newExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def _createLoadExaminationButton(self):
        self.loadExaminationButton = QPushButton("Load Examination")
        self.loadExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        self.layout.addWidget(self.loadExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def getNewExaminationButton(self):
        return self.newExaminationButton
    
    def getLoadExaminationButton(self):
        return self.loadExaminationButton

class ExamCardInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }") 
        self.label = QLabel(self)
        self.label.setText("Exam Cards")
        self.label.setStyleSheet("QLabel { color: black; }")

class ScanProgressInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._createProgressBar()
        self._createScanButtons()

    def _createProgressBar(self):
        progressBarLayout = QHBoxLayout()   

        progressBarLabel = QLabel("Scan Progress:")
        progressBarLabel.setStyleSheet("QLabel { border: none; }")  # Remove border
        progressBarLayout.addWidget(progressBarLabel)

        progressBar = QProgressBar()
        progressBar.setValue(50)
        progressBarLayout.addWidget(progressBar)

        self.layout.addLayout(progressBarLayout)
        
    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()
        
        scanStartButton = QPushButton("Start Scan")
        #scanStartButton.setStyleSheet("QPushButton { background-color: green; color: #ffffff; }")
        scanButtonsLayout.addWidget(scanStartButton)
        
        scanStopButton = QPushButton("Stop Scan")
        #scanStopButton.setStyleSheet("QPushButton { background-color: red; color: #ffffff; }") 
        scanButtonsLayout.addWidget(scanStopButton)

        self.layout.addLayout(scanButtonsLayout)

class StateLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Current state: ")

class ScanPlanningFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black; border: 1px solid black;")

class ScanParametersTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.addTab(GeometryTab(), "Geometry")
        self.addTab(ContrastTab(), "Contrast")

class GeometryTab(QWidget):
    def __init__(self):
        super().__init__()
        label = QLabel(self)
        label.setText("Geometry parameters")

class ContrastTab(QWidget):
    def __init__(self):
        super().__init__()
        label = QLabel(self)
        label.setText("Contrast parameters")

class ScannedImageFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black; border: 1px solid black;")

class NewExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New examination")
        self.layout = QVBoxLayout()

        self._createModelComboBox()
        self._createExamInfoForm()
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        self.layout.addLayout(self.examInfoForm)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.okButton)
        horizontal_layout.addWidget(self.cancelButton)
        self.layout.addLayout(horizontal_layout)

        self.setLayout(self.layout)
    
    def _createModelComboBox(self):
        self.modelComboBox = QComboBox()
        self.modelComboBox.addItems(["Brain model", "Knee model", "Cylindrical phantom"])

    def _createExamInfoForm(self):
        self.examInfoForm = QFormLayout()
        horizontal_layout = QHBoxLayout()
        self.uploadModelButton = QPushButton("Upload")
        horizontal_layout.addWidget(self.modelComboBox)
        horizontal_layout.addWidget(self.uploadModelButton)
        self.examInfoForm.addRow("Select model:", horizontal_layout)
        self.examInfoForm.addRow("Exam name:", QLineEdit())


class LoadExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load examination")