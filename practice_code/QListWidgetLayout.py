import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QPushButton, QListWidgetItem, QLabel

class CustomItem(QWidget):
    def __init__(self, text):
        super().__init__()

        self.button = QPushButton("Click Me")
        self.label = QLabel(text)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list_widget = QListWidget()

        # Add custom items to the QListWidget
        for i in range(5):
            item = QListWidgetItem(self.list_widget)
            custom_item = CustomItem(f"Item {i}")
            item.setSizeHint(custom_item.sizeHint())
            self.list_widget.setItemWidget(item, custom_item)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QListWidget with Button Example')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())