from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import   (QComboBox, QFormLayout, QFrame, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListView, QListWidget, QProgressBar, QPushButton, QSizePolicy,
                             QStackedLayout, QTabWidget, QVBoxLayout, QWidget)
from PyQt5.QtGui import QPainter, QPixmap, QImage, QResizeEvent, QColor
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
    def scannerNameLabel(self):
        return self._scanProgressInfoFrame.scannerNameLabel

    @property
    def scannerFieldStrengthLabel(self):
        return self._scanProgressInfoFrame.scannerFieldStrengthLabel  
    
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
    def scanParametersCancelChangesButton(self):
        return self._scanParametersWidget.scanParametersCancelChangesButton

    @property
    def examCardListView(self):
        return self._examCardTab.examCardListView
    
    @property
    def scannedImageFrame(self):
        return self._scannedImageFrame 
     
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

        self._scanlistInfoFrame = ScanlistInfoFrame()
        leftLayout.addWidget(self._scanlistInfoFrame, stretch=2)

        self._scanProgressInfoFrame = ScanProgressInfoFrame(self.scanner)
        leftLayout.addWidget(self._scanProgressInfoFrame, stretch=1)

        return leftLayout
    
    def _createRightLayout(self) -> QVBoxLayout:

        rightLayout = QVBoxLayout() 

        scan_planning_frame = ScanPlanningFrame()
        rightLayout.addWidget(scan_planning_frame,stretch=1)

        bottomLayout = QHBoxLayout()

        self._examCardTab = ExamCardTab()
        self._scanParametersWidget = ScanParametersWidget()
        self._examCardTabWidget = ExamCardTabWidget(self._examCardTab)
        self._editingStackedLayout = EditingStackedLayout(self._scanParametersWidget, self._examCardTabWidget)
        self._editingStackedLayout.setCurrentIndex(0)
        bottomLayout.addLayout(self._editingStackedLayout, stretch=1)
        self._scannedImageFrame = ImageLabel()
        bottomLayout.addWidget(self._scannedImageFrame, stretch=1)

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

class ScanlistInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }") 
        #self.label.setStyleSheet("QLabel { color: black; }")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._addScanItemButton = QPushButton("Add Scan Item")
        self._addScanItemButton.setVisible(False)
        self._scanlistListWidget = QListWidget()
        self._scanlistListWidget.setVisible(False)
        self._scanlistListWidget.setStyleSheet("border: none;")
        self.layout.addWidget(self._scanlistListWidget)
        self.layout.addWidget(self._addScanItemButton)

    @property
    def addScanItemButton(self):
        return self._addScanItemButton

    @property
    def scanlistListWidget(self):
        return self._scanlistListWidget

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
        scannerName = QLabel(scanner.name)
        scannerName.setStyleSheet("border: none;")
        scannerFieldStrength = QLabel(str(scanner.field_strength))
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
    def __init__(self, scanParametersWidget, examCardTabWidget):
        super().__init__()
        self.addWidget(scanParametersWidget)
        self.addWidget(examCardTabWidget)
        
class ScanParametersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._createScanParametersTabWidget()
        self._createButtons()


    @property
    def parameterFormLayout(self):
        return self.scanParametersTabWidget.parameterFormLayout
    
    @property 
    def scanParametersSaveChangesButton(self):
        return self._scanParametersSaveChangesButton
    
    @property 
    def scanParametersCancelChangesButton(self):
        return self._scanParametersCancelChangesButton

    def _createScanParametersTabWidget(self):
        self.scanParametersTabWidget = ScanParametersTabWidget() 
        self.layout.addWidget(self.scanParametersTabWidget)

    def _createButtons(self):
        buttonsLayout = QHBoxLayout()
        self._scanParametersSaveChangesButton = QPushButton("Save Changes")
        self._scanParametersCancelChangesButton = QPushButton("Cancel")
        buttonsLayout.addWidget(self._scanParametersSaveChangesButton)
        buttonsLayout.addWidget(self._scanParametersCancelChangesButton)
        self.layout.addLayout(buttonsLayout)        
    

