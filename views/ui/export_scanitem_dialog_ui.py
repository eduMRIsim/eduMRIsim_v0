import os

from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWidgets import QDialog, QFileDialog

from utils.logger import log


class ExportScanItemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Export scan item")

    def open_file_dialog(self, save=True) -> str | None:
        if save:
            self.setWindowTitle("Save scan item")
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Choose location to save scan item",
                os.path.join(
                    QStandardPaths.writableLocation(
                        QStandardPaths.StandardLocation.DocumentsLocation
                    ),
                    "eduMRIsim",
                    "scan_items",
                ),
                "json (*.json);;All Files (*)",
            )
        else:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Choose the scan item file",
                os.path.join(
                    QStandardPaths.writableLocation(
                        QStandardPaths.StandardLocation.DocumentsLocation
                    ),
                    "eduMRIsim",
                    "scan_items",
                ),
                "json (*.json);;All Files (*)",
            )
        if file_name is not None:
            log.info(f"ScanItem location: {file_name}")
            return file_name
        else:
            log.error("No location selected")
            return None
