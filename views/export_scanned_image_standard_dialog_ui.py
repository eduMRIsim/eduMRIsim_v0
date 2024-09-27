import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QDialog, QFileDialog


class ExportScannedImageStandardDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choose a file location")

    def export_file_dialog(self, image_data: np.ndarray | None):
        if image_data is None:
            raise ValueError("At least one scan should be performed before trying to export an image")

        max_val: float = np.max(image_data)
        min_val: float = np.min(image_data)
        image_data_normalized = ((image_data - min_val) / (max_val - min_val)) * 255.0
        image_data_normalized = image_data_normalized.astype(np.uint8)

        # Convert the NumPy array to a grayscale image
        image = Image.fromarray(image_data_normalized, mode="L")

        # Open a file dialog to select the save location
        options = QFileDialog.Options()

        file_name: str
        selected_filter: str
        file_name, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export to Standard Image",
            filter="JPEG Files (*.jpeg);;PNG Files (*.png)",
            options=options
        )
        if file_name:
            if selected_filter == "JPEG Files (*.jpeg)":
                image.save(file_name, filter="jpeg")
            elif selected_filter == "PNG Files (*.png)":
                image.save(file_name, filter="png")
            else:
                raise ValueError(f"Unknown file format filter selected: {selected_filter}")