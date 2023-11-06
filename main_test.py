import sys
from PyQt5.QtWidgets import QApplication
from scanner import Scanner
from controllers.main_ctrl import MainController
from views.main_view import MainView

SCANNER_NAME = "test"
SCANNER_FIELD_STRENGTH = 3

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.scanner = Scanner(SCANNER_NAME, SCANNER_FIELD_STRENGTH)
        self.main_controller = MainController(self.scanner)
        self.main_view = MainView(self.scanner, self.main_controller)
        self.main_view.show()


if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())