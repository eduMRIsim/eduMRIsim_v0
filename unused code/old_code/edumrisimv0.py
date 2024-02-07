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
    
    scanning_mode_signal = pyqtSignal()
    viewing_mode_signal = pyqtSignal()
    new_exam_signal = pyqtSignal()
    load_exam_signal = pyqtSignal()
    
    def __init__(self):
        # This call allows you to properly initialize instances of this class. The parent argument is set to None because this will be the main window.
        super().__init__(parent=None)
        self.setWindowTitle("eduMRIsim")
        
        # Initialize the state machine
        self.stateMachine = QStateMachine()
        
        # Set up the UI
        self.setupUI()
        
        # Set up the states and transitions
        self.setupStates()
        self.setupTransitions()
        
        # Start State Machine
        self.stateMachine.start()
    
      
    def setupUI(self):    
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
        self._createStateLabel()
        
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
        
        self.tabsAndImageLayout = QHBoxLayout()
        
        self._createParameterTabs()
        self._createScannedImage()
        
        self.rightScanningLayout.addLayout(self.tabsAndImageLayout,stretch = 1)
        
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
        
        scanningModeButton.clicked.connect(lambda: self.scanning_mode_signal.emit())
        viewingModeButton.clicked.connect(lambda: self.viewing_mode_signal.emit())
        
        modeSwitchButtonsLayout.addWidget(scanningModeButton)
        modeSwitchButtonsLayout.addWidget(viewingModeButton)
        
        self.leftLayout.addLayout(modeSwitchButtonsLayout, stretch = 1)
    
        
    def _createPatientInfo(self):
        patientInfoFrame = QFrame()
        patientInfoFrame.setStyleSheet("QFrame { border: 2px solid black; }")
        
        patientInfoFrameLayout = QHBoxLayout()
        patientInfoFrame.setLayout(patientInfoFrameLayout)
        
        newExaminationButton = QPushButton("New Examination")
        newExaminationButton.clicked.connect(lambda: self.new_exam_signal.emit())
        newExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )

        loadExaminationButton = QPushButton("Load Examination")
        #buttonLoadExamination.clicked.connect(lambda: self.loadExam_signal.emit())
        loadExaminationButton.setStyleSheet("QPushButton { background-color: #0987e0; font-size: 16px; color: white; min-width: 150px; min-height: 100px;border-radius: 5px; }" )



        patientInfoFrameLayout.addWidget(newExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)
        patientInfoFrameLayout.addWidget(loadExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.leftLayout.addWidget(patientInfoFrame, stretch=1)

    def _createExamCardInfo(self):
        examCardsFrame = QFrame()
        examCardsFrame.setStyleSheet("QFrame { border: 2px solid black; }")
        
        examCardsLabel = QLabel(examCardsFrame)
        examCardsLabel.setText("Exam Cards")
        examCardsLabel.setStyleSheet("QLabel { color: black; }")  # Set the label style
        
        self.leftLayout.addWidget(examCardsFrame, stretch=2)
        
    def _createScanProgressInfo(self):
        scanProgressInfoFrame = QFrame()
        scanProgressInfoFrame.setStyleSheet("QFrame { border: 2px solid black; }")
        
        self.scanProgressInfoFrameLayout = QVBoxLayout()
        scanProgressInfoFrame.setLayout(self.scanProgressInfoFrameLayout)
        
        self._createProgressBar()
        self._createScanButtons()

        self.leftLayout.addWidget(scanProgressInfoFrame, stretch=1)
    
    def _createProgressBar(self):
        scanProgressBarLayout = QHBoxLayout()
        
        scanProgressBarLabel = QLabel("Scan Progress:")
        scanProgressBarLabel.setStyleSheet("QLabel { border: none; }")  # Remove border
        scanProgressBarLayout.addWidget(scanProgressBarLabel)
        
        scanProgressBar = QProgressBar()
        scanProgressBar.setValue(50)
        scanProgressBarLayout.addWidget(scanProgressBar)
        
        self.scanProgressInfoFrameLayout.addLayout(scanProgressBarLayout)
        
    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()
        
        scanStartButton = QPushButton("Start Scan")
        #scanStartButton.setStyleSheet("QPushButton { background-color: green; color: #ffffff; }")
        scanButtonsLayout.addWidget(scanStartButton)
        
        scanStopButton = QPushButton("Stop Scan")
        #scanStopButton.setStyleSheet("QPushButton { background-color: red; color: #ffffff; }") 
        scanButtonsLayout.addWidget(scanStopButton)
        
        self.scanProgressInfoFrameLayout.addLayout(scanButtonsLayout)

    def _createStateLabel(self):
        self.stateLabel = QLabel()
        self.stateLabel.setText("Current state:")

        self.leftLayout.addWidget(self.stateLabel)
    
    def _createScanPlanningWindow(self):
        scanPlanningFrame = QFrame()
        scanPlanningFrame.setStyleSheet("background-color: black; border: 1px solid black;")
        
        self.rightScanningLayout.addWidget(scanPlanningFrame, stretch=1)
    
    def _createParameterTabs(self):
        parametersTabs= QTabWidget()
        parametersTabs.addTab(self._geometryTab(), "Geometry")
        parametersTabs.addTab(self._contrastTab(), "Contrast")
        
        self.tabsAndImageLayout.addWidget(parametersTabs,stretch=1)
                              
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
        scannedImageFrame = QFrame()
        scannedImageFrame.setStyleSheet("background-color: black; border: 1px solid black;")
        
        self.tabsAndImageLayout.addWidget(scannedImageFrame, stretch = 1)
        
    def setupStates(self):
        # Define the states
        self.scanningModeState = QState()
        self.viewingModeState = QState()
        self.newExamState = QState()
        self.loadExamState = QState()

        # Add the states to the state machine 
        self.stateMachine.addState(self.scanningModeState)
        self.stateMachine.addState(self.viewingModeState)
        self.stateMachine.addState(self.newExamState)
        self.stateMachine.addState(self.loadExamState)
        
        # Set initial state
        self.stateMachine.setInitialState(self.scanningModeState)
        
        # Define actions related to states
        self.scanningModeState.entered.connect(lambda: self.openScanningMode())
        self.viewingModeState.entered.connect(lambda: self.openViewingMode())
        self.newExamState.entered.connect(lambda: self.openNewExam())
        self.loadExamState.entered.connect(lambda: self.openLoadExam())
        
        
    def setupTransitions(self):
        self.scanningModeState.addTransition(self.viewing_mode_signal, self.viewingModeState)
        self.viewingModeState.addTransition(self.scanning_mode_signal, self.scanningModeState)
        self.scanningModeState.addTransition(self.new_exam_signal, self.newExamState)
        self.scanningModeState.addTransition(self.load_exam_signal, self.loadExamState)

        self.newExamState.addTransition(self.scanning_mode_signal, self.scanningModeState)

    def openScanningMode(self):
        self.rightStackedLayout.setCurrentIndex(0)
        self.stateLabel.setText("Current state: scanning mode")
        
    def openViewingMode(self):
        self.rightStackedLayout.setCurrentIndex(1)
        self.stateLabel.setText("Current state: viewing mode")

    def openNewExam(self): 
        self.stateLabel.setText("Current state: start new examination")

        self.dialog = QDialog()
        self.dialog.setWindowTitle("New examination")

        layout = QVBoxLayout()

        formLayout = QFormLayout()

        modelCombo = QComboBox()
        modelCombo.addItems(["Brain model", "Knee model", "Cylindrical phantom"])
        uploadModelButton = QPushButton("Upload")
        uploadModelButton.setStyleSheet("QPushButton { background-color: #0987e0; color: white}")


        modelComboLayout = QHBoxLayout()
        modelComboLayout.addWidget(modelCombo)
        modelComboLayout.addWidget(uploadModelButton)


        formLayout.addRow("Select model:", modelComboLayout)
        formLayout.addRow("Exam name:", QLineEdit())

        buttonsLayout = QHBoxLayout()

        okButton = QPushButton("OK")
        okButton.clicked.connect(self.newExamOkPressed)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.newExamCancelPressed)

        buttonsLayout.addWidget(okButton)
        buttonsLayout.addWidget(cancelButton)


        layout.addLayout(formLayout)
        layout.addLayout(buttonsLayout)

        self.dialog.setLayout(layout)
        self.dialog.exec()

    def newExamOkPressed(self):
        self.scanning_mode_signal.emit()  # Emit the signal
        self.dialog.accept()  # Close the dialog

    def newExamCancelPressed(self):
        self.scanning_mode_signal.emit()  # Emit the signal
        self.dialog.accept()  # Close the dialog

    def openLoadExam(self):
        self.stateLabel.setText("Current state: load examination")

        msgBox = QMessageBox()
        msgBox.setText("Hello, world!")
        msgBox.exec()

        
# having a main() function like this is best practice in Python. This function provides the apps entry point.         
def main():
    
    # creates QApplication object
    eduMRIsimApp = QApplication([])

    
    # creates instance of app's window and shows GUI
    eduMRIsimWindow = eduMRIsimMainWindow()
    
    # Set the QSS stylesheet
    # with open("stylesheet_eduMRIsim.qss", "r") as f:
    #     style_sheet = f.read()
    # eduMRIsimWindow.setStyleSheet(style_sheet)
    
    eduMRIsimWindow.show()
    
    # runs application's event loop with .exec() 
    sys.exit(eduMRIsimApp.exec())
    
if __name__ == "__main__": 
    main()
        
        
        
        