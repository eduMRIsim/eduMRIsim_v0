import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QDialog, QFileDialog


class ExportScannedImageStandardDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choose a file location")

    def export_file_dialog(self):
        # Create a sample NumPy array with floating point values
        array = np.random.rand(100, 100) * 255  # Scale values to 0-255
        array = array.astype(np.uint8)  # Convert to unsigned 8-bit integer type

        # Convert the NumPy array to a grayscale image
        image = Image.fromarray(array, mode="L")

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
            file_format: str = ""
            if selected_filter == "JPEG Files (*.jpeg)":
                file_format = "jpeg"
            elif selected_filter == "PNG Files (*.png)":
                file_format = "png"
            else:
                raise ValueError(f"Unknown file format filter selected: {selected_filter}")
            image.save(file_name, filter=file_format)