from PyQt5.QtCore import Qt, QObject, pyqtSignal, QPointF, QEvent
from PyQt5.QtWidgets import (QComboBox, QFormLayout, QFrame, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem,
                             QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListView, QListWidget, QMainWindow, QProgressBar, QPushButton, QSizePolicy,
                             QStackedLayout, QTabWidget, QVBoxLayout, QWidget, QSpacerItem, QScrollArea,
                             QGraphicsTextItem, QGraphicsPolygonItem, QGraphicsSceneMouseEvent, QGraphicsItem,
                             QGraphicsEllipseItem, QApplication)
from PyQt5.QtGui import QPainter, QPixmap, QImage, QResizeEvent, QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent, QFont, QPolygonF

import numpy as np

from contextlib import contextmanager

from views.UI_MainWindowState import IdleState
from views.styled_widgets import SegmentedButtonFrame, SegmentedButton, PrimaryActionButton, SecondaryActionButton, TertiaryActionButton, DestructiveActionButton, InfoFrame, HeaderLabel

from simulator.scanlist import AcquiredSeries, ScanVolume

from events import EventEnum

'''Note about naming: PyQt uses camelCase for method names and variable names. This unfortunately conflicts with the naming convention used in Python. Most of the PyQt related code in eduRMIsim uses the PyQt naming convention. However, I've noticed that I haven't been fully consistent with this so I realise some of the naming might be confusing. I might change the names in the future. For the SEP project feel free to use whichever convention you find most convenient when adding new PyQt related code.'''

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

        self._state = IdleState()
        self.update_UI()
    
    def update_UI(self):
        self.state.update_UI(self)

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
        #leftLayout.addLayout(self._modeSwitchButtonsLayout, stretch=1)

        self._preExaminationInfoFrame = PreExaminationInfoFrame()
        self._examinationInfoFrame = InfoFrame("Examination", "Model")
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
        self._scannedImageFrame = AcquiredSeriesViewer2D()
        bottomLayout.addWidget(self._scannedImageFrame, stretch=1)

        rightLayout.addLayout(bottomLayout,stretch=1)

        return rightLayout
    
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
        self.setStyleSheet("""
            PreExaminationInfoFrame {
                background-color: white; /* Background color */
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """)
        self.layout = QVBoxLayout()
        self.welcomeLabel = QLabel("Welcome to eduMRIsim!", alignment=Qt.AlignmentFlag.AlignCenter)
        self.welcomeLabel.setStyleSheet("QLabel { font-size: 24px; }")
        self.setLayout(self.layout)
        self.layout.addWidget(self.welcomeLabel)
        self.horizontalLayout = QHBoxLayout()
        self._createNewExaminationButton()
        self._createLoadExaminationButton()
        self.layout.addLayout(self.horizontalLayout)

    def _createNewExaminationButton(self):
        self._newExaminationButton = PrimaryActionButton("New Examination")
        self._newExaminationButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalLayout.addWidget(self._newExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def _createLoadExaminationButton(self):
        self._loadExaminationButton = PrimaryActionButton("Load Examination")
        self._loadExaminationButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalLayout.addWidget(self._loadExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def newExaminationButton(self):
        return self._newExaminationButton
    
    @property
    def loadExaminationButton(self):
        return self._loadExaminationButton
    
class ScanlistInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            ScanlistInfoFrame {
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._addScanItemButton = PrimaryActionButton("Add Scan Item")
        self._scanlistListWidget = ScanlistListWidget()
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
        self.setSelectionMode(self.SingleSelection)
        self.setAcceptDrops(True)
  


    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            self.setCurrentItem(item)
            self.itemDoubleClicked.emit(item)  # Manually emit the itemDoubleClicked signal


    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        e.accept()

    def dragMoveEvent(self, e: QDragMoveEvent) -> None:
        e.accept()

    def dropEvent(self, e: QDropEvent):
        # Get the widget that received the drop event
        widget = e.source()
        # do not accept drops from itself
        if widget == self:
            e.ignore()
        else:    
            selected_indexes = widget.selectedIndexes()
            self.dropEventSignal.emit(selected_indexes)
            e.accept()        

class ScanProgressInfoFrame(QFrame):
    def __init__(self, scanner):
        super().__init__()
        self.setStyleSheet("""
            ScanProgressInfoFrame {
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.scanner = scanner
        self._createProgressBar()
        self._createScanButtons()

    @property
    def scanProgressBar(self):
        return self._scanProgressBar
    
    @property
    def startScanButton(self):
        return self._startScanButton
    
    @property
    def stopScanButton(self):
        return self._stopScanButton
 
    def _createProgressBar(self):
        scanProgressBarLayout = QHBoxLayout()   

        self._scanProgressBar = QProgressBar()

        self._scanProgressBar.setValue(0)
        # Set a custom stylesheet for the progress bar to customize its appearance
        self._scanProgressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #6bcc7a; /* Set the color of the progress bar chunk */
            }
        """)        
        scanProgressBarLayout.addWidget(self._scanProgressBar)
        

        self.layout.addLayout(scanProgressBarLayout)
        
    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()
        
        self._startScanButton = SecondaryActionButton("Start Scan")
        scanButtonsLayout.addWidget(self._startScanButton)
        
        self._stopScanButton = DestructiveActionButton("Stop Scan")
        scanButtonsLayout.addWidget(self._stopScanButton)

        self.layout.addLayout(scanButtonsLayout)

class ScanPlanningWindow(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        self.ImageLabelTuple = tuple(DropAcquiredSeriesViewer2D() for i in range(3))
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
        self._scanParametersSaveChangesButton = PrimaryActionButton("Save")
        self._scanParametersCancelChangesButton = SecondaryActionButton("Cancel")
        self._scanParametersResetButton = DestructiveActionButton("Reset")
        buttonsLayout.addWidget(self._scanParametersSaveChangesButton, 1)
        buttonsLayout.addWidget(self._scanParametersCancelChangesButton, 1)
        buttonsLayout.addSpacerItem(QSpacerItem(self._scanParametersSaveChangesButton.sizeHint().width(), self._scanParametersSaveChangesButton.sizeHint().height(), QSizePolicy.Expanding, QSizePolicy.Minimum))
        buttonsLayout.addWidget(self._scanParametersResetButton, 1)
        self.layout.addLayout(buttonsLayout)        
    
class ExamCardTabWidget(QTabWidget):
    def __init__(self, examCardTab):
        super().__init__()
        self.addTab(examCardTab, "Scan items")

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
        self.addTab(self.parameterTab, "Scan parameters")
        
    @property
    def parameterFormLayout(self):
        return self.parameterTab.parameterFormLayout

class ParameterTab(QScrollArea):
    def __init__(self):
        super().__init__()
        container_widget = self.createContainerWidget()
        self.setWidget(container_widget)
        self.setWidgetResizable(True)
    
    def createContainerWidget(self):
        self.horizontalLayout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self._parameterFormLayout = ParameterFormLayout()
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addLayout(self.parameterFormLayout)
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        #self.horizontalLayout.addItem(QSpacerItem(10, 0,  QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.horizontalLayout.addLayout(self.layout)
        self.horizontalLayout.addItem(QSpacerItem(0, 0,  QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setStyleSheet("QLineEdit { border: 1px solid  #BFBFBF; }")
        containerWidget = QWidget()
        containerWidget.setLayout(self.horizontalLayout)
        return containerWidget

    @property
    def parameterFormLayout(self):
        return self._parameterFormLayout    
    
class ParameterFormLayout(QVBoxLayout):
    formActivatedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.isReadOnly = True
        self.editors = {}

    def createForm(self, parameters : dict) -> None:
        # Create form elements based on the data in "parameters".
        for parameter in parameters:
            name = parameter["name"]
            parameter_key = parameter["key"]
            editor_type = parameter["editor"]
            default_value = parameter["default_value"]
            unit = parameter["unit"]

            parameter_layout = QGridLayout()

            # Create the appropriate editor widget based on the editor type.
            if editor_type == "QLineEdit":
                editor = QLineEdit()
                editor.setText(default_value)
                parameter_layout.addWidget(QLabel(name), 0, 0, Qt.AlignLeft)
                parameter_layout.addWidget(editor, 1, 0, Qt.AlignLeft)
                parameter_layout.addWidget(HeaderLabel(unit), 1, 1, Qt.AlignLeft)
                editor.textChanged.connect(lambda: self.formActivatedSignal.emit())
            elif editor_type == "QComboBox":
                editor = QComboBox()
                editor.addItems(default_value)
                editor.setCurrentIndex(0)
                parameter_layout.addWidget(QLabel(name), 0, 0, Qt.AlignLeft)
                parameter_layout.addWidget(editor, 1, 0, Qt.AlignLeft)
                editor.currentIndexChanged.connect(lambda: self.formActivatedSignal.emit())
            else:
                raise ValueError(f"Unknown editor type: {editor_type}") # Raise an error if the editor type is unknown. If the error is raised, the program will stop executing. 
            
            editor.setFixedHeight(30)
            editor.setFixedWidth(300)
            editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # Add the editor widget to the layout.
        
            self.addLayout(parameter_layout)

            # Add a vertical spacer (with expandable space)
            spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.addSpacerItem(spacer)

            # Store the editor widget in the dictionary for later access.
            self.editors[parameter_key] = editor

    def get_parameters(self):
        # Create a dictionary to store the current values of the editor widgets.
        parameters = {}

        # Get the current value of each editor widget and store it in a dictionary.
        for name, editor in self.editors.items():
            if isinstance(editor, QLineEdit):
                parameters[name] = editor.text()
            elif isinstance(editor, QComboBox):
                parameters[name] = editor.currentText()
            else:
                raise ValueError(f"Unknown editor type: {type(editor)}")
            
        return parameters
            
    def set_parameters(self, parameters):
        # Set the data into the editors
        with block_signals(self.editors.values()):
            for name, value in parameters.items():
                if name in self.editors: # Checks if the string name is a key in the self.editors dictionary.
                    editor = self.editors[name] # Get the editor widget from the dictionary.
                    if isinstance(editor, QLineEdit):
                        editor.setText(str(value))
                    elif isinstance(editor, QComboBox):
                        index = editor.findText(str(value))
                        if index != -1:
                            editor.setCurrentIndex(index)        

    def setReadOnly(self, bool : bool):
        for editor in self.editors.values():
            if isinstance(editor, (QLineEdit)):
                editor.setReadOnly(bool)
            if isinstance(editor, (QComboBox)):
                editor.setEnabled(not bool)
        self.isReadOnly = bool

    def clearForm(self):
        with block_signals(self.editors.values()):
            for editor in self.editors.values():
                if isinstance(editor, QLineEdit):
                    editor.clear()
                elif isinstance(editor, QComboBox):
                    editor.setCurrentIndex(0)

class CustomPolygonItem(QGraphicsPolygonItem):
    '''Represents the intersection of the scan volume with the image in the viewer as a polygon. The polygon is movable and sends an update to the observers when it has been moved. '''
    def __init__(self, parent: QGraphicsPixmapItem, viewer):
        super().__init__(parent)
        self.setPen(Qt.red)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.observers = []
        self.previous_position_in_pixmap_coords = None

        # Scale parameters, including scale handles.
        self.is_being_scaled = False
        self.scale_handles = []
        for i in range(8):
            handle = QGraphicsEllipseItem(-5, -5, 10, 10, parent=self)
            handle.setPen(Qt.yellow)
            handle.setFlag(QGraphicsItem.ItemIsMovable, enabled=False)
            handle.setAcceptedMouseButtons(Qt.LeftButton)
            handle.setAcceptHoverEvents(True)
            handle.setCursor(Qt.PointingHandCursor)
            handle.mousePressEvent = lambda event, hdl=handle: self.scale_handle_press_event_handler(event, hdl)
            self.scale_handles.append(handle)
        self.scale_handle_offsets = []
        self.active_scale_handle = None
        self.scene_center = QPointF(0.0, 0.0)
        self.previous_scale_handle_position = None
        self.viewer = viewer

        self.on_x_axis = False
        self.on_y_axis = False

        # Set the initial position of the scale handles.
        self.update_scale_handle_positions()

    def update_scale_handle_positions(self):
        """
        This function updates the scale handle positions so that they are moved to their new positions.
        """

        # Get the current polygon and its number of points.
        polygon = self.polygon()
        number_of_points = len(polygon)

        # Error case, avoids division by zero.
        if number_of_points == 0:
            return

        # Find the local center of the polygon's points.
        local_center = QPointF(sum(point.x() for point in polygon) / number_of_points, sum(point.y() for point in polygon) / number_of_points)

        # Set the new handle positions based on the local center and the offsets.
        # Also, show only the first few handles.
        for i, offset in enumerate(self.scale_handle_offsets):
            if i >= len(self.scale_handles):
                break
            handle = self.scale_handles[i]
            handle_pos_local = local_center + offset
            handle.setPos(handle_pos_local)
            handle.setVisible(True)

        # Hide the remaining handles.
        for i in range(len(self.scale_handle_offsets), len(self.scale_handles)):
            self.scale_handles[i].setVisible(False)

    def scale_handle_press_event_handler(self, event: QGraphicsSceneMouseEvent, handle):
        """
        This function is an event handler that is called whenever the user left-clicks on a scale handle.
        :param event: the mouse event that the user performed by left-clicking on a scale handle.
        :param handle: the scale handle that the user clicked on.
        """

        self.is_being_scaled = True
        self.active_scale_handle = handle  # Keep track of which handle is active.
        self.previous_scale_handle_position = event.scenePos()
        handle.setCursor(Qt.ClosedHandCursor)

        # Get the current polygon (points), and the number of points in the current polygon.
        polygon = self.polygon()
        number_of_points = len(polygon)

        # Define axis booleans
        self.on_x_axis = False
        self.on_y_axis = False
        self.on_z_axis = False

        # If the current polygon has no points, the scene center will be (0.0, 0.0) in scene coordinates;
        # else, the scene center is the center of all points in the polygon.
        if number_of_points == 0:
            self.scene_center = QPointF(0.0, 0.0)
        else:
            self.scene_center = QPointF(sum(point.x() for point in polygon) / number_of_points, sum(point.y() for point in polygon) / number_of_points)
            self.scene_center = self.mapToScene(self.scene_center)

        #self.on_x_axis = abs(self.previous_scale_handle_position.x() - self.scene_center.x()) <= 5.5
        #self.on_y_axis = abs(self.previous_scale_handle_position.y() - self.scene_center.y()) <= 5.5

        # Find which plane we are on
        axis = self.get_plane_axis()

        if axis == 'FH':
            self.on_x_axis = abs(self.previous_scale_handle_position.x() - self.scene_center.x()) <= 5.5
            self.on_z_axis = abs(self.previous_scale_handle_position.y() - self.scene_center.y()) <= 5.5
        elif axis == 'AP':
            self.on_y_axis = abs(self.previous_scale_handle_position.y() - self.scene_center.y()) <= 5.5
            self.on_z_axis = abs(self.previous_scale_handle_position.x() - self.scene_center.x()) <= 5.5
        elif axis == 'RL':
            self.on_x_axis = abs(self.previous_scale_handle_position.x() - self.scene_center.x()) <= 5.5
            self.on_y_axis = abs(self.previous_scale_handle_position.y() - self.scene_center.y()) <= 5.5


        print(f"{self.on_x_axis = }, {self.on_y_axis = }, {self.on_z_axis = }" )
        print(self.get_plane_axis())

    def scale_handle_move_event_handler(self, event: QGraphicsSceneMouseEvent):
        """
        This function is called whenever a scale handle is moved,
        i.e. when the user holds left click on and drags a scale handle to a new position.
        :param event: the mouse event that the user performed by holding left click on and dragging a scale handle.
        """

        # Get the new position in scene coordinates.
        new_position = event.scenePos()

        # Calculate the scale factors in the x and y directions.
        # Also, avoid division by zero, which would happen if the previous scale handle position's x or y is equal to
        # the scene center's x or y respectively; in that case, set the respective scale factor to 1.0.
        if self.on_x_axis:
            scale_factor_x = 1.0
        else:
            scale_factor_x = abs(new_position.x() - self.scene_center.x()) / abs(self.previous_scale_handle_position.x() - self.scene_center.x())
        if self.on_y_axis:
            scale_factor_y = 1.0
        else:
            scale_factor_y = abs(new_position.y() - self.scene_center.y()) / abs(self.previous_scale_handle_position.y() - self.scene_center.y())

        # Set the previous handle position equal to the new handle position.
        self.previous_scale_handle_position = new_position

        # Let the other windows know that the scan volume display was scaled, passing in the calculated scale factors.
        self.notify_observers(EventEnum.SCAN_VOLUME_DISPLAY_SCALED, scale_factor_x=scale_factor_x, scale_factor_y=scale_factor_y, origin_plane=self.viewer.displayed_image.image_geometry.plane, handle_pos=self.active_scale_handle.pos())

        # Update the scale handle positions.
        self.update_scale_handle_positions()

        axis = self.get_plane_axis()

        print(axis)

    def scale_handle_release_event_handler(self):
        """
        This function is called whenever a scale handle is released,
        i.e. when the user stops holding left click on the scale handle.
        """

        self.is_being_scaled = False
        self.on_x_axis = False
        self.on_y_axis = False

        # Reset the active scale handle if it was set previously.
        if self.active_scale_handle is not None:
            self.active_scale_handle.setCursor(Qt.PointingHandCursor)
            self.active_scale_handle = None

    def get_plane_axis(self):
        '''Determine the rotation axis based on the displayed image plane'''
        plane = self.viewer.displayed_image.image_geometry.plane

        if plane is None:
            raise ValueError("Image plane is not set in ImageGeometry.")

        plane = plane.lower()

        if plane == 'axial':
            return 'FH'
        elif plane == 'sagittal':
            return 'RL'
        elif plane == 'coronal':
            return 'AP'
        else:
            raise ValueError(f"Unknown plane: {plane}")

    def setPolygon(self, polygon_in_polygon_coords: QPolygonF):
        number_of_points = len(polygon_in_polygon_coords)
        if number_of_points == 0:
            super().setPolygon(polygon_in_polygon_coords)
            for handle in self.scale_handles:
                handle.setVisible(False)
            self.scale_handle_offsets = []
            return

        super().setPolygon(polygon_in_polygon_coords)
        self.previous_position_in_pixmap_coords = self.pos()

        local_center = QPointF(sum(point.x() for point in polygon_in_polygon_coords) / number_of_points, sum(point.y() for point in polygon_in_polygon_coords) / number_of_points)

        self.scale_handle_offsets = []
        for i in range(len(polygon_in_polygon_coords)):
            offset = (polygon_in_polygon_coords[i] + polygon_in_polygon_coords[(i+1) % number_of_points]) / 2 - local_center
            self.scale_handle_offsets.append(offset)

        self.update_scale_handle_positions()

    def setPolygonFromPixmapCoords(self, polygon_in_pixmap_coords: list[np.array]):
        polygon_in_polygon_coords = QPolygonF()
        for pt in polygon_in_pixmap_coords:
            pt_in_polygon_coords = self.mapFromParent(QPointF(pt[0], pt[1]))
            polygon_in_polygon_coords.append(pt_in_polygon_coords)
        self.setPolygon(polygon_in_polygon_coords)

    def add_observer(self, observer: object):
        self.observers.append(observer)
        #print("Observer", observer, "added to", self)

    def notify_observers(self, event: EventEnum, **kwargs):
        for observer in self.observers:
            #print("Subject", self, "is updating observer", observer, "with event", event)
            observer.update(event, direction_vector_in_pixmap_coords=kwargs.get('direction_vector_in_pixmap_coords'), scale_factor_x=kwargs.get('scale_factor_x'), scale_factor_y=kwargs.get('scale_factor_y'), origin_plane=kwargs.get('origin_plane'), handle_pos=kwargs.get('handle_pos'))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        #print(self.viewer.displayed_image.image_geometry.plane)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(event)
        direction_vector_in_pixmap_coords = QPointF(self.pos().x() - self.previous_position_in_pixmap_coords.x(), self.pos().y() - self.previous_position_in_pixmap_coords.y())
        self.previous_position_in_pixmap_coords = self.pos()
        self.update_scale_handle_positions()
        self.notify_observers(EventEnum.SCAN_VOLUME_DISPLAY_TRANSLATED, direction_vector_in_pixmap_coords=direction_vector_in_pixmap_coords)

class AcquiredSeriesViewer2D(QGraphicsView):
    '''Displays an acquired series of 2D images in a QGraphicsView. The user can scroll through the images using the mouse wheel. The viewer also displays the intersection of the scan volume with the image in the viewer. The intersection is represented with a CustomPolygonItem. The CustomPolygonItem is movable and sends geometry changes to the observers. Each acquired image observes the CustomPolygonItem and updates the scan volume when the CustomPolygonItem is moved.
    '''

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

        # Initialize displayed image to None
        self.displayed_image = None

        # Initalize displayed series to None
        self.acquired_series = None

        # Initalize scan volume to None
        self.scan_volume = None

        # Initialize array attribute to None
        self.array = None

        self.scan_volume_display = CustomPolygonItem(self.pixmap_item, viewer=self) # Create a custom polygon item that is a child of the pixmap item
        self.scan_volume_display.add_observer(self)

        self.scene.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneMouseMove:
            if self.scan_volume_display is not None and self.scan_volume_display.is_being_scaled:
                self.scan_volume_display.scale_handle_move_event_handler(event)
                return True
        elif event.type() == QEvent.GraphicsSceneMouseRelease:
            if self.scan_volume_display is not None and self.scan_volume_display.is_being_scaled:
                self.scan_volume_display.scale_handle_release_event_handler()
                return True
        return super().eventFilter(source, event)

    def resizeEvent(self, event: QResizeEvent):
        '''This method is called whenever the graphics view is resized. It ensures that the image is always scaled to fit the view.''' 
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def _displayArray(self):
        width, height = 0, 0
        if self.array is not None:

            # Normalize the slice values for display
            array_norm = (self.array[:,:] - np.min(self.array)) / (np.max(self.array) - np.min(self.array))
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

    def update(self, event: EventEnum, **kwargs): 
        if event == EventEnum.SCAN_VOLUME_CHANGED:
            self._update_scan_volume_display()

        if event == EventEnum.SCAN_VOLUME_DISPLAY_TRANSLATED:
            direction_vector_in_pixmap_coords = (kwargs['direction_vector_in_pixmap_coords'].x(), kwargs['direction_vector_in_pixmap_coords'].y())
            direction_vector_in_LPS_coords = np.array(self.displayed_image.image_geometry.pixmap_coords_to_LPS_coords(direction_vector_in_pixmap_coords)) - np.array(self.displayed_image.image_geometry.pixmap_coords_to_LPS_coords((0, 0)))
            self.scan_volume.remove_observer(self)
            self.scan_volume.translate_scan_volume(direction_vector_in_LPS_coords)
            self.scan_volume.add_observer(self)

        if event == EventEnum.SCAN_VOLUME_DISPLAY_SCALED:
            scale_factor_x = kwargs['scale_factor_x']
            scale_factor_y = kwargs['scale_factor_y']
            origin_plane = kwargs['origin_plane']
            handle_pos = kwargs['handle_pos']

            # self.scan_volume.remove_observer(self)
            self.scan_volume.scale_scan_volume(scale_factor_x, scale_factor_y, origin_plane, handle_pos)
            self._update_scan_volume_display()
            # self.scan_volume.add_observer(self)

    def wheelEvent(self, event):
        # Check if the array is None
        if self.array is None:
            # Do nothing and return
            return
        displayed_image_index = self.displayed_image_index
        delta = event.angleDelta().y() 
        if delta > 0:
            new_displayed_image_index = max(0, min(displayed_image_index + 1, len(self.acquired_series.list_acquired_images) - 1))
        elif delta < 0:
            new_displayed_image_index = max(0, min(displayed_image_index - 1, len(self.acquired_series.list_acquired_images) - 1))
        elif delta == 0:
            new_displayed_image_index = displayed_image_index
        self.displayed_image_index = new_displayed_image_index
        self.setDisplayedImage(self.acquired_series.list_acquired_images[self.displayed_image_index])

    def setAcquiredSeries(self, acquired_series : AcquiredSeries):
        if acquired_series is not None:
            self.acquired_series = acquired_series
            self.displayed_image_index = 0 
            self.setDisplayedImage(self.acquired_series.list_acquired_images[self.displayed_image_index])
        else:
            self.acquired_series = None
            self.setDisplayedImage(None)

    def setDisplayedImage(self, image):
        self.displayed_image = image
        if image is not None:
            self.array = image.image_data

        else:
            self.array = None
        self._displayArray()
        self._update_scan_volume_display()

    def setScanVolume(self, scan_volume: ScanVolume):
        # remove the observer from the previous scan volume
        if self.scan_volume is not None:
            self.scan_volume.remove_observer(self)
        # set the new scan volume and observe it
        self.scan_volume = scan_volume
        self.scan_volume.add_observer(self)
        # update the intersection polygon
        self._update_scan_volume_display()
    
    def _update_scan_volume_display(self):
        '''Updates the intersection polygon between the scan volume and the displayed image.'''
        if self.displayed_image is not None and self.scan_volume is not None:
            intersection_in_pixmap_coords = self.scan_volume.compute_intersection_with_acquired_image(self.displayed_image)
            self.scan_volume_display.setPolygonFromPixmapCoords(intersection_in_pixmap_coords)
        else: 
            self.scan_volume_display.setPolygon(QPolygonF())

class DropAcquiredSeriesViewer2D(AcquiredSeriesViewer2D):
    '''Subclass of AcquiredSeriesViewer2D that can accept drops from scanlistListWidget. The dropEventSignal is emitted when a drop event occurs.'''
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
        self.dropEventSignal.emit(selected_index)
        event.accept()

class ImageLabel(QGraphicsView):
    '''Old version of AcquiredSeriesViewer2D. This viewer is still used to display the anatomical model in the model viewing dialog.'''
    def __init__(self):
        super().__init__()

        # QGraphicsScene is essentially a container that holds and manages the graphical items you want to display in your QGraphicsView. QGraphicsScene is a container and manager while QGraphicsView is responsible for actually displaying those items visually. 
        self.scene = QGraphicsScene(self)

        # Creates a pixmap graphics item that will be added to the scene
        self.pixmap_item = QGraphicsPixmapItem()

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
        self._current_slice = None

        self._window_width = None
        self._window_level = None

        self.observers = []

        self.middle_mouse_button_pressed = False
        self._displaying = False

        self.scene.addItem(self.pixmap_item)

        self.text_item = QGraphicsTextItem(self.pixmap_item)
        # change text color to white
        self.text_item.setDefaultTextColor(Qt.white)
        # set font size
        self.text_item.setFont(QFont("Arial", 5))

    @property
    def displaying(self):
        return self._displaying
    
    @displaying.setter
    def displaying(self, bool):
        if bool == True:
            self._displaying = True
        else:
            self._displaying = False
            self.array = None
            self.current_slice = None
            self.window_width = None
            self.window_level = None
            self.text_item.setPlainText("")

    @property
    def current_slice(self):
        return self._current_slice
    
    @current_slice.setter
    def current_slice(self, value):
        self._current_slice = value

    @property
    def window_width(self):
        return self._window_width

    @window_width.setter
    def window_width(self, value):
        self._window_width = value

    @property
    def window_level(self):
        return self._window_level
    
    @window_level.setter
    def window_level(self, value):
        self._window_level = value

    def set_window_width_level(self, window_width, window_level):
        self._window_width = window_width
        self._window_level = window_level
        self.notify_observers(window_width, window_level)

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

        delta = event.angleDelta().y() 
        current_slice = getattr(self, 'current_slice', 0)
        if delta > 0:
            new_slice = max(0, min(current_slice + 1, self.array.shape[2] - 1))
        elif delta < 0:
            new_slice = max(0, min(current_slice - 1, self.array.shape[2] - 1))
        elif delta == 0:
            new_slice = current_slice
        self.current_slice = int(new_slice)
        self.displayArray()


    #ImageLabel holds a copy of the array of MRI data to be displayed. 
    def setArray(self, array):
        # Set the array and make current_slice the middle slice by default
        self.array = array
        if array is not None:
            self.displaying = True
            self.current_slice = array.shape[2] // 2    
            window_width, window_level = self.calculate_window_width_level(method='percentile')
            self.set_window_width_level(window_width, window_level) 
        else:
            self.displaying = False
           
    def displayArray(self):
        width, height = 0, 0
        if self.displaying == True:
            windowed_array = self.apply_window_width_level()
            array_8bit = (windowed_array * 255).astype(np.uint8)

            # Convert the array to QImage for display. This is because you cannot directly set a QPixmap from a NumPy array. You need to convert the array to a QImage first.
            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

            self.update_text_item()


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

    def update_text_item(self):
        # set text
        text = f"Slice: {self.current_slice + 1}/{self.array.shape[2]}\nWW: {self.window_width:.2f}\nWL: {self.window_level:.2f}"
        self.text_item.setPlainText(text) # setPlainText() sets the text of the text item to the specified text.

        # set position of text
        pixmap_rect = self.pixmap_item.boundingRect() # boundingRect() returns the bounding rectangle of the pixmap item in the pixmap's local coordinates.
        # set position of text to the bottom right corner of the pixmap
        text_rect = self.text_item.boundingRect() # boundingRect() returns the bounding rectangle of the text item in the text item's local coordinates.
        x = pixmap_rect.right() - text_rect.width() - 5 # Adjusted to the right by 10 pixels for padding
        y = pixmap_rect.bottom() - text_rect.height() - 5 # Adjusted to the bottom by 10 pixels for padding
        self.text_item.setPos(x, y) # setPos() sets the position of the text item in the parent item's (i.e., the pixmap's) coordinates.

    def calculate_window_width_level(self, method='std', **kwargs):
        """
        Calculate window width and level based on signal intensity distribution of middle slice of signal array.

        Parameters:
        method (str): Method to calculate WW and WL ('std' or 'percentile').
        std_multiplier (float): Multiplier for the standard deviation (only used if method is 'std').

        Returns:
        tuple: (window_width, window_level)
        """        

        array = self.array[:,:,self.array.shape[2] // 2] # window width and level will be calculate based on middle slice of array 

        if method == 'std':
            std_multiplier = kwargs.get('std_multiplier', 2)
            window_level = np.mean(array)
            window_width = std_multiplier * np.std(array)
        elif method == 'percentile':
            lower_percentile = kwargs.get('lower_percentile', 5)
            upper_percentile = kwargs.get('upper_percentile', 95)
            lower_percentile_value = np.percentile(array, lower_percentile) # value blow which lower_percentile of the data lies
            upper_percentile_value = np.percentile(array, upper_percentile) # value below which upper_percentile of the data lies
            window_width = upper_percentile_value - lower_percentile_value
            window_level = lower_percentile_value + window_width / 2
        elif method == 'none':
            window_width = np.max(array) - np.min(array)
            window_level = (np.max(array) + np.min(array)) / 2
        else:
            raise ValueError(f"Invalid method: {method}")

        return window_width, window_level

    def apply_window_width_level(self):
        """
        Apply window width and level to the displayed slice of the signal array.

        Returns:
        numpy.ndarray: The windowed array of the displayed slice (normalized).
        """
        windowed_array = np.clip(self.array[:,:,self.current_slice], self.window_level - self.window_width / 2, self.window_level + self.window_width / 2)
        windowed_array = (windowed_array - (self.window_level - self.window_width / 2)) / self.window_width
        return windowed_array

    def add_observer(self, observer):
        self.observers.append(observer)
        #print("Observer", observer, "added to", self)

    def notify_observers(self, window_width, window_level):
        for observer in self.observers:
            observer.update(window_width, window_level)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_button_pressed = True
            self.start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_button_pressed = False

    def mouseMoveEvent(self, event):
        if self.displaying == False:
            return

        if self.middle_mouse_button_pressed:
            dx = event.x() - self.start_pos.x()
            dy = self.start_pos.y() - event.y()

            window_level = max(0, self.window_level + dy*0.001)
            window_width = max(0,self.window_width + dx*0.001)

            self.start_pos = event.pos()    

            self.set_window_width_level(window_width, window_level)
            self.displayArray()

    def update(self, window_width, window_level):
        if self.displaying == False:
            return
        if self.window_width != window_width or self.window_level != window_level:
            self.set_window_width_level(window_width, window_level)
            self.displayArray()
        else:
            pass

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
        self.dropEventSignal.emit(selected_index)
        event.accept()