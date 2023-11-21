from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QDialog, QHBoxLayout, QPushButton, QLabel, QSlider, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

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
