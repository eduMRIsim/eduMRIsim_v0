from PyQt5.QtWidgets import QApplication, QHBoxLayout, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

class DragButton(QPushButton):
    def __init__(self, text, data):
        super().__init__(text)
        self.data = data  # Store data associated with the button

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            # Set data to be transferred
            mime.setData('application/x-mybuttondata', bytes(str(self.data), encoding='utf-8'))
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)

class ButtonDataLabel(QLabel):
    def __init__(self):
        super().__init__()  
        self.setAcceptDrops(True)
        self.setText("I will display button data")
    
    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        mime = e.mimeData()
        # Check if the dropped data has the expected format
        if mime.hasFormat('application/x-mybuttondata'):
            # Retrieve the button data from the MIME data
            data = str(mime.data('application/x-mybuttondata'), encoding='utf-8')
            # Update the label text with the button data
            self.setText(data)
            e.accept()
        else:
            e.ignore()

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout()
        self.blayout = QHBoxLayout()
        for l, data in [('A', 'I am button A'), ('B', 'I am button B'), ('C', 'I am button C'), ('D', 'I am button D')]:  # Example data associated with buttons
            btn = DragButton(l, data)
            self.blayout.addWidget(btn)
        self.layout.addLayout(self.blayout)
        self.button_data_label = ButtonDataLabel()
        self.layout.addWidget(self.button_data_label)
        self.setLayout(self.layout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()

        for n in range(self.blayout.count()):
            w = self.blayout.itemAt(n).widget()
            if pos.x() < w.x() + w.size().width() // 2:
                self.blayout.insertWidget(n-1, widget)
                break

        e.accept()

if __name__ == '__main__':
    app = QApplication([])
    w = Window()
    w.show()
    app.exec_()