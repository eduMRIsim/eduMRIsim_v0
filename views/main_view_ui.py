from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QProgressBar, QPushButton, QMainWindow, QLabel, QLineEdit, QSlider, QStackedLayout, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class Ui_MainWindow:
    def __init__(self, scanner, MainWindow):
        super().__init__()

        #self.setWindowTitle("eduMRIsim_V0_UI")

        self.centralWidget = QWidget(MainWindow)
        #self.setCentralWidget(self.centralWidget)

        self.layout = QHBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.scanner = scanner
        self._createMainWindow()

        MainWindow.setCentralWidget(self.centralWidget)
        MainWindow.setWindowTitle("eduMRIsim_V0_UI")

        self._scanningModeButton = self._modeSwitchButtonsLayout.scanningModeButton
        self._viewingModeButton = self._modeSwitchButtonsLayout.viewingModeButton
        self._newExaminationButton = self._preExaminationInfoFrame.newExaminationButton
        self._loadExaminationButton = self._preExaminationInfoFrame.loadExaminationButton
        self._examinationNameLabel = self._examinationInfoFrame.examinationNameLabel
        self._modelNameLabel = self._examinationInfoFrame.modelNameLabel
        self._viewModelButton = self._examinationInfoFrame.viewModelButton
        self._addScanItemButton = self._examCardInfoFrame.addScanItemButton
        self._scanProgressBar = self._scanProgressInfoFrame.scanProgressBar
        self._startScanButton = self._scanProgressInfoFrame.startScanButton
        self._stopScanButton = self._scanProgressInfoFrame.stopScanButton
        self._scannerNameLabel = self._scanProgressInfoFrame.scannerNameLabel
        self._scannerFieldStrenghtLabel = self._scanProgressInfoFrame.scannerFieldStrengthLabel

    
    @property
    def scanningModeButton(self):
        return self._scanningModeButton
    
    @property
    def viewingModeButton(self):
        return self._viewingModeButton 
    
    @property
    def examinationInfoStackedLayout(self):
        return self._examinationInfoStackedLayout
    
    @property
    def newExaminationButton(self):
        return self._newExaminationButton
    
    @property
    def loadExaminationButton(self):
        return self._loadExaminationButton
    
    @property
    def examinationNameLabel(self):
        return self._examinationNameLabel
    
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

        scan_parameters_tab_widget = ScanParametersTabWidget()
        bottomLayout.addWidget(scan_parameters_tab_widget, stretch=1)
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
            
        self.layout = QVBoxLayout()

        self.model = model
        self.slice = 15
        self.map = self.model._T1map[:,:,:]
        self.image_array = self.model._T1map[:,:,self.slice]
 
        self.image_label = QLabel()

        self.setPixmap(self.image_array)
        self.layout.addWidget(self.image_label)

        self.createButtons()
        self.createSlider() 

        self.setLayout(self.layout)

    def createButtons(self):
        buttonsLayout = QHBoxLayout()
        T1Button = QPushButton("T1")
        T2Button = QPushButton("T2")
        PDButton = QPushButton("PD")
        T1Button.clicked.connect(self.T1ButtonPressed)
        T2Button.clicked.connect(self.T2ButtonPressed)
        PDButton.clicked.connect(self.PDButtonPressed)
        buttonsLayout.addWidget(T1Button)
        buttonsLayout.addWidget(T2Button)
        buttonsLayout.addWidget(PDButton)
        self.layout.addLayout(buttonsLayout)

    def createSlider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(self.map.shape[2]-1)
        slider.setValue(self.slice)
        slider.sliderMoved.connect(self.handleSliderMoved)
        self.layout.addWidget(slider)

    def handleSliderMoved(self,position):
        self.slice = self.sender().value()
        self.image_array = self.map[:,:,self.slice]
        self.setPixmap(self.image_array)


    def T1ButtonPressed(self):
        self.map = self.model._T1map[:,:,:]
        self.image_array = self.map[:,:,self.slice]
        self.setPixmap(self.image_array)

    def T2ButtonPressed(self):
        self.map = self.model._T2map[:,:,:]
        self.image_array = self.map[:,:,self.slice]
        self.setPixmap(self.image_array)

    def PDButtonPressed(self):
        self.map = self.model._PDmap[:,:,:]
        self.image_array = self.map[:,:,self.slice]
        self.setPixmap(self.image_array)

    def setPixmap(self, array):
        array_norm = (array - np.min(array)) / (np.max(array) - np.min(array))  # Normalize to [0, 1] range
        array_8bit = (array_norm * 255).astype(np.uint8)  # Scale to 8bit range       

        # The np.ascontiguousarray function is used to create a new NumPy array that is guaranteed to have a contiguous memory layout. In other words, it ensures that the array elements are stored in adjacent memory locations without any gaps or strides.
        # QImage expects the image data to be stored in a contiguous block of memory.
        image = np.ascontiguousarray(np.array(array_8bit))   

         # Create QImage
        height, width = image.shape
        qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)           
    
        self.image_label.setPixmap(QPixmap.fromImage(qimage))

