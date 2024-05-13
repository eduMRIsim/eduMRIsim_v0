from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import   (QComboBox, QFormLayout, QFrame, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListView, QListWidget, QMainWindow, QProgressBar, QPushButton, QSizePolicy,
                             QStackedLayout, QTabWidget, QVBoxLayout, QWidget)
from PyQt5.QtGui import QPainter, QPixmap, QImage, QResizeEvent, QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent
import numpy as np
from views.UI_MainWindowState import IdleState
from contextlib import contextmanager

@contextmanager
def block_signals(widgets):
    """
    Context manager to temporarily block signal emissions for a group of widgets.
    :param widgets: List of widgets for which signal emissions should be blocked.
    """
    try:
        # Temporarily block signal emissions for each widget
        for widget in widgets:
            widget.blockSignals(True)
        # Yield control back to the caller
        yield
    finally:
        # Re-enable signal emissions for each widget, even if an exception occurred
        for widget in widgets:
            widget.blockSignals(False)

class Ui_MainWindow(QMainWindow):
    def __init__(self, scanner):
        super().__init__()

        self.centralWidget = QWidget(self)

        self.layout = QHBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.scanner = scanner
        self._createMainWindow()

        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("eduMRIsim_V0_UI")

        self.state = IdleState()
        self.state.enter_state(self)
    
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
    def stopExaminationButton(self):
        return self._examinationInfoFrame.stopExaminationButton

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
    def testInfoLabel(self):
        return self._scanProgressInfoFrame.testInfoLabel
    
    @property
    def testInfoLabel2(self):
        return self._scanProgressInfoFrame.testInfoLabel2
    
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
    def scanParametersResetButton(self):
        return self._scanParametersWidget.scanParametersResetButton

    @property
    def examCardListView(self):
        return self._examCardTab.examCardListView
    
    @property
    def scannedImageFrame(self):
        return self._scannedImageFrame 
     
    @property 
    def scanPlanningWindow1(self):
        return self.scanPlanningWindow.ImageLabelTuple[0]
    
    @property
    def scanPlanningWindow2(self):  
        return self.scanPlanningWindow.ImageLabelTuple[1]

    @property
    def scanPlanningWindow3(self):
        return self.scanPlanningWindow.ImageLabelTuple[2]   

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
        leftLayout.addLayout(self._examinationInfoStackedLayout, stretch=1)

        self._scanlistInfoFrame = ScanlistInfoFrame()
        leftLayout.addWidget(self._scanlistInfoFrame, stretch=2)

        self._scanProgressInfoFrame = ScanProgressInfoFrame(self.scanner)
        leftLayout.addWidget(self._scanProgressInfoFrame, stretch=1)

        return leftLayout
    
    def _createRightLayout(self) -> QVBoxLayout:

        rightLayout = QVBoxLayout() 

        self.scanPlanningWindow = ScanPlanningWindow()
        rightLayout.addWidget(self.scanPlanningWindow,stretch=1)

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
        self._createButtonLayout()

    def _createExaminationInfo(self):
        examInfoForm = QFormLayout()

        self._examinationNameLabel = QLabel()
        self._modelNameLabel = QLabel()

        examInfoForm.addRow(QLabel("Exam name:"), self._examinationNameLabel)
        examInfoForm.addRow(QLabel("Model name:"), self._modelNameLabel)

        self.layout.addLayout(examInfoForm)        
    
    def _createButtonLayout(self):
        buttonLayout = QHBoxLayout()
        self._viewModelButton = QPushButton("View Model")
        self._viewModelButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        buttonLayout.addWidget(self._viewModelButton)
        self._stopExaminationButton = QPushButton("Stop Examination")
        self._stopExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )
        buttonLayout.addWidget(self._stopExaminationButton)
        self.layout.addLayout(buttonLayout)

    @property
    def examinationNameLabel(self):
        return self._examinationNameLabel

    @property
    def modelNameLabel(self):
        return self._modelNameLabel
    
    @property
    def viewModelButton(self):
        return self._viewModelButton
    
    @property
    def stopExaminationButton(self):
        return self._stopExaminationButton

class ScanlistInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: 2px solid black; }") 
        #self.label.setStyleSheet("QLabel { color: black; }")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._addScanItemButton = QPushButton("Add Scan Item")
        #self._addScanItemButton.setVisible(False)
        self._scanlistListWidget = ScanlistListWidget()
        #self._scanlistListWidget.setVisible(False)
        #self._scanlistListWidget.setStyleSheet("border: none;")
        self.layout.addWidget(self._scanlistListWidget)
        self.layout.addWidget(self._addScanItemButton)

    @property
    def addScanItemButton(self):
        return self._addScanItemButton

    @property
    def scanlistListWidget(self):
        return self._scanlistListWidget

