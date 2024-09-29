import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QDialog, QFileDialog


class ExportScannedImageStandardDialog(QDialog):
    """
    This class represents a dialog to export acquired images to standard image files, such as JPEG, PNG.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choose a file location")

    def export_file_dialog(self, image_data: np.ndarray | None) -> None:
        """
        This method exports acquired image data to a standard image file through a file save dialog.
        """

        if image_data is None:
            raise ValueError("At least one scan should be performed before trying to export an image")

        # Normalize the image data array by scaling it down to a floating point value in range [0.0, 1.0]
        # and multiplying by 255.0.
        # Also, set the type of the normalized data array to np.uint8.
        max_val: float = np.max(image_data)
        min_val: float = np.min(image_data)
        image_data_normalized = ((image_data - min_val) / (max_val - min_val)) * 255.0
        image_data_normalized = image_data_normalized.astype(np.uint8)

        # Convert the normalized image data to a grayscale image.
        # The mode, "L", is for 8-bit pixels, grayscale.
        # This may be something to change in the future if we want different color scales.
        image = Image.fromarray(image_data_normalized, mode="L")

        # Open a save file dialog so that the user can save the image.
        options = QFileDialog.Options()
        file_name: str
        selected_filter: str
        file_name, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export to Standard Image",
            filter="JPEG Files (*.jpeg);;PNG Files (*.png)",
            options=options
        )

        # If the user specified a file name, save the image in that file name and using the filter that they selected.
        if file_name:
            if selected_filter == "JPEG Files (*.jpeg)":
                image.save(file_name, filter="jpeg")
            elif selected_filter == "PNG Files (*.png)":
                image.save(file_name, filter="png")
            else:
                raise ValueError(f"Unknown file format filter selected: {selected_filter}")