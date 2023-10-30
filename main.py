# this module provides the exit() function which we need to cleanly terminate the app
import sys 
from PyQt5.QtWidgets import (
    QApplication
)

from view import MainWindow
from controller import Controller
from scanner import Scanner

SCANNER_NAME = "test"
SCANNER_FIELD_STRENGTH = 3

# having a main() function like this is best practice in Python. This function provides the apps entry point.         
def main():
    
    # creates QApplication object
    eduMRIsimApp = QApplication([])

    scanner = Scanner(SCANNER_NAME,SCANNER_FIELD_STRENGTH)

    # creates instance of app's window and shows GUI
    eduMRIsimWindow = MainWindow(scanner)
    
    # Set the QSS stylesheet
    with open("stylesheet_eduMRIsim.qss", "r") as f:
        style_sheet = f.read()
    eduMRIsimWindow.setStyleSheet(style_sheet)
    
    eduMRIsimWindow.show()

    controller = Controller(eduMRIsimWindow, scanner)
    
    # runs application's event loop with .exec() 
    sys.exit(eduMRIsimApp.exec())
    
if __name__ == "__main__": 
    main()