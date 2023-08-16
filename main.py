# this module provides the exit() function which we need to cleanly terminate the app
import sys 
from PyQt5.QtWidgets import (
    QApplication
)

from view import MainWindow

# having a main() function like this is best practice in Python. This function provides the apps entry point.         
def main():
    
    # creates QApplication object
    eduMRIsimApp = QApplication([])

    
    # creates instance of app's window and shows GUI
    eduMRIsimWindow = MainWindow()
    
    # Set the QSS stylesheet
    with open("stylesheet_eduMRIsim.qss", "r") as f:
        style_sheet = f.read()
    eduMRIsimWindow.setStyleSheet(style_sheet)
    
    eduMRIsimWindow.show()
    
    # runs application's event loop with .exec() 
    sys.exit(eduMRIsimApp.exec())
    
if __name__ == "__main__": 
    main()