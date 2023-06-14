# this module provides the exit() function which we need to cleanly terminate the app
import sys 
from PyQt5.QtCore import QStateMachine, QState, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QProgressBar, QStackedLayout,
    QTabWidget, QVBoxLayout, QWidget
)

# this class inherits from QMainWindow. This class will provide the app's GUI 
class eduMRIsimMainWindow(QMainWindow):
    
    scanningMode_signal = pyqtSignal()
    viewingMode_signal = pyqtSignal()
    newExam_signal = pyqtSignal()
    loadExam_signal = pyqtSignal()
    
    def __init__(self):
        # This call allows you to properly initialize instances of this class. The parent argument is set to None because this will be the main window.
        super().__init__(parent=None)
        self.setWindowTitle("eduMRIsim")
        
        # Initialize the state machine
        self.state_machine = QStateMachine()
        
        # Set up the UI
        self._setupUI()
        
        # Set up the states and transitions
        self._setupStates()
        self._setupTransitions()
        
        # Start State Mahince
        self.state_machine.start()
    
      
    def _setupUI(self):    
        # This will give the app's general layout
        self.generalLayout = QHBoxLayout()
        
        # create a QWidget object and set it as the window's central widget. This object will be the parent of all the required GUI components in the app. 
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        
        self._createMainWindowLeft()
        self._createMainWindowRight()
      
    def _createMainWindowLeft(self):
        self.leftLayout = QVBoxLayout()
        
        self._createModeSwitchButtons()
        self._createPatientInfo()
        self._createExamCardInfo()
        self._createScanProgressInfo()
        
        self.generalLayout.addLayout(self.leftLayout, stretch=1)
        
    def _createMainWindowRight(self): 
        
        self.rightStackedLayout = QStackedLayout()
        
        #create scanning page
        self._createScanningPage()
        # create viewing page
        self._createViewingPage()
   
        self.generalLayout.addLayout(self.rightStackedLayout, stretch = 3)
        
    def _createScanningPage(self):    
        scanningPage = QWidget()
        self.rightScanningLayout = QVBoxLayout()
        
        self._createScanPlanningWindow()
        
        self.layoutTabsAndImage = QHBoxLayout()
        
        self._createParameterTabs()
        self._createScannedImage()
        
        self.rightScanningLayout.addLayout(self.layoutTabsAndImage,stretch = 1)
        
        scanningPage.setLayout(self.rightScanningLayout)
        self.rightStackedLayout.addWidget(scanningPage)
        
    def _createViewingPage(self):
        viewingPage = QWidget()
        
        self.rightViewingLayout = QGridLayout()
        
        self._createViewingFrames()
        
        viewingPage.setLayout(self.rightViewingLayout)
        self.rightStackedLayout.addWidget(viewingPage)
    
    def _createViewingFrames(self):
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for position in positions:
            viewingFrame = QFrame()
            viewingFrame.setStyleSheet("background-color: black; border: 1px solid black;")
            #The *position notation unpacks the position tuple and passes the individual elements as arguments to the addWidget method, specifying the row and column positions.
            self.rightViewingLayout.addWidget(viewingFrame, *position)
        
    def _createModeSwitchButtons(self):
        modeSwitchButtonsLayout = QHBoxLayout()
        
        scanningModeButton = QPushButton("Scanning Mode")
        viewingModeButton = QPushButton("Viewing Mode")
        
        scanningModeButton.clicked.connect(lambda: self.scanningMode_signal.emit())
        viewingModeButton.clicked.connect(lambda: self.viewingMode_signal.emit())
        
        modeSwitchButtonsLayout.addWidget(scanningModeButton)
        modeSwitchButtonsLayout.addWidget(viewingModeButton)
        
        self.leftLayout.addLayout(modeSwitchButtonsLayout, stretch = 1)
    
        
    def _createPatientInfo(self):
        framePatientInfo = QFrame()
        framePatientInfo.setStyleSheet("QFrame { border: 2px solid black; }")
        
        framePatientInfoLayout = QHBoxLayout()
        framePatientInfo.setLayout(framePatientInfoLayout)
        
        buttonNewExamination = QPushButton("New Examination")
        buttonNewExamination.clicked.connect(lambda: self.newExam_signal.emit())
        buttonNewExamination.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )

        buttonLoadExamination = QPushButton("Load Examination")
        buttonLoadExamination.clicked.connect(lambda: self.loadExam_signal.emit())
        buttonLoadExamination.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )



        framePatientInfoLayout.addWidget(buttonNewExamination, alignment=Qt.AlignmentFlag.AlignCenter)
        framePatientInfoLayout.addWidget(buttonLoadExamination, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.leftLayout.addWidget(framePatientInfo, stretch=1)

    def _createExamCardInfo(self):
        frameExamCards = QFrame()
        frameExamCards.setStyleSheet("QFrame { border: 2px solid black; }")
        
        labelExamCards = QLabel(frameExamCards)
        labelExamCards.setText("Exam Cards")
        labelExamCards.setStyleSheet("QLabel { color: black; }")  # Set the label style
        
        self.leftLayout.addWidget(frameExamCards, stretch=2)
        
    def _createScanProgressInfo(self):
        frameScanProgressInfo = QFrame()
        frameScanProgressInfo.setStyleSheet("QFrame { border: 2px solid black; }")
        
        self.frameScanProgressInfoLayout = QVBoxLayout()
        frameScanProgressInfo.setLayout(self.frameScanProgressInfoLayout)
        
        self._createProgressBar()
        self._createScanButtons()

        self.leftLayout.addWidget(frameScanProgressInfo, stretch=1)
    
    def _createProgressBar(self):
        scanProgressBarLayout = QHBoxLayout()
        
        scanProgressBarLabel = QLabel("Scan Progress:")
        scanProgressBarLabel.setStyleSheet("QLabel { border: none; }")  # Remove border
        scanProgressBarLayout.addWidget(scanProgressBarLabel)
        
        scanProgressBar = QProgressBar()
        scanProgressBar.setValue(50)
        scanProgressBarLayout.addWidget(scanProgressBar)
        
        self.frameScanProgressInfoLayout.addLayout(scanProgressBarLayout)
        
    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()
        
        scanStartButton = QPushButton("Start Scan")
        #scanStartButton.setStyleSheet("QPushButton { background-color: green; color: #ffffff; }")
        scanButtonsLayout.addWidget(scanStartButton)
        
        scanStopButton = QPushButton("Stop Scan")
        #scanStopButton.setStyleSheet("QPushButton { background-color: red; color: #ffffff; }") 
        scanButtonsLayout.addWidget(scanStopButton)
        
        self.frameScanProgressInfoLayout.addLayout(scanButtonsLayout)

    
    def _createScanPlanningWindow(self):
        frameScanPlanning = QFrame()
        frameScanPlanning.setStyleSheet("background-color: black; border: 1px solid black;")
        
        self.rightScanningLayout.addWidget(frameScanPlanning, stretch=1)
    
    def _createParameterTabs(self):
        tabsParameters= QTabWidget()
        tabsParameters.addTab(self._geometryTab(), "Geometry")
        tabsParameters.addTab(self._contrastTab(), "Contrast")
        
        self.layoutTabsAndImage.addWidget(tabsParameters,stretch=1)
                              
    def _geometryTab(self):
        geometryTab = QWidget()
        geometryLabel = QLabel(geometryTab)
        geometryLabel.setText("Geometry parameters")
        return geometryTab
    
    def _contrastTab(self):
        contrastTab = QWidget()
        contrastLabel = QLabel(contrastTab)
        contrastLabel.setText("Contrast parameters")
        return contrastTab
        
    def _createScannedImage(self):
        frameScannedImage = QFrame()
        frameScannedImage.setStyleSheet("background-color: black; border: 1px solid black;")
        
        self.layoutTabsAndImage.addWidget(frameScannedImage, stretch = 1)
        
    def _setupStates(self):
        # Define the states
        self.scanningMode_state = QState()
        self.viewingMode_state = QState()
        self.newExam_state = QState()
        self.loadExam_state = QState()

        # Add the states to the state machine 
        self.state_machine.addState(self.scanningMode_state)
        self.state_machine.addState(self.viewingMode_state)
        self.state_machine.addState(self.newExam_state)
        self.state_machine.addState(self.loadExam_state)
        
        # Set initial state
        self.state_machine.setInitialState(self.scanningMode_state)
        
        # Define actions related to states
        self.scanningMode_state.entered.connect(lambda: self.scanningMode_open())
        self.viewingMode_state.entered.connect(lambda: self.viewingMode_open())
        self.newExam_state.entered.connect(lambda: self.newExam_open())
        self.loadExam_state.entered.connect(lambda: self.loadExam_open())
        
        
    def _setupTransitions(self):
        self.scanningMode_state.addTransition(self.viewingMode_signal, self.viewingMode_state)
        self.viewingMode_state.addTransition(self.scanningMode_signal, self.scanningMode_state)
        self.scanningMode_state.addTransition(self.newExam_signal, self.newExam_state)
        self.scanningMode_state.addTransition(self.loadExam_signal, self.loadExam_state)

    def scanningMode_open(self):
        self.rightStackedLayout.setCurrentIndex(0)
        
    def viewingMode_open(self):
        self.rightStackedLayout.setCurrentIndex(1)

    def newExam_open(self): 
        dialog = QDialog()
        dialog.setWindowTitle("New examination")

        layout = QFormLayout()

        model_combo = QComboBox()
        model_combo.addItems(["Brain model", "Knee model", "Cylindrical phantom"])
        upload_button_model = QPushButton("Upload")
        upload_button_model.setStyleSheet("QPushButton { background-color: #0987e0; color: white}")


        model_combo_layout = QHBoxLayout()
        model_combo_layout.addWidget(model_combo)
        model_combo_layout.addWidget(upload_button_model)


        layout.addRow("Select model:", model_combo_layout)
        layout.addRow("Exam name:", QLineEdit())

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addRow(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def loadExam_open(self):
        msg_box = QMessageBox()
        msg_box.setText("Hello, world!")
        msg_box.exec()

        
# having a main() function like this is best practice in Python. This function provides the apps entry point.         
def main():
    
    # creates QApplication object
    eduMRIsimApp = QApplication([])

    
    # creates instance of app's window and shows GUI
    eduMRIsimWindow = eduMRIsimMainWindow()
    
    # Set the QSS stylesheet
    with open("stylesheet_eduMRIsim.qss", "r") as f:
        style_sheet = f.read()
    eduMRIsimWindow.setStyleSheet(style_sheet)
    
    eduMRIsimWindow.show()
    
    # runs application's event loop with .exec() 
    sys.exit(eduMRIsimApp.exec())
    
if __name__ == "__main__": 
    main()
        
        
        
        