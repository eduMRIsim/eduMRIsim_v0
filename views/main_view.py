from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot
from views.main_view_ui import Ui_MainWindow
from scanner import Scanner

SCANNER_NAME = "test"
SCANNER_FIELD_STRENGTH = 3

class MainView(QMainWindow):
    def __init__(self, model, main_controller):
        super().__init__()

        self._model = model
        self._main_controller = main_controller
        self._scanner = Scanner(SCANNER_NAME, SCANNER_FIELD_STRENGTH)
        self._ui = Ui_MainWindow(self._scanner, self)
