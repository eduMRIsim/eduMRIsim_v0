import sys
import numpy as np
from scipy.io import loadmat
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSlider, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class MRSTATViewer(QMainWindow):
    def __init__(self, PDf, T1f, T2f):
        super().__init__()
        self.PDf = PDf
        self.T1f = T1f
        self.T2f = T2f
        self.initUI()

    def initUI(self):
        self.data = {
            'TE': 0.1,
            'TR': 4.5,
            'TI': 0,
            'TI2': 0,
            'slice': 15
        }

        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Iteractive mode demo")

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)

        self.image = QImage(self.PDf.shape[1], self.PDf.shape[0], QImage.Format_Grayscale8)
        self.updateImage()

        self.sliderTE = QSlider(Qt.Horizontal)
        self.sliderTE.setRange(5, 200)
        self.sliderTE.setValue(int(self.data['TE'] * 1000))
        self.sliderTE.valueChanged.connect(self.changeTE)
        labelTE = QLabel('TE', self)
        self.layout.addWidget(labelTE)
        self.layout.addWidget(self.sliderTE)

        self.sliderTR = QSlider(Qt.Horizontal)
        self.sliderTR.setRange(100, 15000)
        self.sliderTR.setValue(int(self.data['TR'] * 1000))
        self.sliderTR.valueChanged.connect(self.changeTR)
        labelTR = QLabel('TR', self)
        self.layout.addWidget(labelTR)
        self.layout.addWidget(self.sliderTR)

        self.sliderTI = QSlider(Qt.Horizontal)
        self.sliderTI.setRange(0, 5000)
        self.sliderTI.setValue(int(self.data['TI'] * 1000))
        self.sliderTI.valueChanged.connect(self.changeTI)
        labelTI = QLabel('TI', self)
        self.layout.addWidget(labelTI)
        self.layout.addWidget(self.sliderTI)

        self.sliderSlice = QSlider(Qt.Horizontal)
        self.sliderSlice.setRange(1, 30)
        self.sliderSlice.setValue(self.data['slice'])
        labelSlice = QLabel('Slice', self)
        self.layout.addWidget(labelSlice)
        self.sliderSlice.valueChanged.connect(self.changeSlice)
        self.layout.addWidget(self.sliderSlice)

        self.buttons = {
            'PDw': (0.020, 2.800, 0, 0),
            'T1w': (0.014, 0.864, 0, 0),
            'T2w': (0.080, 3.254, 0, 0),
            'FLAIR': (0.120, 10, 2.8, 0)
        }

        for text, params in self.buttons.items():
            button = QPushButton(text, self)
            button.clicked.connect(lambda _, p=params: self.changeContrast(*p))
            self.layout.addWidget(button)

    def updateImage(self):
        TE = self.data['TE']
        TR = self.data['TR']
        TI = self.data['TI']
        TI2 = self.data['TI2']
        slice_idx = self.data['slice'] - 1

        PD = self.PDf[:, :, slice_idx]
        T1 = self.T1f[:, :, slice_idx]
        T2 = self.T2f[:, :, slice_idx]

        A = np.abs(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1))))
        A = ((A / np.max(A)) * 255).astype(np.uint8)
        A = np.ascontiguousarray(np.array(A))

        q_image = QImage(A.data, A.shape[1], A.shape[0], A.shape[1], QImage.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(q_image)

        # Increase the size of the QPixmap
        scale_factor = 2
        new_width = A.shape[1] * scale_factor  # Adjust scale_factor as needed
        new_height = A.shape[0] * scale_factor  # Adjust scale_factor as needed
        pixmap = pixmap.scaled(new_width, new_height)

        self.imageLabel.setPixmap(pixmap)

    def changeTE(self, value):
        self.data['TE'] = value / 1000
        self.updateImage()

    def changeTR(self, value):
        self.data['TR'] = value / 1000
        self.updateImage()

    def changeTI(self, value):
        self.data['TI'] = value / 1000
        self.updateImage()

    def changeSlice(self, value):
        self.data['slice'] = value
        self.updateImage()

    def changeContrast(self, TE, TR, TI, TI2):
        self.data['TE'] = TE
        self.data['TR'] = TR
        self.data['TI'] = TI
        self.data['TI2'] = TI2
        self.updateImage()

def main():
    app = QApplication(sys.argv)

    data = loadmat("models/BrainHighResolution.mat")

    print(type(data['VObj']))
    print(type(data['VObj'][0,0]))

    # Load your PDf, T1f, and T2f data here
    PDf = data['VObj'][0,0]['Rho'] #values [0,1]
    T1f = data['VObj'][0,0]['T1'] #values [0,4.5]
    T2f = data['VObj'][0,0]['T2'] #values [0,2.2]

    print(np.min(T2f))
    print(np.max(T2f))
    viewer = MRSTATViewer(PDf, T1f, T2f)
    viewer.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
