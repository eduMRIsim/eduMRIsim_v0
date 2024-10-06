from PyQt5.QtWidgets import QDialog, QPushButton, QFileDialog, QVBoxLayout
from utils.logger import log
from controllers.settings_mgr import SettingsManager


class LoadExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load examination")

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose INI File",
            "",
            "INI Files (*.ini);;All Files (*)",
            options=options,
        )
        if file_name:
            log.info(f"Selected file: {file_name}")

        settings_manager = SettingsManager.get_instance()
        settings_manager.setup_settings(file_name)
