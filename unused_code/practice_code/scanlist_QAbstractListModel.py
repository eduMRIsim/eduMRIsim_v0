from PyQt5.QtWidgets import QListView, QApplication, QWidget, QHBoxLayout, QAbstractItemView
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtGui import QDragEnterEvent, QStandardItemModel, QStandardItem

class DictionaryModel(QStandardItemModel):
    def __init__(self, data):
        super().__init__()

        self.data = data
        self.populate_model()

    def populate_model(self):
        for key in self.data.keys():
            item = QStandardItem(key)
            self.appendRow(item)

    def get_data(self, index):
        key = self.itemFromIndex(index).text()
        return self.data[key]
    
    def add_item(self, key, value):
        self.data[key] = value
        item = QStandardItem(key)
        self.appendRow(item)

class ScanItem:
    def __init__(self, name, value1, value2, value3):
        self.name = name
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3

class Scanlist:
    def __init__(self):
        self.scan_items = []
        self.observers = []

    def add_scan_item(self, scan_item : ScanItem):
        self.scan_items.append(scan_item)
        for item in self.scan_items:
            print(item.name)
        for observer in self.observers:
            observer.update()

    def add_observer(self, observer):
        self.observers.append(observer)

class ScanlistModel(QAbstractListModel):
    def __init__(self, scanlist, parent=None):
        super().__init__(parent)
        self.scanlist = scanlist

    def rowCount(self, parent=QModelIndex()):
        return len(self.scanlist.scan_items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            scan_item = self.scanlist.scan_items[index.row()]
            return scan_item.name
        return None

    def update(self):
        self.beginResetModel()
        self.endResetModel()

class SourceList(QListView):
    def __init__(self):
        super().__init__()
        self.setDragDropMode(self.DragOnly)
        self.setSelectionMode(self.ExtendedSelection)

class TargetList(QListView):
    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        print('drag entered')
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        print('dropped')
        widget = e.source()
        print(type(widget.selectedIndexes()))
        for index in widget.selectedIndexes():
            name = widget.model().itemFromIndex(index).text()
            data = widget.model().get_data(index)
            scan_item = ScanItem(name, data['Parameter 1'], data['Parameter 2'], data['Parameter 3'])
            self.model().scanlist.add_scan_item(scan_item)
        e.accept()

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.source_list = SourceList()
        self.target_list = TargetList()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.source_list)
        self.layout.addWidget(self.target_list)
        self.setLayout(self.layout)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = Window()
    w.show()

    exam_card_data = {"Card 1": {"Parameter 1": "Value 1", "Parameter 2": "Value 2", "Parameter 3": "Value 3"}, "Card 2": {"Parameter 1": "Value 1", "Parameter 2": "Value 2", "Parameter 3": "Value 3"}, "Card 3": {"Parameter 1": "Value 1", "Parameter 2": "Value 2", "Parameter 3": "Value 3"}}
    exam_card_model = DictionaryModel(exam_card_data)
    w.source_list.setModel(exam_card_model)
    scanlist = Scanlist()
    scanlist_model = ScanlistModel(scanlist)
    w.target_list.setModel(scanlist_model)
    scanlist.add_observer(scanlist_model)
    print("test")
    for item in scanlist.scan_items:
        print(item.name)

    sys.exit(app.exec_())

