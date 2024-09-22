from PyQt5.QtWidgets import QDialog, QPushButton, QFileDialog, QVBoxLayout

from controllers.settings_mgr import SettingsManager


class LoadExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load examination")

        # # Create a button to open the file picker
        # self.open_file_button = QPushButton("Choose INI File", self)
        # self.open_file_button.clicked.connect(self.open_file_dialog)
        #
        # # Set up the layout
        # layout = QVBoxLayout()
        # layout.addWidget(self.open_file_button)
        # self.setLayout(layout)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose INI File", "", "INI Files (*.ini);;All Files (*)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")

        settings_manager = SettingsManager.get_instance()
        settings_manager.setup_settings(file_name)
