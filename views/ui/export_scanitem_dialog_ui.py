from PyQt6.QtWidgets import QDialog, QFileDialog

from utils.logger import log


class ExportScanItemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Export scan item")

    def open_file_dialog(self) -> str | None:
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Choose location to save scan item",
            "",
            "json (*.json);;All Files (*)",
        )
        if file_name is not None:
            log.info(f"ScanItem export location: {file_name}")
            return file_name
        else:
            log.error("No location selected")
            return None
