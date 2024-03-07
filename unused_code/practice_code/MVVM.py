from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

class Model:
    def __init__(self):
        self._counter = 0

    def get_counter(self):
        return self._counter

    def increment_counter(self):
        self._counter += 1

class ViewModel(QObject):
    counterChanged = pyqtSignal(int)

    def __init__(self, model):
        super().__init__()
        self._model = model

    @pyqtProperty(int, notify=counterChanged)
    def counter(self):
        return self._model.get_counter()

    @pyqtSlot()
    def incrementCounter(self):
        self._model.increment_counter()
        self.counterChanged.emit(self.counter)

class View(QWidget):
    def __init__(self, viewModel):
        super().__init__()
        self.viewModel = viewModel
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout()
        self.label = QLabel("Counter: 0")
        self.button = QPushButton("Increment")
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.button.clicked.connect(self.viewModel.incrementCounter)
        self.viewModel.counterChanged.connect(self.updateCounter)

    def updateCounter(self, value):
        self.label.setText(f"Counter: {value}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    model = Model()
    viewModel = ViewModel(model)
    view = View(viewModel)
    
    view.show()
    sys.exit(app.exec_())