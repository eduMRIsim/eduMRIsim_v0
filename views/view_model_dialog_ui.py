from PyQt5.QtCore import Qt, pyqtSignal, QSize, QStringListModel
from PyQt5.QtWidgets import  QDialog, QHBoxLayout, QPushButton, QLabel, QSlider, QVBoxLayout, QGridLayout, QLineEdit, QFrame, QWidget, QListView

from PyQt5.QtGui import QMouseEvent, QPixmap, QImage, QDragMoveEvent, QDropEvent
import numpy as np
from views.main_view_ui import ScanlistInfoFrame, PrimaryActionButton, ScanlistListWidget, AcquiredSeriesViewer2D, DropAcquiredSeriesViewer2D, ExamCardTab
#from views.main_view_ui import ImageLabel
#from views.styled_widgets import SecondaryActionButton, PrimaryActionButton, HeaderLabel

class ViewWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Viewing Mode")

        self.setGeometry(800, 300, 800, 600)
        #self.showMaximized()

        # initialize horizontal layout 
        main_layout = QHBoxLayout()

        # vertical layout for the left side
        left_layout = QVBoxLayout()

        #planning view button
        self.Button = QPushButton("Planning View",self)
        left_layout.addWidget(self.Button, stretch=2)
        self.Button.clicked.connect(self.exitViewingMode)

        #example data for the list
        test_data = ["Item 1", "Item 2", "Item 3"]
        self.model = QStringListModel(test_data)

        #list of acquired images
        left_layout.addWidget(QLabel("Acquired Images"))
        self._acquiredlistView = AcquiredList()
        left_layout.addWidget(self._acquiredlistView, stretch=2)

        #populate list with the data
        self.acquiredlistView.acquiredlistView.setModel(self.model)
      
        # widget for the left side 
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        #
        emptyCellStyle = """
        background-color: black;
        border: 1px solid white;
        """
   
        # creates default 2x2 grid
        right_layout = QGridLayout()
        for i in range(2):
            for j in range(2):
                empty_widget = QWidget()
                #empty_widget = DropWidget()
                empty_widget.setStyleSheet(emptyCellStyle)
                right_layout.addWidget(empty_widget, i, j)

        # widget for the right side
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # combine left and right into the horizontal layout
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(right_widget, stretch=3)

        self.setLayout(main_layout)

    def exitViewingMode(self):
        QDialog.close(self)
    
    @property
    def acquiredlistView(self):
        return self._acquiredlistView

