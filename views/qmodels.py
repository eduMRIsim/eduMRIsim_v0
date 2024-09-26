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
