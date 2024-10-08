import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor, QResizeEvent, QImage, QPixmap, QDropEvent, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QSizePolicy,
    QMenu,
    QWidgetAction
)

from simulator.scanlist import AcquiredSeries
from views.ui.scanlist_ui import ScanlistListWidget


class gridViewingWindowLayout(QFrame):
    def __init__(self):
        super().__init__()

        rightLayout = QVBoxLayout()

        # store all GridCell cells
        # useful for handling the drops
        self.grid_cells = []

        # creates default 2x2 grid
        right_layout = QGridLayout()
        for i in range(2):
            rows = []  # list of elements in each row
            for j in range(2):
                empty_widget = GridCell(i, j)
                rows.append(empty_widget)
                right_layout.addWidget(empty_widget, i, j)
            self.grid_cells.append(rows)

        rightLayout.addLayout(right_layout)
        self.setLayout(rightLayout)

    def connect_drop_signals(self, drop_handler):
        for i in range(2):
            for j in range(2):
                grid_cell = self.grid_cells[i][j]
                grid_cell.dropEventSignal.connect(drop_handler)

    def get_grid_cell(self, i: int, j: int) -> "GridCell":
        return self.grid_cells[i][j]
    
    def add_row(self):
        '''Adds a new column of GridCell instances into the grid. '''
        row_index = len(self.grid_cells) 
        new_row= []  

        nr_columns = self.righ_layout.columnCount()  

        for j in range(nr_columns): 
            new_cell = GridCell(row_index, j)  
            new_row.append(new_cell) 
            self.right_layout.addWidget(new_cell, row_index, j) 

        self.grid_cells.append(new_row) 

    def add_column(self):
        '''Adds a new column of GridCell instances into the grid. '''
        col_index = len(self.grid_cells)
        new_col = []

        nr_rows = self.right_layout.rorCount()

        for i in range(nr_rows):
            new_cell = GridCell(i, col_index)
            new_col.append(new_cell)
            self.right_layout.addWidget(new_cell, i, col_index)

        self.grid_cells.append(new_col)


class GridCell(QGraphicsView):
    dropEventSignal = pyqtSignal(int, int, int)

    def __init__(self, row: int, col: int):
        super().__init__()

        self.row = row  # row index
        self.col = col  # col index

        # pixmap graphics
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Set the background color to black
        self.setBackgroundBrush(QColor(0, 0, 0))

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.displayed_image = None
        self.acquired_series = None
        self.array = None

        self.setAcceptDrops(True)

        # zoom controls
        self.mouse_pressed = False
        self.zoom_key_pressed = False
        self.last_mouse_pos = None
        self.zoom_sensitivity = 0.005

    def contextMenuEvent(self, event):
        '''Context menu for adding a row or column. '''
        super().contextMenuEvent(event)


    # start zoom when pressed
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_pos = event.pos()

    # stop zoom when released
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            self.last_mouse_pos = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Z:
            self.zoom_key_pressed = True

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Z:
            self.zoom_key_pressed = False


    def mouseMoveEvent(self, event):
        """Handle zoom when the mouse is being dragged."""
        if self.mouse_pressed and self.zoom_key_pressed and self.last_mouse_pos is not None:

            max_zoom_out = 0.1
            max_zoom_in = 10
            current_pos = event.pos()
            delta_y = current_pos.y() - self.last_mouse_pos.y()

            # cursor_pos = self.mapToScene(current_pos)
            zoom_factor = 1 + (delta_y * self.zoom_sensitivity)

            # get current zoom level (scaling factor)
            current_zoom = self.transform().m11()

            new_zoom = current_zoom * zoom_factor
            if max_zoom_out <= new_zoom <= max_zoom_in:
                self.scale(zoom_factor, zoom_factor)

            self.scale(zoom_factor, zoom_factor)
            self.centerOn(self.mapToScene(current_pos))
            self.last_mouse_pos = current_pos

    def zoom_in(self, center_point):
        if self.transform().m11() < self.max_zoom_in:
            self.scale(self.zoom_factor, self.zoom_factor)

    def zoom_out(self, center_point):
        if self.transform().m11() > self.max_zoom_out:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            self.centerOn(center_point)

    def resizeEvent(self, event: QResizeEvent):
        """This method is called whenever the graphics view is resized.
        It ensures that the image is always scaled to fit the view."""
        super().resizeEvent(event)
        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self.pixmap_item)

    def _displayArray(self):
        width, height = 0, 0
        if self.array is not None:

            # Normalize the slice values for display
            array_norm = (self.array[:, :] - np.min(self.array)) / (
                np.max(self.array) - np.min(self.array)
            )
            array_8bit = (array_norm * 255).astype(np.uint8)

            # Convert the array to QImage for display. This is because you cannot directly set a QPixmap from a NumPy array. You need to convert the array to a QImage first.
            image = np.ascontiguousarray(np.array(array_8bit))
            height, width = image.shape
            qimage = QImage(
                image.data, width, height, width, QImage.Format.Format_Grayscale8
            )

            # Create a QPixmap - a pixmap which can be displayed in a GUI
            pixmap = QPixmap.fromImage(qimage)
            self.pixmap_item.setPixmap(pixmap)

            self.pixmap_item.setPos(0, 0)  # Ensure the pixmap item is at (0, 0)
            self.scene.setSceneRect(
                0, 0, width, height
            )  # Adjust the scene rectangle to match the pixmap dimensions

        else:
            # Set a black image when self.array is None
            black_image = QImage(1, 1, QImage.Format.Format_Grayscale8)
            black_image.fill(Qt.GlobalColor.black)
            pixmap = QPixmap.fromImage(black_image)
            self.pixmap_item.setPixmap(pixmap)
            self.scene.setSceneRect(0, 0, 1, 1)

        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self.pixmap_item)

    def setAcquiredSeries(self, acquired_series: AcquiredSeries):
        if acquired_series is not None:
            self.acquired_series = acquired_series
            self.displayed_image_index = 0

            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
        else:
            self.acquired_series = None
            self.setDisplayedImage(None)

    def set_displayed_image(self, displayed_image):
        self.displayed_image = displayed_image

    def setDisplayedImage(self, image, scan_plane="Unknown", series_name="Scan"):
        self.displayed_image = image
        if image is not None:
            self.array = image.image_data
            self.set_displayed_image(image)
        else:
            self.array = None

        self._displayArray()

    def dropEvent(self, event: QDropEvent) -> None:
        source_widget = event.source()
        selected_index = source_widget.selectedIndexes()[0].row()
        self.dropEventSignal.emit(self.row, self.col, selected_index)
        event.accept()

    def dragEnterEvent(self, event):
        source_widget = event.source()
        if (
            isinstance(source_widget, ScanlistListWidget)
            and len(source_widget.selectedIndexes()) == 1
        ):
            event.accept()
        else:
            event.ignore()
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()