class ScanlistListWidget(QListWidget):
    dropEventSignal = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: none;")
        self.setDragDropMode(self.DragDrop)
        self.setSelectionMode(self.ExtendedSelection)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        e.accept()

    def dragMoveEvent(self, e: QDragMoveEvent) -> None:
        e.accept()

    def dropEvent(self, e: QDropEvent):
        widget = e.source()
        selected_indexes = widget.selectedIndexes()
        self.dropEventSignal.emit(selected_indexes)
        e.accept()        

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
    
    @property
    def testInfoLabel(self):
        return self._testInfoLabel

    @property
    def testInfoLabel2(self):
        return self._testInfoLabel2

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
        #Label for printing info for testing
        self._testInfo = QLabel("Test info:")
        self._testInfo.setStyleSheet("border: none;")
        self._testInfoLabel = QLabel()
        self._testInfoLabel.setStyleSheet("border: none;")
        self._testInfo2 = QLabel("Test info2:")
        self._testInfo2.setStyleSheet("border: none;")
        self._testInfoLabel2 = QLabel()
        self._testInfoLabel2.setStyleSheet("border: none;")

        scanInfoForm.addRow(self._scannerNameLabel, scannerName)
        scanInfoForm.addRow(self._scannerFieldStrengthLabel, scannerFieldStrength)
        scanInfoForm.addRow(self._testInfo, self._testInfoLabel)
        scanInfoForm.addRow(self._testInfo2, self._testInfoLabel2)

        self.layout.addLayout(scanInfoForm)

