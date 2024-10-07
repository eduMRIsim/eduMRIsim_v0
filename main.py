import argparse
import sys
from rich.traceback import install
from PyQt5.QtCore import qInstallMessageHandler
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from utils.logger import log, qt_message_handler, numpy_handler
from controllers.main_ctrl import MainController
from controllers.settings_mgr import SettingsManager
from events import EventEnum
from simulator.load import load_json
from simulator.scanner import Scanner
from views.main_view_ui import Ui_MainWindow
from views.menu_bar import MenuBar
from views.starting_window import StartingWindow  # Import the StartingWindow
from views.load_examination_dialog_ui import (
    LoadExaminationDialog,
)  # Import the LoadExaminationDialog


class App(QApplication):
    """Main application class."""

    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        self.scanner = Scanner()
        self.main_view = Ui_MainWindow(self.scanner)

        self.setup_scan_parameter_form()
        self.main_view.update_UI()

        self.main_controller = MainController(self.scanner, self.main_view)

        # Initialize the settings manager
        self.settings_manager = SettingsManager(
            scanner=self.scanner,
            main_ctrl=self.main_controller,
            main_view=self.main_view,
            file_name="settings.ini",
        )

        # Show the starting screen
        self.starting_window = StartingWindow(
            self.start_new_examination, self.load_examination
        )

        if not self.settings_manager.is_previous_session():
            self.starting_window.load_previous_examination_button.setDisabled(True)
        self.starting_window.show()

    def start_main_app(self, settings_file=None):
        """Start the main application."""
        self.main_view.update_UI()
        self.main_view.show()

        self.menu_bar = MenuBar(self.main_view)
        self.setup_menu_bar()

    def start_new_examination(self):
        """Start a new examination."""
        self.starting_window.close()
        self.main_controller.handle_newExaminationButton_clicked()
        self.start_main_app()

    def load_examination(self):
        """Load an existing examination from a file."""
        self.starting_window.close()
        self.start_main_app()
        self.load_dialog = LoadExaminationDialog()
        self.load_dialog.open_file_dialog()

    # TODO all menu bar actions should be moved to the MenuBar class
    # Set up the menu bar
    def setup_menu_bar(self):
        # Create the menu bar and sections
        menu_bar = self.menu_bar

        # Session section
        session_section = menu_bar.add_section('Session')
        session_section.add_action('Save session', self.main_controller.export_examination)
        session_section.add_action('Load session', self.load_examination)

        # Mode section
        mode_section = menu_bar.add_section('Mode')
        mode_section.add_mode_action_group()
        mode_section.add_mode_action('Scanning Mode', lambda: self.main_view._stackedLayout.setCurrentIndex(0),
                                     checked=True)
        mode_section.add_mode_action('Viewing Mode', lambda: self.main_view._stackedLayout.setCurrentIndex(1))

        # Tools section
        tools_section = menu_bar.add_section('Tools')
        tools_section.add_action('Measure Distance', self.test_action)
        tools_section.add_action('Measure Area', self.test_action)

    def test_action(self):
        pass

    def measure_distance(self):
        self.main_controller.handle_measureDistanceButtonClicked()

    def setup_scan_parameter_form(self):
        """Load and set up the scan parameter form."""
        parameters = load_json("scan_parameters/scan_parameters.json")
        self.main_view.parameterFormLayout.createForm(parameters)


def main():
    """Main entry point for the application."""
    # Enable rich traceback
    install(show_locals=True)

    # Add support for --log-level command line argument
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Set the logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    args = parser.parse_args()

    # Set the log level
    log.setLevel(args.log_level)

    # Connect Qt messages to the logging module
    qInstallMessageHandler(qt_message_handler)
    numpy_handler()

    app = App(sys.argv)

    # Set the default font for the application
    default_font = QFont("Segoe UI", 11)
    default_font.setWeight(55)
    app.setFont(default_font)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