class ExamCardTabWidget(QTabWidget):
    def __init__(self, examCardTab):
        super().__init__()
        self.addTab(examCardTab, "Exam cards")

class ExamCardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._examCardListView = QListView()
        self._examCardListView.setEditTriggers(QListView.NoEditTriggers)
        self.layout.addWidget(self._examCardListView)
    
    @property
    def examCardListView(self):
        return self._examCardListView

class ScanParametersTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.parameterTab = ParameterTab()
        self.addTab(self.parameterTab, "Scan Parameters")
        
    @property
    def parameterFormLayout(self):
        return self.parameterTab.parameterFormLayout


class ParameterTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        self._parameterFormLayout = ParameterFormLayout()
        self.layout.addLayout(self.parameterFormLayout)

    @property
    def parameterFormLayout(self):
        return self._parameterFormLayout    
    


class ParameterFormLayout(QGridLayout):
    def __init__(self):
        super().__init__()

        self.scanTechniqueComboBox = QComboBox()
        self.scanTechniqueComboBox.addItems(["GE", "SE"])
        self.TELineEdit = QLineEdit()
        self.TRLineEdit = QLineEdit()
        self.TILineEdit = QLineEdit()
        #self.sliceLineEdit = QLineEdit()


        self.scanTechniqueMessageLabel = QLabel()
        self.scanTechniqueMessageLabel.setStyleSheet("color: red")    
        self.TEMessageLabel = QLabel()
        self.TEMessageLabel.setStyleSheet("color: red")
        self.TRMessageLabel = QLabel()
        self.TRMessageLabel.setStyleSheet("color: red")
        self.TIMessageLabel = QLabel()
        self.TIMessageLabel.setStyleSheet("color: red")
        #self.sliceMessageLabel = QLabel()
        #self.sliceMessageLabel.setStyleSheet("color: red")

        self.setHorizontalSpacing(0)

        self.addWidget(QLabel("Scan Technique:"), 0, 0, Qt.AlignLeft)
        self.addWidget(self.scanTechniqueComboBox, 0, 1, Qt.AlignLeft)
        self.addWidget(self.scanTechniqueComboBox, 0, 2, Qt.AlignLeft)

        self.addWidget(QLabel("TE:"), 1, 0, Qt.AlignLeft)
        self.addWidget(self.TELineEdit, 1, 1, Qt.AlignLeft)
        self.addWidget(self.TEMessageLabel, 1, 2, Qt.AlignLeft)

        self.addWidget(QLabel("TR:"), 2, 0, Qt.AlignLeft)
        self.addWidget(self.TRLineEdit, 2, 1, Qt.AlignLeft)
        self.addWidget(self.TRMessageLabel, 2, 2, Qt.AlignLeft)

        self.addWidget(QLabel("TI:"), 3, 0, Qt.AlignLeft)
        self.addWidget(self.TILineEdit, 3, 1, Qt.AlignLeft)
        self.addWidget(self.TIMessageLabel, 3, 2, Qt.AlignLeft)

        #self.addWidget(QLabel("slice:"), 4, 0, Qt.AlignLeft)
        #self.addWidget(self.sliceLineEdit, 4, 1, Qt.AlignLeft)
        #self.addWidget(self.sliceMessageLabel, 4, 2, Qt.AlignLeft)

        self.setColumnStretch(0, 1)
        self.setColumnStretch(1, 2)
        self.setColumnStretch(2, 2)

    def setData(self, data):
        index = self.scanTechniqueComboBox.findText(str(data.get("scan_technique", "")))
        if index != -1:
            self.scanTechniqueComboBox.setCurrentIndex(index)
        self.TELineEdit.setText(str(data.get("TE", "")))
        self.TRLineEdit.setText(str(data.get("TR", "")))
        self.TILineEdit.setText(str(data.get("TI", "")))
        #self.sliceLineEdit.setText(str(data.get("slice", "")))

    def getData(self):
        data = {}

        data["scan_technique"] = self.scanTechniqueComboBox.currentText()
        data["TE"] = self.TELineEdit.text()
        data["TR"] = self.TRLineEdit.text()
        data["TI"] = self.TILineEdit.text()
        #data["slice"] = self.sliceLineEdit.text()

        return data

    def setMessages(self, messages):
        self.TEMessageLabel.setText(messages.get("TE", ""))
        self.TRMessageLabel.setText(messages.get("TR", ""))
        self.TIMessageLabel.setText(messages.get("TI", ""))
        #self.sliceMessageLabel.setText(messages.get("slice", ""))

class ScannedImageFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black; border: 1px solid black;")

""" class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def displayArray(self, array):
        array_norm = (array - np.min(array)) / (np.max(array) - np.min(array))  # Normalize to [0, 1] range
        array_8bit = (array_norm * 255).astype(np.uint8)  # Scale to 8bit range       

        # The np.ascontiguousarray function is used to create a new NumPy array that is guaranteed to have a contiguous memory layout. In other words, it ensures that the array elements are stored in adjacent memory locations without any gaps or strides.
        # QImage expects the image data to be stored in a contiguous block of memory.
        image = np.ascontiguousarray(np.array(array_8bit))   

         # Create QImage
        height, width = image.shape
        qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)           
    
        self.setPixmap(QPixmap.fromImage(qimage))
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setAspectRatioMode(Qt.KeepAspectRatio) """

#QGraphicsView is a Qt class designed to display the contents of a QGraphicsScene. It provides a 2D view of the scene and allows users to interact with the items within the scene. 
class ImageLabel(QGraphicsView):
    def __init__(self):
        super().__init__()

        # QGraphicsScene is essentially a container that holds and manages the graphical items you want to display in your QGraphicsView. QGraphicsScene is a container and manager while QGraphicsView is responsible for actually displaying those items visually. 
        self.scene = QGraphicsScene(self)

        # Creates a pixmap graphics item that will be added to the scene
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # Sets the created scene as the scene for the graphics view
        self.setScene(self.scene)

        # Sets the render hint to enable antialiasing, which makes the image look smoother. Aliasings occur when a high-resolution image is displayed or rendered at a lower resolution, leading to the loss of information and the appearance of stair-stepped edges. Antialiasing techniques smooth out these jagged edges by introducing intermediate colors or shades along the edges of objects.
        self.setRenderHint(QPainter.Antialiasing, True)

        # Set the background color to black
        self.setBackgroundBrush(QColor(0, 0, 0))  # RGB values for black

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Initialize array attribute to None
        self.array = None
        self.current_slice = None


    # This method is called whenever the graphics view is resized. It ensures that the image is always scaled to fit the view.
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    # overriden method from QGraphicsView. QGraphicsView has inherited QWidget's wheelEvent method. QGraphicsView is a child of QWidget. 
    def wheelEvent(self, event):
        # Check if the event occurred over the image
        if self.pixmap_item.isUnderMouse():
            delta = event.angleDelta().y() / 120
            current_slice = getattr(self, 'current_slice', 0)
            new_slice = max(0, min(current_slice + delta, self.array.shape[2] - 1))
            self.current_slice = int(new_slice)
            self.displayArray()
        else:
            # Allow the base class to handle the event in other cases
            super().wheelEvent(event)

    def setArray(self, array):
        # Set the array and display the middle slice by default
        self.array = array
        self.current_slice = array.shape[2] // 2
        self.displayArray()    

    def displayArray(self):
        if self.array is not None:
            displayed_slice = getattr(self, 'current_slice', 0)

            array_norm = (self.array[:,:,displayed_slice] - np.min(self.array)) / (np.max(self.array) - np.min(self.array))
            array_8bit = (array_norm * 255).astype(np.uint8)

            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)

            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

            # Adjust the scene rectangle and center the image
            self.scene.setSceneRect(0, 0, width, height)
            self.centerOn(width / 2, height / 2)
        
        else:
            pass 