class ScanPlanningWindow(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        self.ImageLabelTuple = tuple(DropImageLabel() for i in range(3))
        for label in self.ImageLabelTuple:
            layout.addWidget(label, stretch=1)

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
    
    @property
    def scanParametersResetButton(self):
        return self._scanParametersResetButton

    def _createScanParametersTabWidget(self):
        self.scanParametersTabWidget = ScanParametersTabWidget() 
        self.layout.addWidget(self.scanParametersTabWidget)

    def _createButtons(self):
        buttonsLayout = QHBoxLayout()
        self._scanParametersSaveChangesButton = QPushButton("Save Changes")
        self._scanParametersCancelChangesButton = QPushButton("Cancel")
        self._scanParametersResetButton = QPushButton("Reset")
        buttonsLayout.addWidget(self._scanParametersSaveChangesButton)
        buttonsLayout.addWidget(self._scanParametersCancelChangesButton)
        buttonsLayout.addWidget(self._scanParametersResetButton)
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
        self._examCardListView.setDragDropMode(QListView.DragOnly)
        self._examCardListView.setSelectionMode(QListView.ExtendedSelection)
        self._examCardListView.setEditTriggers(QListView.NoEditTriggers) #This is a flag provided by PyQt, which is used to specify that no editing actions should trigger item editing in the list view. It essentially disables editing for the list view, preventing users from directly editing the items displayed in the list.
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
    formActivatedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.scanTechniqueComboBox = QComboBox()
        self.scanTechniqueComboBox.addItems(["GE", "SE"])
        self.TELineEdit = QLineEdit()
        self.TRLineEdit = QLineEdit()
        self.TILineEdit = QLineEdit()
        self.FALineEdit = QLineEdit()
        #self.sliceLineEdit = QLineEdit()


        self.scanTechniqueMessageLabel = QLabel()
        self.scanTechniqueMessageLabel.setStyleSheet("color: red")    
        self.TEMessageLabel = QLabel()
        self.TEMessageLabel.setStyleSheet("color: red")
        self.TRMessageLabel = QLabel()
        self.TRMessageLabel.setStyleSheet("color: red")
        self.TIMessageLabel = QLabel()
        self.TIMessageLabel.setStyleSheet("color: red")
        self.FAMessageLabel = QLabel()
        self.FAMessageLabel.setStyleSheet("color: red")
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

        self.addWidget(QLabel("FA:"), 4, 0, Qt.AlignLeft)
        self.addWidget(self.FALineEdit, 4, 1, Qt.AlignLeft)
        self.addWidget(self.FAMessageLabel, 4, 2, Qt.AlignLeft)

        #self.addWidget(QLabel("slice:"), 4, 0, Qt.AlignLeft)
        #self.addWidget(self.sliceLineEdit, 4, 1, Qt.AlignLeft)
        #self.addWidget(self.sliceMessageLabel, 4, 2, Qt.AlignLeft)

        self.setColumnStretch(0, 1)
        self.setColumnStretch(1, 2)
        self.setColumnStretch(2, 2)

        self.isReadOnly = None

        # Connect signals to the custom signal
        self.TELineEdit.textChanged.connect(lambda: self.formActivatedSignal.emit())
        self.TRLineEdit.textChanged.connect(lambda: self.formActivatedSignal.emit())
        self.TILineEdit.textChanged.connect(lambda: self.formActivatedSignal.emit())
        self.FALineEdit.textChanged.connect(lambda: self.formActivatedSignal.emit())
        self.scanTechniqueComboBox.currentIndexChanged.connect(lambda: self.formActivatedSignal.emit())

    def setReadOnly(self, isReadOnly):
        if self.isReadOnly == isReadOnly:
            return
        else:
            for row in range(self.rowCount()):
                for col in range(self.columnCount()):
                    item = self.itemAtPosition(row, col)
                    if item and item.widget():
                        # Check if the widget is a QLineEdit or QComboBox and set its read-only state
                        if isinstance(item.widget(), (QLineEdit)):
                            item.widget().setReadOnly(isReadOnly)
                        elif isinstance(item.widget(), (QComboBox)):
                            item.widget().setEnabled(not isReadOnly)
            self.isReadOnly = isReadOnly

    def setData(self, data, messages):
        widgets = [self.TELineEdit, self.TRLineEdit, self.TILineEdit, self.FALineEdit, self.scanTechniqueComboBox]

        # Use the block_signals context manager to temporarily block signal emissions
        with block_signals(widgets):
            # Set the data for the widgets without emitting formActivatedSignal
            index = self.scanTechniqueComboBox.findText(str(data.get("scan_technique", "")))
            if index != -1:
                self.scanTechniqueComboBox.setCurrentIndex(index)
            self.TELineEdit.setText(str(data.get("TE", "")))
            self.TRLineEdit.setText(str(data.get("TR", "")))
            self.TILineEdit.setText(str(data.get("TI", "")))
            self.FALineEdit.setText(str(data.get("FA", "")))
            #self.sliceLineEdit.setText(str(data.get("slice", "")))

            self.setMessages(messages)

    def getData(self):
        data = {}

        data["scan_technique"] = self.scanTechniqueComboBox.currentText()
        data["TE"] = self.TELineEdit.text()
        data["TR"] = self.TRLineEdit.text()
        data["TI"] = self.TILineEdit.text()
        data["FA"] = self.FALineEdit.text()
        #data["slice"] = self.sliceLineEdit.text()

        return data

    def setMessages(self, messages):
        self.TEMessageLabel.setText(messages.get("TE", ""))
        self.TRMessageLabel.setText(messages.get("TR", ""))
        self.TIMessageLabel.setText(messages.get("TI", ""))
        self.FAMessageLabel.setText(messages.get("FA", ""))
        #self.sliceMessageLabel.setText(messages.get("slice", ""))

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

        # Check if the array is None
        if self.array is None:
            # Do nothing and return
            return

        # Check if the event occurred over the image
        if self.pixmap_item.isUnderMouse():
            # angleDelta().y() provides the angle through which the vertical mouse wheel was rotated since the last event in eigths of a degree. The value is positive when the wheel is rotated away from the user and negative when the wheel is rotated towards the user. 120 units * 1/8 = 15 degrees for most mouses. 
            delta = event.angleDelta().y() / 120
            current_slice = getattr(self, 'current_slice', 0)
            new_slice = max(0, min(current_slice + delta, self.array.shape[2] - 1))
            self.current_slice = int(new_slice)
            self.displayArray()
        else:
            # Allow the base class to handle the event in other cases
            super().wheelEvent(event)

    #ImageLabel holds a copy of the array of MRI data to be displayed. 
    def setArray(self, array):
        # Set the array and make current_slice the middle slice by default
        self.array = array
        if array is not None:
            self.current_slice = array.shape[2] // 2    
        else:
            self.current_slice = 0
            
    def displayArray(self):
        width, height = 0, 0
        if self.array is not None:
            displayed_slice = getattr(self, 'current_slice', 0)

            # Normalize the slice values for display
            array_norm = (self.array[:,:,displayed_slice] - np.min(self.array)) / (np.max(self.array) - np.min(self.array))
            array_8bit = (array_norm * 255).astype(np.uint8)

            # Convert the array to QImage for display. This is because you cannot directly set a QPixmap from a NumPy array. You need to convert the array to a QImage first.
            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

        else:
            # Set a black image when self.array is None
            black_image = QImage(1, 1, QImage.Format_Grayscale8)
            black_image.fill(Qt.black)
            pixmap = QPixmap.fromImage(black_image)
            self.pixmap_item.setPixmap(pixmap)           

        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

        # Adjust the scene rectangle and center the image.  The arguments (0, 0, width, height) specify the left, top, width, and height of the scene rectangle.
        self.scene.setSceneRect(0, 0, width, height)
        # The centerOn method is used to center the view on a particular point within the scene.
        self.centerOn(width / 2, height / 2)
        
class DropImageLabel(ImageLabel):
    dropEventSignal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        source_widget = event.source()
        # Should only accept drops if source widget is ScanlistListWidget and only one item is selected
        if isinstance(source_widget, ScanlistListWidget) and len(source_widget.selectedIndexes()) == 1:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        source_widget = event.source()
        selected_index = source_widget.selectedIndexes()[0].row()
        print(selected_index)
        self.dropEventSignal.emit(selected_index)
        event.accept()