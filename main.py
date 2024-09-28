import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from controllers.main_ctrl import MainController
from controllers.settings_mgr import SettingsManager
from events import EventEnum
from simulator.load import load_json
from simulator.scanner import Scanner
from views.main_view_ui import Ui_MainWindow
from PyQt5.QtCore import QSettings
from views.menu_bar import MenuBar


class App(QApplication):
    '''Main application class.'''

    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        # Create a Scanner object. The Scanner object is responsible for scanning anatomical model data with the given scan parameters and returning an acquired image series. The scanner keeps track of the current active examination, scanlist, active scan item and holds a reference to the anatomical model. 
        self.scanner = Scanner()

        # Setup UI
        self.main_view = Ui_MainWindow(self.scanner)

        self.setup_scan_parameter_form()
        self.main_view.update_UI()
        self.main_view.show()

        # Create a MainController object. The MainController object is responsible for connecting the UI with the scanner functionalities.
        self.main_controller = MainController(self.scanner, self.main_view)

        # Create a SettingsManager object. The SettingsManager object is responsible for saving and loading the application state.
        self.settings_manager = SettingsManager(self.scanner, self.main_controller, self.main_view, "settings.ini")
        self.settings_manager.setup_settings(None)
        
        # Create menu bar
        self.menu_bar = MenuBar(self.main_view)
        self.setup_menu_bar()
        
    # Set up the menu bar
    def setup_menu_bar(self):
        self.menu_bar.add_section('Session')
        self.menu_bar.add_action('Session', 'Save session', self.main_controller.export_examination)
        self.menu_bar.add_action('Session', 'Load session', self.test_action)

        self.menu_bar.add_section('Mode')
        self.menu_bar.add_action('Mode', 'Scanning Mode', self.test_action)
        self.menu_bar.add_action('Mode', 'Viewing Mode', self.test_action)
        
        self.menu_bar.add_section('Tools')
        self.menu_bar.add_action('Tools', 'Measure Distance', self.test_action)
        self.menu_bar.add_action('Tools', 'Measure Area', self.test_action)
        
        
    def test_action(self):
        # print("Action test")
        pass

    def setup_scan_parameter_form(self):
        # Load the scan parameters from the .json file. This file defines for each scan parameter which QWidget editor should be used to edit it. It also defines the default values for each parameter, the parameter's name, description and units.         
        parameters = load_json("scan_parameters/scan_parameters.json")

        # Scan parameters are passed to the parameter form layout so that it can create the appropriate QWidget editors for each scan parameter.
        self.main_view.parameterFormLayout.createForm(parameters)


def main():
    app = App(sys.argv)

    # Set the default font for the application
    default_font = QFont("Segoe UI", 11)
    default_font.setWeight(55)
    app.setFont(default_font)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
