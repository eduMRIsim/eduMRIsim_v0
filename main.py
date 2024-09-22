import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from events import EventEnum
from simulator.scanner import Scanner
from controllers.main_ctrl import MainController
from views.main_view_ui import Ui_MainWindow
from simulator.load import load_json
from PyQt5.QtCore import QSettings


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

        settings = QSettings("Eindhoven University of Technology", "eduMRIsim")
        state_name = settings.value("currentState", type=str)
        exam_name = settings.value("exam_name", type=str)
        model_name = settings.value("model_name", type=str)

        if state_name == "ScanCompleteState" or state_name == "ReadyToScanState":
            self.main_controller.prepare_model_data()
            self.main_controller.handle_newExaminationOkButton_clicked(exam_name, model_name)
            scannerState = settings.value("scannerState", type=dict)
            scan_list_items = scannerState.get("scanlist")
            scan_list_params = scannerState.get("params")
            scan_list_status = scannerState.get("status")
            scan_list_data = scannerState.get("data")

            if scan_list_items is not None:
                for i in range(len(scan_list_items)):
                    self.scanner.scanlist.add_scanlist_element(scan_list_items[i], scan_list_params[i])
                    self.main_controller.update(EventEnum.SCANLIST_ITEM_ADDED)
                    self.scanner.scanlist.notify_observers(EventEnum.SCANLIST_ITEM_ADDED)

                    # if scan_list_data[i] is not None:
                    self.scanner.scanlist.scanlist_elements[i].acquired_data = scan_list_data[i]
                    self.scanner.scanlist.scanlist_elements[i].scan_item.status = scan_list_status[i]
                    self.main_controller.update(EventEnum.SCAN_ITEM_STATUS_CHANGED)
                    self.scanner.scanlist.notify_observers(EventEnum.SCAN_ITEM_STATUS_CHANGED)

                    self.main_controller.update_scanlistListWidget(self.scanner.scanlist)

        self.main_view.restore_settings()


    def setup_scan_parameter_form(self):
        # Load the scan parameters from the .json file. This file defines for each scan parameter which QWidget editor should be used to edit it. It also defines the default values for each parameter, the parameter's name, description and units.         
        parameters = load_json("scan_parameters/scan_parameters.json")

        # Scan parameters are passed to the parameter form layout so that it can create the appropriate QWidget editors for each scan parameter.
        self.main_view.parameterFormLayout.createForm(parameters)


def main():
    app = App(sys.argv)

    # Set the default font for the application
    default_font =  QFont("Segoe UI", 11)
    default_font.setWeight(55)
    app.setFont(default_font)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()