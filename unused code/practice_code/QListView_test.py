from PyQt5.QtWidgets import QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel


class MyModel(QStandardItemModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        for item in data:
            self.appendRow(QStandardItem(item))

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        data = ["Item 1", "Item 2", "Item 3"]

        # Using a custom model
        self.custom_model = MyModel(data)
        self.custom_list_view = QListView(self)
        self.custom_list_view.setModel(self.custom_model)
        self.custom_list_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.layout.addWidget(self.custom_list_view)

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
