import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QResizeEvent, QImage, QPixmap, QDragEnterEvent, QDragMoveEvent, \
    QDropEvent
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSizePolicy, QGraphicsTextItem

from utils.logger import log
from views.ui.scanlist_ui import ScanlistListWidget


class ImageLabel(QGraphicsView):
    """Old version of AcquiredSeriesViewer2D. This viewer is still used to display the anatomical model in the model viewing dialog."""

    def __init__(self):
        super().__init__()

        # QGraphicsScene is essentially a container that holds and manages the graphical items you want to display in your QGraphicsView. QGraphicsScene is a container and manager while QGraphicsView is responsible for actually displaying those items visually.
        self.scene = QGraphicsScene(self)

        # Creates a pixmap graphics item that will be added to the scene
        self.pixmap_item = QGraphicsPixmapItem()

        # Sets the created scene as the scene for the graphics view
        self.setScene(self.scene)

        # Sets the render hint to enable antialiasing, which makes the image look smoother. Aliasings occur when a high-resolution image is displayed or rendered at a lower resolution, leading to the loss of information and the appearance of stair-stepped edges. Antialiasing techniques smooth out these jagged edges by introducing intermediate colors or shades along the edges of objects.
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Set the background color to black
        self.setBackgroundBrush(QColor(0, 0, 0))  # RGB values for black

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Initialize array attribute to None
        self.array = None
        self._current_slice = None

        self._window_width = None
        self._window_level = None

        self.observers = []

        self.middle_mouse_button_pressed = False
        self._displaying = False

        self.scene.addItem(self.pixmap_item)

        self.text_item = QGraphicsTextItem(self.pixmap_item)
        # change text color to white
        self.text_item.setDefaultTextColor(Qt.GlobalColor.white)
        # set font size
        self.text_item.setFont(QFont("Arial", 5))

    @property
    def displaying(self):
        return self._displaying

    @displaying.setter
    def displaying(self, bool):
        if bool == True:
            self._displaying = True
        else:
            self._displaying = False
            self.array = None
            self.current_slice = None
            self.window_width = None
            self.window_level = None
            self.text_item.setPlainText("")

    @property
    def current_slice(self):
        return self._current_slice

    @current_slice.setter
    def current_slice(self, value):
        self._current_slice = value

    @property
    def window_width(self):
        return self._window_width

    @window_width.setter
    def window_width(self, value):
        self._window_width = value

    @property
    def window_level(self):
        return self._window_level

    @window_level.setter
    def window_level(self, value):
        self._window_level = value

    def set_window_width_level(self, window_width, window_level):
        self._window_width = window_width
        self._window_level = window_level
        self.notify_observers(window_width, window_level)

    # This method is called whenever the graphics view is resized. It ensures that the image is always scaled to fit the view.
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    # overriden method from QGraphicsView. QGraphicsView has inherited QWidget's wheelEvent method. QGraphicsView is a child of QWidget.
    def wheelEvent(self, event):
        # Check if the array is None
        if self.array is None:
            # Do nothing and return
            return

        delta = event.angleDelta().y()
        current_slice = getattr(self, "current_slice", 0)
        if delta > 0:
            new_slice = max(0, min(current_slice + 1, self.array.shape[2] - 1))
        elif delta < 0:
            new_slice = max(0, min(current_slice - 1, self.array.shape[2] - 1))
        elif delta == 0:
            new_slice = current_slice
        self.current_slice = int(new_slice)
        self.displayArray()

    # ImageLabel holds a copy of the array of MRI data to be displayed.
    def setArray(self, array):
        # Set the array and make current_slice the middle slice by default
        self.array = array
        if array is not None:
            self.displaying = True
            self.current_slice = array.shape[2] // 2
            window_width, window_level = self.calculate_window_width_level(
                method="percentile"
            )
            self.set_window_width_level(window_width, window_level)
        else:
            self.displaying = False

    def displayArray(self):
        width, height = 0, 0
        if self.displaying == True:
            windowed_array = self.apply_window_width_level()
            array_8bit = (windowed_array * 255).astype(np.uint8)

            # Convert the array to QImage for display. This is because you cannot directly set a QPixmap from a NumPy array. You need to convert the array to a QImage first.
            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(image.data, width, height, width, QImage.Format.Format_Grayscale8)

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

            self.update_text_item()

        else:
            # Set a black image when self.array is None
            black_image = QImage(1, 1, QImage.Format.Format_Grayscale8)
            black_image.fill(Qt.GlobalColor.black)
            pixmap = QPixmap.fromImage(black_image)
            self.pixmap_item.setPixmap(pixmap)
            #
            self.scene.setSceneRect(0, 0, 1, 1)

        # self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self.pixmap_item)

        # Adjust the scene rectangle and center the image.  The arguments (0, 0, width, height) specify the left, top, width, and height of the scene rectangle.
        # self.scene.setSceneRect(0, 0, width, height)
        # The centerOn method is used to center the view on a particular point within the scene.
        # self.centerOn(width / 2, height / 2)

    def update_text_item(self):
        # set text
        text = f"Slice: {self.current_slice + 1}/{self.array.shape[2]}\nWW: {self.window_width:.2f}\nWL: {self.window_level:.2f}"
        self.text_item.setPlainText(
            text
        )  # setPlainText() sets the text of the text item to the specified text.

        # set position of text
        pixmap_rect = (
            self.pixmap_item.boundingRect()
        )  # boundingRect() returns the bounding rectangle of the pixmap item in the pixmap's local coordinates.
        # set position of text to the bottom right corner of the pixmap
        text_rect = (
            self.text_item.boundingRect()
        )  # boundingRect() returns the bounding rectangle of the text item in the text item's local coordinates.
        x = (
            pixmap_rect.right() - text_rect.width() - 5
        )  # Adjusted to the right by 10 pixels for padding
        y = (
            pixmap_rect.bottom() - text_rect.height() - 5
        )  # Adjusted to the bottom by 10 pixels for padding
        self.text_item.setPos(
            x, y
        )  # setPos() sets the position of the text item in the parent item's (i.e., the pixmap's) coordinates.

    def calculate_window_width_level(self, method="std", **kwargs):
        """
        Calculate window width and level based on signal intensity distribution of middle slice of signal array.

        Parameters:
        method (str): Method to calculate WW and WL ('std' or 'percentile').
        std_multiplier (float): Multiplier for the standard deviation (only used if method is 'std').

        Returns:
        tuple: (window_width, window_level)
        """

        array = self.array[
            :, :, self.array.shape[2] // 2
        ]  # window width and level will be calculate based on middle slice of array

        if method == "std":
            std_multiplier = kwargs.get("std_multiplier", 2)
            window_level = np.mean(array)
            window_width = std_multiplier * np.std(array)
        elif method == "percentile":
            lower_percentile = kwargs.get("lower_percentile", 5)
            upper_percentile = kwargs.get("upper_percentile", 95)
            lower_percentile_value = np.percentile(
                array, lower_percentile
            )  # value blow which lower_percentile of the data lies
            upper_percentile_value = np.percentile(
                array, upper_percentile
            )  # value below which upper_percentile of the data lies
            window_width = upper_percentile_value - lower_percentile_value
            window_level = lower_percentile_value + window_width / 2
        elif method == "none":
            window_width = np.max(array) - np.min(array)
            window_level = (np.max(array) + np.min(array)) / 2
        else:
            raise ValueError(f"Invalid method: {method}")

        return window_width, window_level

    def apply_window_width_level(self):
        """
        Apply window width and level to the displayed slice of the signal array.

        Returns:
        numpy.ndarray: The windowed array of the displayed slice (normalized).
        """
        windowed_array = np.clip(
            self.array[:, :, self.current_slice],
            self.window_level - self.window_width / 2,
            self.window_level + self.window_width / 2,
        )
        windowed_array = (
            windowed_array - (self.window_level - self.window_width / 2)
        ) / self.window_width
        return windowed_array

    def add_observer(self, observer):
        self.observers.append(observer)
        log.debug(f"Observer {observer} added to {self}")

    def notify_observers(self, window_width, window_level):
        for observer in self.observers:
            observer.update(window_width, window_level)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_button_pressed = True
            self.start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_button_pressed = False

    def mouseMoveEvent(self, event):
        if self.displaying == False:
            return

        if self.middle_mouse_button_pressed:
            dx = event.x() - self.start_pos.x()
            dy = self.start_pos.y() - event.y()

            window_level = max(0, self.window_level + dy * 0.001)
            window_width = max(0, self.window_width + dx * 0.001)

            self.start_pos = event.pos()

            self.set_window_width_level(window_width, window_level)
            self.displayArray()

    def update(self, window_width, window_level):
        if self.displaying == False:
            return
        if self.window_width != window_width or self.window_level != window_level:
            self.set_window_width_level(window_width, window_level)
            self.displayArray()
        else:
            pass


class DropImageLabel(ImageLabel):
    dropEventSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        source_widget = event.source()
        # Should only accept drops if source widget is ScanlistListWidget and only one item is selected
        if (
            isinstance(source_widget, ScanlistListWidget)
            and len(source_widget.selectedIndexes()) == 1
        ):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        source_widget = event.source()
        selected_index = source_widget.selectedIndexes()[0].row()
        self.dropEventSignal.emit(selected_index)
        event.accept()
