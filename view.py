from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QProgressBar, QPushButton, QMainWindow, QLabel, QLineEdit, QStackedLayout, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self, scanner):
        super().__init__()

        self.setWindowTitle("eduMRIsim_V0_UI")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QHBoxLayout()
        central_widget.setLayout(self.layout)

        self.scanner = scanner
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

        self.examination_info_stacked_layout = ExaminationInfoStackedLayout(self.scanner)
        self.examination_info_stacked_layout.setCurrentIndex(0)
        leftLayout.addLayout(self.examination_info_stacked_layout, stretch=1)

        self.exam_card_info_frame = ExamCardInfoFrame()
        leftLayout.addWidget(self.exam_card_info_frame, stretch=2)

        scan_progress_info_frame = ScanProgressInfoFrame(self.scanner)
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
        return self.examination_info_stacked_layout.getNewExaminationButton()
    
    def getLoadExaminationButton(self):
        return self.examination_info_stacked_layout.getLoadExaminationButton()
    
    def getAddScanItemButton(self):
        return self.exam_card_info_frame.getAddScanItemButton()
    
    def getViewModelButton(self):
        return self.examination_info_stacked_layout.getViewModelButton()

class ModeSwitchButtonsLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.scanningModeButton = QPushButton("Scanning Mode")
        self.viewingModeButton = QPushButton("Viewing Mode")
        self.addWidget(self.scanningModeButton)
        self.addWidget(self.viewingModeButton)

class ExaminationInfoStackedLayout(QStackedLayout):
    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner
        self.pre_examination_info_frame = PreExaminationInfoFrame()
        self.examination_info_frame = ExaminationInfoFrame(self.scanner)
        self.addWidget(self.pre_examination_info_frame)
        self.addWidget(self.examination_info_frame)
    
    def getNewExaminationButton(self):
        return self.pre_examination_info_frame.getNewExaminationButton()
    
    def getLoadExaminationButton(self):
        return self.pre_examination_info_frame.getLoadExaminationButton()
    
    def getViewModelButton(self):
        return self.examination_info_frame.getViewModelButton()
    
    def setTextExaminationInfoFrame(self, exam_name, model_name):
        exam_name_label = self.examination_info_frame.getExaminationNameLabel()
        model_name_label = self.examination_info_frame.getModelNameLabel()
        exam_name_label.setText(exam_name)
        model_name_label.setText(model_name)

class PreExaminationInfoFrame(QFrame):
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
    
class ExaminationInfoFrame(QFrame):
    def __init__(self, scanner):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName("examinationFrame")
        self.setStyleSheet("QFrame#examinationFrame { border: 2px solid black; }")
        self._createExaminationInfo(scanner)
        self._createViewModelButton()

    def _createExaminationInfo(self, scanner):
        examInfoForm = QFormLayout()

        examination = scanner.get_examination()
        self.examination_name_label = QLabel()
        self.model_name_label = QLabel()

        examInfoForm.addRow(QLabel("Exam name:"), self.examination_name_label)
        examInfoForm.addRow(QLabel("Model name:"), self.model_name_label)

        self.layout.addLayout(examInfoForm)        
    
    def _createViewModelButton(self):
        self.viewModelButton = QPushButton("View Model")
        self.viewModelButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        self.layout.addWidget(self.viewModelButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def getExaminationNameLabel(self):
        return self.examination_name_label

    def getModelNameLabel(self):
        return self.model_name_label
    
    def getViewModelButton(self):
        return self.viewModelButton

class ExamCardInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }") 
        self.label = QLabel(self)
        self.label.setText("Exam Cards")
        self.label.setStyleSheet("QLabel { color: black; }")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.addScanItemButton = QPushButton("Add Scan Item")
        self.addScanItemButton.setVisible(False)
        self.layout.addWidget(self.addScanItemButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def getAddScanItemButton(self):
        return self.addScanItemButton


class ScanProgressInfoFrame(QFrame):
    def __init__(self, scanner):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.scanner = scanner
        self._createProgressBar()
        self._createScanButtons()
        self._createScanInfo(scanner)

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

    def _createScanInfo(self,scanner):
        scanInfoForm = QFormLayout()

        scanner_name = QLabel(scanner.get_name())
        scanner_name.setStyleSheet("border: none;")
        scanner_field_strength = QLabel(str(scanner.get_field_strength()))
        scanner_field_strength.setStyleSheet("border: none;")

        # Ensure there's no border around labels "Scanner" and "Field strength (T)"
        label_scanner = QLabel("Scanner name:")
        label_scanner.setStyleSheet("border: none;")
        label_field_strength = QLabel("Field strength (T):")
        label_field_strength.setStyleSheet("border: none;")

        scanInfoForm.addRow(label_scanner, scanner_name)
        scanInfoForm.addRow(label_field_strength, scanner_field_strength)

        self.layout.addLayout(scanInfoForm)

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
    def __init__(self, model_names):
        super().__init__()
        self.model_names = model_names

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
        self.modelComboBox.addItems(self.model_names)

    def _createExamInfoForm(self):
        self.examInfoForm = QFormLayout()
        horizontal_layout = QHBoxLayout()
        self.uploadModelButton = QPushButton("Upload")
        horizontal_layout.addWidget(self.modelComboBox)
        horizontal_layout.addWidget(self.uploadModelButton)
        self.examInfoForm.addRow("Select model:", horizontal_layout)
        self.examNameLineEdit = QLineEdit()
        self.examInfoForm.addRow("Exam name:", self.examNameLineEdit)

    def getOkButton(self):
        return self.okButton
    
    def getCancelButton(self):
        return self.cancelButton


class LoadExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load examination")

class ViewModelDialog(QDialog):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("View Model")
            
        layout = QVBoxLayout()

        self.model_name_label = QLabel(model._model_name)
        self.model_description_label = QLabel(model._description)

        layout.addWidget(self.model_name_label)
        layout.addWidget(self.model_description_label)

        self.setLayout(layout)