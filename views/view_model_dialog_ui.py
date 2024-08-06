from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import  QDialog, QHBoxLayout, QPushButton, QLabel, QSlider, QVBoxLayout
from PyQt5.QtGui import QMouseEvent, QPixmap, QImage
import numpy as np
from views.main_view_ui import ImageLabel

class ModelViewLabel(ImageLabel):
    def __init__(self):
        super().__init__()
        self.mouse_moved_signal = pyqtSignal(int, int, int)


    # override mouseMoveEvent
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # if mouse move event happens over pixmap item print coordinates in pixmap item coordinates
        if self.pixmap_item.isUnderMouse():
            #print("coordinates in pixmap item: ", self.pixmap_item.mapFromScene(self.mapToScene(event.pos())))
            coordinate_in_pixmap = self.pixmap_item.mapFromScene(self.mapToScene(event.pos()))
            # convert to model coordinates
            #print("coordinates in model: ", int(abs(coordinate_in_pixmap.y())), int(abs(coordinate_in_pixmap.x())), self.current_slice)
            #self.mouse_moved_signal.emit(int(abs(coordinate_in_pixmap.y())), int(abs(coordinate_in_pixmap.x())), self.current_slice)

class ViewModelDialog(QDialog):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("View Model")
            
        self.layout = QVBoxLayout()

        self.model = model
        self.map = self.model._T1map_ms[:,:,:]
 
        # make practice 10x10x10 array with random values
        #self.map = np.random.rand(10,10,10)


        self.image_label = ModelViewLabel()
        self.layout.addWidget(self.image_label)
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

        self.createButtons()
        #self.createSlider() 

        self.setLayout(self.layout)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        #self.image_label.mouse_moved_signal.connect(self.handleMouseMoved)
    
    def handleMouseMoved(self, x, y, z):
        print("underlying model value")
        print(self.map[x,y,z])

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
        self.map = self.model._T1map_ms[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

    def T2ButtonPressed(self):
        self.map = self.model._T2map_ms[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

    def PDButtonPressed(self):
        self.map = self.model._PDmap_ms[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()
