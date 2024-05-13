from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QDialog, QHBoxLayout, QPushButton, QLabel, QSlider, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
from views.main_view_ui import ImageLabel

class ViewModelDialog(QDialog):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("View Model")
            
        self.layout = QVBoxLayout()

        self.model = model
        self.map = self.model._T1map[:,:,:]
 
        self.image_label = ImageLabel()
        self.layout.addWidget(self.image_label)
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

        self.createButtons()
        #self.createSlider() 

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
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

    def T2ButtonPressed(self):
        self.map = self.model._T2map[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

    def PDButtonPressed(self):
        self.map = self.model._PDmap[:,:,:]
        self.image_label.setArray(self.map)
        self.image_label.displayArray()

