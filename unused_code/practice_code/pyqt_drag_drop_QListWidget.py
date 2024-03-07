from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QHBoxLayout, QWidget, QApplication, QAbstractItemView
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

""" class DragListItem(QListWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()

            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction) """
class SourceList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)


class TargetList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.DropOnly)

    
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.source_list = SourceList()
        self.target_list = TargetList()
        for l in ['A', 'B', 'C', 'D']:
            item = QListWidgetItem(l)
            self.source_list.addItem(item)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.source_list)
        self.layout.addWidget(self.target_list)
        self.setLayout(self.layout)

app = QApplication([])
w = Window()
w.show()
app.exec_()