class AcquiredList(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._acquiredlistView = QListView()
        self._acquiredlistView.setDragDropMode(QListView.DragOnly)
        self._acquiredlistView.setSelectionMode(QListView.SingleSelection)

        def dragMoveEvent(self, e: QDragMoveEvent) -> None:
            e.accept()

        #self._acquiredlistView.setEditTriggers(QListView.NoEditTriggers) #This is a flag provided by PyQt, which is used to specify that no editing actions should trigger item editing in the list view. It essentially disables editing for the list view, preventing users from directly editing the items displayed in the list.
        self.layout.addWidget(self._acquiredlistView)
    
    @property
    def acquiredlistView(self):
        return self._acquiredlistView
        
"""
class ModelViewLabel(ImageLabel):

    mouse_moved_signal = pyqtSignal(int, int, int) 

    def __init__(self):
        super().__init__()

    # override mouseMoveEvent
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.pixmap_item.isUnderMouse():
            coordinate_in_pixmap = self.pixmap_item.mapFromScene(self.mapToScene(event.pos()))
            # convert to model coordinates
            self.mouse_moved_signal.emit(int(abs(coordinate_in_pixmap.y())), int(abs(coordinate_in_pixmap.x())), self.current_slice)
        else:
            self.mouse_moved_signal.emit(-1, -1, -1) # signal that mouse is not over the pixmap

    def update_text_item(self):
        # set text
        text = f"Slice: {self.current_slice + 1}/{self.array.shape[2]}"
        self.text_item.setPlainText(text) # setPlainText() sets the text of the text item to the specified text.

        # set position of text
        pixmap_rect = self.pixmap_item.boundingRect() # boundingRect() returns the bounding rectangle of the pixmap item in the pixmap's local coordinates.
        # set position of text to the bottom right corner of the pixmap
        text_rect = self.text_item.boundingRect() # boundingRect() returns the bounding rectangle of the text item in the text item's local coordinates.
        x = pixmap_rect.right() - text_rect.width() - 15 # Adjusted to the right by 10 pixels for padding
        y = pixmap_rect.bottom() - text_rect.height() - 5 # Adjusted to the bottom by 10 pixels for padding
        self.text_item.setPos(x, y) # setPos() sets the position of the text item in the parent item's (i.e., the pixmap's) coordinates.

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if self.pixmap_item.isUnderMouse():
            # get current mouse position
            mouse_position = event.pos()
            # get the position of the mouse in the pixmap item
            coordinate_in_pixmap = self.pixmap_item.mapFromScene(self.mapToScene(mouse_position))
            # convert to model coordinates
            self.mouse_moved_signal.emit(int(abs(coordinate_in_pixmap.y())), int(abs(coordinate_in_pixmap.x())), self.current_slice)
        else:
            self.mouse_moved_signal.emit(-1, -1, -1) # signal that mouse is not over the pixmap

class ViewModelDialog(QDialog):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("View Model")
            
        self.layout = QVBoxLayout()

        self.model = model
        self.map = self.model.T1map_msec[:,:,:]
 

        # make practice 10x10x10 array with random values
        #self.map = np.random.rand(10,10,10)

        self.select_label = QLabel("Select tissue property map")
        self.layout.addWidget(self.select_label)
        self.createButtons()

    

        self.image_label = ModelViewLabel()
        self.layout.addWidget(self.image_label)
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

        #self.createSlider() 

        self.createInformationLabels()

        self.setLayout(self.layout)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.tissue_property_label.setText("T1 relaxation time")
        self.unit_label.setText("milliseconds")
        
        self.image_label.mouse_moved_signal.connect(self.handleMouseMoved)
    
        self.T1Button.set_highlighted(True)
        self.activeButton = self.T1Button

        self.setMouseTracking(True)

    def handleMouseMoved(self, x, y, z):
        if x == -1 and y == -1 and z == -1:
            self.tissue_property_value_display.setText("")
        else:
            self.tissue_property_value_display.setText(str(round(self.map[x,y,z],2)))

    def createButtons(self):
        buttonsLayout = QHBoxLayout()
        self.T1Button = PrimaryActionButton("T1 relaxation time")
        self.T2Button = PrimaryActionButton("T2 relaxation time")
        if self.model.T2smap_msec is not None:
            self.T2sButton = PrimaryActionButton("T2* relaxation time")
            self.T2sButton.clicked.connect(self.T2sButtonPressed)
        self.PDButton = PrimaryActionButton("Proton density")
        self.T1Button.clicked.connect(self.T1ButtonPressed)
        self.T2Button.clicked.connect(self.T2ButtonPressed)
        self.PDButton.clicked.connect(self.PDButtonPressed)
        buttonsLayout.addWidget(self.T1Button)
        buttonsLayout.addWidget(self.T2Button)
        if self.model.T2smap_msec is not None:
            buttonsLayout.addWidget(self.T2sButton)
        buttonsLayout.addWidget(self.PDButton)
        self.layout.addLayout(buttonsLayout)

    def createSlider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(self.map.shape[2]-1)
        slider.setValue(self.slice)
        slider.sliderMoved.connect(self.handleSliderMoved)
        self.layout.addWidget(slider)

    def createInformationLabels(self):
        self.information_label_layout = QGridLayout()
        self.tissue_property_label = QLabel()
        self.tissue_property_value_display = QLineEdit()
        self.tissue_property_value_display.setStyleSheet("QLineEdit { border: 1px solid  #BFBFBF; }")
        self.tissue_property_value_display.setReadOnly(True)
        self.tissue_property_value_display.setFixedWidth(200)
        self.tissue_property_value_display.setFixedHeight(30)
        self.unit_label = HeaderLabel("") 
        self.information_label_layout.addWidget(self.tissue_property_label, 0, 0)
        self.information_label_layout.addWidget(self.tissue_property_value_display, 1, 0)
        self.information_label_layout.addWidget(self.unit_label, 1, 1) 
        self.layout.addLayout(self.information_label_layout)

    def handleSliderMoved(self,position):
        self.slice = self.sender().value()
        self.image_array = self.map[:,:,self.slice]
        self.setPixmap(self.image_array)

    def T1ButtonPressed(self):
        self.map = self.model.T1map_msec[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()
        self.tissue_property_label.setText("T1 relaxation time")
        self.unit_label.setText("milliseconds")
        self.setActiveButton(self.T1Button)

    def T2ButtonPressed(self):
        self.map = self.model.T2map_msec[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()
        self.tissue_property_label.setText("T2 relaxation time")
        self.unit_label.setText("milliseconds")
        self.setActiveButton(self.T2Button)

    def PDButtonPressed(self):
        self.map = self.model.PDmap[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()
        self.tissue_property_label.setText("Proton density")
        self.unit_label.setText("")
        self.setActiveButton(self.PDButton)

    def T2sButtonPressed(self):
        self.map = self.model.T2smap_msec[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()
        self.tissue_property_label.setText("T2* relaxation time")
        self.unit_label.setText("milliseconds")
        self.setActiveButton(self.T2sButton)

    def setActiveButton(self, button):
        self.activeButton.set_highlighted(False)
        button.set_highlighted(True)
        self.activeButton = button

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
            self.tissue_property_value_display.setText("")
"""
