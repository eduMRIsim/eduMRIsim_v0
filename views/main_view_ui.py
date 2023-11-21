from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import  QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QListView, QProgressBar, QPushButton, QMainWindow, QLabel, QLineEdit, QSlider, QStackedLayout, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class Ui_MainWindow:
    def __init__(self, scanner, MainWindow):
        super().__init__()

        self.centralWidget = QWidget(MainWindow)

        self.layout = QHBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.scanner = scanner
        self._createMainWindow()

        MainWindow.setCentralWidget(self.centralWidget)
        MainWindow.setWindowTitle("eduMRIsim_V0_UI")
    
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
        return self._examinationInfoFrame.examinationNameLabel
    
    @property
    def modelNameLabel(self):
        return self._examinationInfoFrame.modelNameLabel

    @property
    def viewModelButton(self):
        return self._examinationInfoFrame.viewModelButton

    @property
    def addScanItemButton(self):
        return self._examCardInfoFrame.addScanItemButton

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
    def scannerNameLabel(self):
        return self._scanProgressInfoFrame.scannerNameLabel

    @property
    def scannerFieldStrengthLabel(self):
        return self._scanProgressInfoFrame.scannerFieldStrengthLabel  
    
    @property
    def editingStackedLayout(self):
        return self._editingStackedLayout 
    
    @property
    def examCardListModel(self):
        return self._examCardTab.examCardListModel
    
    @property
    def examCardListView(self):
        return self._examCardTab.examCardListView
     
    def _createMainWindow(self):
        leftLayout = self._createLeftLayout()
        self.layout.addLayout(leftLayout, stretch = 1)

        rightLayout = self._createRightLayout()
        self.layout.addLayout(rightLayout, stretch = 3)
 
    def _createLeftLayout(self) -> QHBoxLayout:

        leftLayout = QVBoxLayout()

        self._modeSwitchButtonsLayout = ModeSwitchButtonsLayout()
        leftLayout.addLayout(self._modeSwitchButtonsLayout, stretch=1)

        self._preExaminationInfoFrame = PreExaminationInfoFrame()
        self._examinationInfoFrame = ExaminationInfoFrame()
        self._examinationInfoStackedLayout = ExaminationInfoStackedLayout(self._preExaminationInfoFrame, self._examinationInfoFrame)
        self._examinationInfoStackedLayout.setCurrentIndex(0)
        leftLayout.addLayout(self._examinationInfoStackedLayout, stretch=1)

        self._examCardInfoFrame = ExamCardInfoFrame()
        leftLayout.addWidget(self._examCardInfoFrame, stretch=2)

        self._scanProgressInfoFrame = ScanProgressInfoFrame(self.scanner)
        leftLayout.addWidget(self._scanProgressInfoFrame, stretch=1)

        return leftLayout
    
    def _createRightLayout(self) -> QVBoxLayout:

        rightLayout = QVBoxLayout() 

        scan_planning_frame = ScanPlanningFrame()
        rightLayout.addWidget(scan_planning_frame,stretch=1)

        bottomLayout = QHBoxLayout()

        self._examCardTab = ExamCardTab()
        self._scanParametersTabWidget = ScanParametersTabWidget()
        self._examCardTabWidget = ExamCardTabWidget(self._examCardTab)
        self._editingStackedLayout = EditingStackedLayout(self._scanParametersTabWidget, self._examCardTabWidget)
        self._editingStackedLayout.setCurrentIndex(0)
        bottomLayout.addLayout(self._editingStackedLayout, stretch=1)
        scanned_image_frame = ScannedImageFrame()
        bottomLayout.addWidget(scanned_image_frame, stretch=1)

        rightLayout.addLayout(bottomLayout,stretch=1)

        return rightLayout

    
class ModeSwitchButtonsLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self._scanningModeButton = QPushButton("Scanning Mode")
        self._viewingModeButton = QPushButton("Viewing Mode")
        self.addWidget(self._scanningModeButton)
        self.addWidget(self._viewingModeButton)
    
    @property
    def scanningModeButton(self):
        return self._scanningModeButton
    
    @property 
    def viewingModeButton(self):
        return self._viewingModeButton

class ExaminationInfoStackedLayout(QStackedLayout):
    def __init__(self, preExaminationInfoFrame, examinationInfoFrame):
        super().__init__()
        self._preExaminationInfoFrame = preExaminationInfoFrame
        self.examination_info_frame = examinationInfoFrame
        self.addWidget(self._preExaminationInfoFrame)
        self.addWidget(self.examination_info_frame)

class PreExaminationInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self._createNewExaminationButton()
        self._createLoadExaminationButton()

    def _createNewExaminationButton(self):
        self._newExaminationButton = QPushButton("New Examination")
        self._newExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        self.layout.addWidget(self._newExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def _createLoadExaminationButton(self):
        self._loadExaminationButton = QPushButton("Load Examination")
        self._loadExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        self.layout.addWidget(self._loadExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def newExaminationButton(self):
        return self._newExaminationButton
    
    @property
    def loadExaminationButton(self):
        return self._loadExaminationButton
    
class ExaminationInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName("examinationFrame")
        self.setStyleSheet("QFrame#examinationFrame { border: 2px solid black; }")
        self._createExaminationInfo()
        self._createViewModelButton()

    def _createExaminationInfo(self):
        examInfoForm = QFormLayout()

        self._examinationNameLabel = QLabel()
        self._modelNameLabel = QLabel()

        examInfoForm.addRow(QLabel("Exam name:"), self._examinationNameLabel)
        examInfoForm.addRow(QLabel("Model name:"), self._modelNameLabel)

        self.layout.addLayout(examInfoForm)        
    
    def _createViewModelButton(self):
        self._viewModelButton = QPushButton("View Model")
        self._viewModelButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        self.layout.addWidget(self._viewModelButton, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def examinationNameLabel(self):
        return self._examinationNameLabel

    @property
    def modelNameLabel(self):
        return self._modelNameLabel
    
    @property
    def viewModelButton(self):
        return self._viewModelButton

class ExamCardInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }") 
        self.label = QLabel(self)
        self.label.setText("Exam Cards")
        self.label.setStyleSheet("QLabel { color: black; }")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._addScanItemButton = QPushButton("Add Scan Item")
        self._addScanItemButton.setVisible(False)
        self.layout.addWidget(self._addScanItemButton, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def addScanItemButton(self):
        return self._addScanItemButton

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

    @property
    def scanProgressBar(self):
        return self._scanProgressBar
    
    @property
    def startScanButton(self):
        return self._startScanButton
    
    @property
    def stopScanButton(self):
        return self._stopScanButton
    
    @property
    def scannerNameLabel(self):
        return self._scannerNameLabel
    
    @property
    def scannerFieldStrengthLabel(self):
        return self._scannerFieldStrengthLabel

    def _createProgressBar(self):
        scanProgressBarLayout = QHBoxLayout()   

        scanProgressBarLabel = QLabel("Scan Progress:")
        scanProgressBarLabel.setStyleSheet("QLabel { border: none; }")  # Remove border
        scanProgressBarLayout.addWidget(scanProgressBarLabel)

        self._scanProgressBar = QProgressBar()
        self._scanProgressBar.setValue(50)
        scanProgressBarLayout.addWidget(self._scanProgressBar)

        self.layout.addLayout(scanProgressBarLayout)
        
    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()
        
        self._startScanButton = QPushButton("Start Scan")
        #self._startScanButton.setStyleSheet("QPushButton { background-color: green; color: #ffffff; }")
        scanButtonsLayout.addWidget(self._startScanButton)
        
        self._stopScanButton = QPushButton("Stop Scan")
        #self._stopScanButton.setStyleSheet("QPushButton { background-color: red; color: #ffffff; }") 
        scanButtonsLayout.addWidget(self._stopScanButton)

        self.layout.addLayout(scanButtonsLayout)

    def _createScanInfo(self,scanner):
        scanInfoForm = QFormLayout()

        scannerName = QLabel(scanner.get_name())
        scannerName.setStyleSheet("border: none;")
        scannerFieldStrength = QLabel(str(scanner.get_field_strength()))
        scannerFieldStrength.setStyleSheet("border: none;")

        # Ensure there's no border around labels "Scanner" and "Field strength (T)"
        self._scannerNameLabel = QLabel("Scanner name:")
        self._scannerNameLabel.setStyleSheet("border: none;")
        self._scannerFieldStrengthLabel = QLabel("Field strength (T):")
        self._scannerFieldStrengthLabel.setStyleSheet("border: none;")

        scanInfoForm.addRow(self._scannerNameLabel, scannerName)
        scanInfoForm.addRow(self._scannerFieldStrengthLabel, scannerFieldStrength)

        self.layout.addLayout(scanInfoForm)

class ScanPlanningFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black; border: 1px solid black;")

class EditingStackedLayout(QStackedLayout):
    def __init__(self, scanParametersTabWidget, examCardTabWidget):
        super().__init__()
        self.addWidget(scanParametersTabWidget)
        self.addWidget(examCardTabWidget)
        
class ExamCardTabWidget(QTabWidget):
    def __init__(self, examCardTab):
        super().__init__()
        self.addTab(examCardTab, "Exam cards")

class ExamCardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._examCardListModel = QStringListModel()
        self._examCardListView = QListView()
        self.layout.addWidget(self._examCardListView)

    @property
    def examCardListModel(self):
        return self._examCardListModel
    
    @property
    def examCardListView(self):
        return self._examCardListView

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
