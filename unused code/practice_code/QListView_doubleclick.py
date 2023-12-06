from PyQt5.QtWidgets import QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class DataTargetList:
    def __init__(self):
        self._data_list = []

    @property
    def data_list(self):
        return self._data_list

    def add_item(self, item):
        self._data_list.append(item)

    def remove_item(self, index):
        del self._data_list[index]

    def move_item(self, from_index, to_index):
        item = self._data_list.pop(from_index)
        self._data_list.insert(to_index, item)

class ListExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dataTargetList = DataTargetList()

        self.source_list = QListView(self)
        self.source_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.source_list.doubleClicked.connect(self.add_to_target)

        # Example list of items
        source_items = ['Item 1', 'Item 2', 'Item 3']

        source_model = self.create_list_model(source_items)
        self.source_list.setModel(source_model)

        self.target_list = QListView(self)
        self.target_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.target_list.setModel(QStandardItemModel())

        layout = QVBoxLayout()
        layout.addWidget(self.source_list)
        layout.addWidget(self.target_list)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_list_model(self, items):
        model = QStandardItemModel()
        for item_text in items:
            item = QStandardItem(item_text)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            model.appendRow(item)
        return model

    def add_to_target(self, index):
        item_text = self.source_list.model().itemFromIndex(index).text()
        self.dataTargetList.add_item(item_text)
        self.target_list.model().appendRow(QStandardItem(item_text))

if __name__ == "__main__":
    app = QApplication([])
    window = ListExample()
    window.show()
    app.exec_()
