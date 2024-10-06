from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class StartingWindow(QWidget):
    def __init__(self, start_callback):
        super(StartingWindow, self).__init__()
        layout = QVBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(start_callback)

        layout.addWidget(self.start_button)

        self.setLayout(layout)

        self.setWindowTitle("Starting Screen")
        self.resize(300, 200)
