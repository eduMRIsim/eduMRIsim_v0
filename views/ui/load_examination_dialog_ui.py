import os

from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWidgets import QDialog, QFileDialog

from controllers.settings_mgr import SettingsManager
from utils.logger import log


class LoadExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load examination")

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose INI File",
            os.path.join(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.DocumentsLocation
                ),
                "eduMRIsim",
                "sessions",
            ),
            "INI Files (*.ini);;All Files (*)",
        )
        if file_name:
            log.info(f"Selected file: {file_name}")

        settings_manager = SettingsManager.get_instance()
        settings_manager.setup_settings(file_name)
