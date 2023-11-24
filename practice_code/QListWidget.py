import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QHBoxLayout


class ScanList:
    def __init__(self):
        self.scan_list = []


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.exam_card_data = {
            'Item1': {'property1': 'value1', 'property2': 'value2'},
            'Item2': {'property1': 'value3', 'property2': 'value4'},
            # Add more items as needed
        }

        self.initUI()

    def initUI(self):
        self.source_list = QListWidget()
        self.target_list = QListWidget()

        self.scan_list_instance = ScanList()

        self.load_source_list()

        self.source_list.itemDoubleClicked.connect(self.add_to_scan_list)

        vbox = QVBoxLayout()
        vbox.addWidget(self.source_list)
        vbox.addWidget(self.target_list)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Simple Python App with PyQt')
        self.show()

    def load_source_list(self):
        self.source_list.addItems(self.exam_card_data.keys())

    def add_to_scan_list(self, item):
        key = item.text()
        if key in self.exam_card_data:
            self.scan_list_instance.scan_list.append(self.exam_card_data[key])
            self.update_target_list()

    def update_target_list(self):
        self.target_list.clear()
        for item in self.scan_list_instance.scan_list:
            self.target_list.addItem(str(item))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
