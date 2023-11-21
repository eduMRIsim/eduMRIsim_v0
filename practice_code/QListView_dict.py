from PyQt5.QtWidgets import QApplication, QListView,QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

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

class CustomListView(QListView):
    def __init__(self, model):
        super().__init__()

        self.setModel(model)
        self.doubleClicked.connect(self.show_data)

    def show_data(self, index):
        data = self.model().get_data(index)
        self.show_data_popup(data)

    def show_data_popup(self, data):
        self.popup = QWidget()
        layout = QVBoxLayout()

        for key, value in data.items():
            label = QLabel(f"{key}: {value}")
            layout.addWidget(label)

        self.popup.setLayout(layout)
        self.popup.setWindowTitle("Data Details")
        self.popup.show()

if __name__ == "__main__":
    app = QApplication([])

    # Example dictionary of dictionaries
    data = {
        'key1': {'name': 'John', 'age': 25},
        'key2': {'name': 'Alice', 'age': 30},
        'key3': {'name': 'Bob', 'age': 22}
    }

    model = DictionaryModel(data)
    list_view = CustomListView(model)

    # Add a button to add a new item
    add_button = QPushButton("Add Item")
    add_button.clicked.connect(lambda: list_view.model().add_item("new_key", {'name': 'New Person', 'age': 21}))

    layout = QVBoxLayout()
    layout.addWidget(list_view)
    layout.addWidget(add_button)

    main_widget = QWidget()
    main_widget.setLayout(layout)
    main_widget.show()

    app.exec_()
