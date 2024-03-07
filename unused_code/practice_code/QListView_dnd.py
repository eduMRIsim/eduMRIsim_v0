from PyQt5.QtWidgets import QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QAbstractItemView
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QDrag
from PyQt5.QtCore import Qt

class DraggableListView(QListView):
    def __init__(self, name, drop_callback, parent=None):
        super().__init__(parent)
        self.name = name
        self.drop_callback = drop_callback

        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        # Set up model
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def startDrag(self, supportedActions):
        indexes = self.selectedIndexes()
        if indexes:
            mimeData = self.model.mimeData(indexes)
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.source() != self:  # Check if the drop is from another list
            source_index = event.source().indexAt(event.source().mapFromGlobal(event.pos()))
            data_item = event.source().model.itemFromIndex(source_index)
            data = data_item.data(Qt.UserRole)  # Retrieve data associated with the item
            self.drop_callback(data)

class DragAndDropExample(QMainWindow):
    def __init__(self):
        super().__init__()

        source_list = DraggableListView("Source", self.handle_drop, self)

        # Example dictionary of dictionaries
        data = {
            'key1': {'name': 'John', 'age': 25},
            'key2': {'name': 'Alice', 'age': 30},
            'key3': {'name': 'Bob', 'age': 22}
        }

        for key, value in data.items():
            item = QStandardItem(key) # Use the key as the associated text
            item.setData(value, Qt.UserRole) # Store the entire dictionary as data
            source_list.model.appendRow(item)

        target_list = DraggableListView("Target", self.handle_drop, self)

        layout = QVBoxLayout()
        layout.addWidget(source_list)
        layout.addWidget(target_list)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_drop(self, data):
        print(f"Item dropped: {data}")

if __name__ == "__main__":
    app = QApplication([])
    window = DragAndDropExample()
    window.show()
    app.exec_()
