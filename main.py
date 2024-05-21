import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from simulator.scanner import Scanner
from controllers.main_ctrl import MainController
from views.main_view_ui import Ui_MainWindow

SCANNER_NAME = "test"
SCANNER_FIELD_STRENGTH = 3

class App(QApplication):
    '''Main application class.'''
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.scanner = Scanner(SCANNER_NAME, SCANNER_FIELD_STRENGTH)
        self.main_view = Ui_MainWindow(self.scanner)
        self.main_view.show()
        self.main_controller = MainController(self.scanner, self.main_view)

def main():
    app = App(sys.argv)
    default_font =  QFont("Segoe UI", 11)
    # change weight of font
    default_font.setWeight(55)
    app.setFont(default_font)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()