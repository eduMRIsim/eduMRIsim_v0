import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QResizeEvent,
    QImage,
    QPixmap,
    QDropEvent,
    QPen,
    QAction,
)
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QSizePolicy,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QMenu,
    QCheckBox
)

from simulator.scanlist import AcquiredSeries
from views.items.measurement_tool import MeasurementTool
from views.items.zoomin import ZoomableView
from views.ui.scanlist_ui import ScanlistListWidget
from utils.logger import log


class gridViewingWindowLayout(QFrame):
    gridUpdated = pyqtSignal() # signal to notify row/column removal

    def __init__(self):
        super().__init__()

        rightLayout = QVBoxLayout()

        self.grid_cells = []

        # creates default 2x2 grid
        self.right_layout = QGridLayout()
        for i in range(2):
            rows = []
            for j in range(2):
                empty_widget = GridCell(self, i, j)
                rows.append(empty_widget)
                self.right_layout.addWidget(empty_widget, i, j)
            self.grid_cells.append(rows)

        rightLayout.addLayout(self.right_layout)
        self.setLayout(rightLayout)

    def connect_drop_signals(self, drop_handler):
        """Connects all GridCell instances in the grid to accept drops. """
        self.drop_handler = drop_handler
        self.reconnect_all_signals(drop_handler)

    def reconnect_all_signals(self, drop_handler):
        """Reconnects all GridCell instances in the grid to accept drops. """
        if self.drop_handler is None:
            log.error("Drop handler is not set.")
            return

        for i in range(len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                self.grid_cell = self.grid_cells[i][j]
                try:
                    self.grid_cell.dropEventSignal.disconnect()
                except Exception as e:
                    log.warn(f"Unable to disconnect dropEventSignal: {e}")
                self.grid_cell.dropEventSignal.connect(drop_handler)

    def get_grid_cell(self, i: int, j: int) -> "GridCell":
        """Retrieves an instance of the GridCell. """
        if i < len(self.grid_cells) and j < len(self.grid_cells[i]):
            return self.grid_cells[i][j]
        else:
            log.error(f"Invalid cell access: row {i}, column {j}.")
            return None
        
    def show_checkboxes(self):
        """Adds checkboxes to all cells in the grid."""
        for row in self.grid_cells:
            for cell in row:
                cell.set_visibility_checkbox(True)

    def hide_checkboxes(self):
        """Hides checkboxes in all cells."""
        for row in self.grid_cells:
            for cell in row:
                cell.set_visibility_checkbox(False) 

    def get_checked_cells(self):
        """Stores a list of the checked cells. """
        checked_cells = []

        for i in range(len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                cell = self.grid_cells[i][j]
                if cell.checkbox.isVisible() and cell.checkbox.isChecked():
                    checked_cells.append((i, j))
                    print(f"Checkbox is checked in cell [{i},{j}]")

        return checked_cells
    
    def start_geometry_linking(self):
        """Synchronizes zooming and panning for the checked cells. """
        linked_cells = self.get_checked_cells()
        self.linked_cells = [self.grid_cells[row][col] for row, col in linked_cells]

        print(f"Geometry linking will be done for cells: {linked_cells}")

        if not linked_cells:
            log.warn("No cells selected for geometry linking!.")
            return

        reference_cell = self.grid_cells[linked_cells[0][0]][linked_cells[0][1]]

        # zoom and pan in the cell the others need to copy
        reference_zoom_level = reference_cell.transform().m11()  # get zoom level
        reference_h_pan = reference_cell.horizontalScrollBar().value() # get horizontal pan
        reference_v_pan = reference_cell.verticalScrollBar().value() # get vertical pan

        for cell in self.linked_cells:
            # connect to zoom and pan signals
            cell.zoomChanged.connect(self.synchronize_zoom_to_all_cells) 
            cell.panChanged.connect(self.synchronize_pan_to_all_cells) 
            # apply the zoom level
            current_zoom = cell.transform().m11()
            if current_zoom != reference_zoom_level:
                cell.resetTransform()
                zoom_factor = reference_zoom_level / 1.0
                cell.scale(zoom_factor, zoom_factor)

            # apply pan values 
            cell.horizontalScrollBar().setValue(reference_h_pan)
            cell.verticalScrollBar().setValue(reference_v_pan)
        
        print(f"Cells {len(linked_cells)} are geometry linked.")
    
    def synchronize_zoom_to_all_cells(self, zoom_level):
        """Synchronizes the zoom level in the linked cells ."""
        for cell in self.linked_cells:
            current_zoom = cell.transform().m11()
            if current_zoom != zoom_level:
                cell.resetTransform()
                zoom_factor = zoom_level / 1.0
                cell.scale(zoom_factor, zoom_factor)

    def synchronize_pan_to_all_cells(self, h_scroll, v_scroll):
        """Synchronizes panning around in the linked cells."""
        for cell in self.linked_cells:
            cell.horizontalScrollBar().setValue(h_scroll)
            cell.verticalScrollBar().setValue(v_scroll)
    
    def stop_geometry_linking(self):
        """Stops geometry linking for the selected cells."""
        linked_cells = self.get_checked_cells()
        
        if not linked_cells:
            log.warn("No cells selected for geometry linking!.")
            return

        for cell in self.linked_cells:
            cell.zoomChanged.disconnect(self.synchronize_zoom_to_all_cells) # disconnects cells from zoom signal
            cell.panChanged.disconnect(self.synchronize_zoom_to_all_cells) # disconnects cells from pan signal
        
        print(f"Stopped geometry linking for {len(self.linked_cells)} cells.")
        self.linked_cells = []
        self.hide_checkboxes()

    def add_row(self):
        """Adds a new row of GridCell instances into the grid."""
        row_index = len(self.grid_cells)
        new_row = []

        if self.grid_cells:
            nr_columns = len(self.grid_cells[0])
        else:
            nr_columns = 0

        if row_index < 5:
            for j in range(nr_columns):
                new_cell = GridCell(self, row_index, j)
                if row_index > 0:
                    new_cell.dropEventSignal.connect(
                        self.grid_cells[row_index - 1][j].dropEventSignal
                    )
                new_row.append(new_cell)
                self.right_layout.addWidget(new_cell, row_index, j)

            self.grid_cells.append(new_row)

        else:
            log.error("Row limit reached!")

    def add_column(self):
        """Adds a new column of GridCell instances into the grid."""
        if self.grid_cells:
            col_index = len(self.grid_cells[0])
        else:
            col_index = 0
        new_col = []

        nr_rows = len(self.grid_cells)

        if col_index < 5:
            for i in range(nr_rows):
                new_cell = GridCell(self, i, col_index)
                if col_index > 0:
                    new_cell.dropEventSignal.connect(
                        self.grid_cells[i][col_index - 1].dropEventSignal
                    )
                new_col.append(new_cell)
                self.right_layout.addWidget(new_cell, i, col_index)

            for i in range(nr_rows):
                if len(self.grid_cells) <= i:
                    self.grid_cells.append([])
                self.grid_cells[i].append(new_col[i])

        else:
            log.error("Column limit reached!")

    def remove_row(self, row_index):
        """Removes the row of the cell you right-click on."""

        log.debug("remove_row is called")

        if row_index < 0 or row_index >= len(self.grid_cells):
            log.error("There's no row here")
            return

        if len(self.grid_cells) < 3:
            log.error("Default grid; can't remove this row.")
            return

        # remove and disconnect cells on row row_index
        for j in range(len(self.grid_cells[row_index])):
            widget_to_remove = self.grid_cells[row_index][j]
            try:
                widget_to_remove.dropEventSignal.disconnect()
            except Exception as e:
                print(f"Warning: Unable to disconnect dropEventSignal: {e}")
            self.right_layout.removeWidget(widget_to_remove) 
            widget_to_remove.deleteLater()

        self.grid_cells.pop(row_index)

        # rearrange the cells
        for i in range(row_index, len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                widget = self.grid_cells[i][j]
                widget.row = i
                widget.col = j
                self.right_layout.addWidget(widget, i, j)

        self.right_layout.update()
        self.update()

        self.gridUpdated.emit() # signals that the grid needs to be reconnected
    
    def remove_col(self, col_index):
        """Removes the column of the cell you right-click on."""

        if col_index < 0 or col_index >= len(self.grid_cells[0]):
            log.error("There's no column here")
            return

        if len(self.grid_cells[0]) < 3:
            log.error("Default grid; can't remove this column.")
            return

        # remove and disconnect cells in column col_index
        for i in range(len(self.grid_cells)):
            widget_to_remove = self.grid_cells[i][col_index]
            try:
                widget_to_remove.dropEventSignal.disconnect()
            except Exception as e:
                print(f"Warning: Unable to disconnect dropEventSignal: {e}")
            self.right_layout.removeWidget(widget_to_remove) 
            widget_to_remove.deleteLater()  
            self.grid_cells[i].pop(col_index)

        # rearrange cells in the grid
        for i in range(len(self.grid_cells)):
            for j in range(col_index, len(self.grid_cells[i])):
                widget = self.grid_cells[i][j]
                widget.row = i
                widget.col = j
                self.right_layout.addWidget(widget, i, j)

        self.update() 

        self.gridUpdated.emit() # signals that the grid needs to be reconnected


class GridCell(ZoomableView):
    dropEventSignal = pyqtSignal(int, int, int)
    rowRemoveSignal = pyqtSignal(int)  # signal for removed rows

    def __init__(self, parent_layout, row: int, col: int):
        super().__init__()

        self.displayed_image_index = None
        self.remove_col_action = None
        self.remove_row_action = None
        self.add_col_action = None
        self.add_row_action = None
        self.add_rowcol_menu = None
        self.row = row  # row index
        self.col = col  # col index
        self.parent_layout = parent_layout  # reference to the parent layout

        # pixmap graphics
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setBackgroundBrush(QColor(0, 0, 0))

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)

        self.displayed_image = None
        self.acquired_series = None
        self.array = None

        self.setAcceptDrops(True)

        self.line_item = QGraphicsLineItem()
        self.line_item.setPen(QPen(QColor(255, 0, 0), 2))
        self.scene.addItem(self.line_item)

        self.text_item = QGraphicsTextItem()
        self.text_item.setDefaultTextColor(QColor(255, 0, 0))
        self.scene.addItem(self.text_item)

        self.measure = MeasurementTool(self.line_item, self.text_item, self)

        self.checkbox = QCheckBox("Link", self)
        self.checkbox.setVisible(False) # invisible by default
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_checkbox_position()
        
    def set_visibility_checkbox(self, visible):
        """Show or hide the checkbox."""
        self.checkbox.setVisible(visible)
        if visible:
            self.update_checkbox_position()
        
    def update_checkbox_position(self):
        if self.checkbox.isVisible():
            checkbox_height = self.checkbox.size().height()
        else:
            checkbox_height = 0

        padding = 10
        x_pos = padding 
        y_pos = self.height() - checkbox_height - padding 
        self.checkbox.move(x_pos, y_pos)
        self.checkbox.adjustSize()

    def add_row(self):
        """Trigger add_row method of the parent."""
        self.parent_layout.add_row()

    def add_column(self):
        """Trigger add_column method of the parent."""
        self.parent_layout.add_column()

    def remove_row(self):
        """Trigger remove_row method of the parent."""
        self.parent_layout.remove_row(self.row)

    def remove_col(self):
        """Trigger remove_col method of the parent."""
        self.parent_layout.remove_col(self.row)

    def contextMenuEvent(self, position):
        """Context menu for adding or removing rows and columns."""

        # Initialize add/remove row/col actions in the context menu
        self.add_rowcol_menu = QMenu(self)
        self.add_row_action = QAction("Add row")
        self.add_rowcol_menu.addAction(self.add_row_action)
        self.add_col_action = QAction("Add column")
        self.add_rowcol_menu.addAction(self.add_col_action)
        self.remove_row_action = QAction("Remove row")
        self.add_rowcol_menu.addAction(self.remove_row_action)
        self.remove_col_action = QAction("Remove column")
        self.add_rowcol_menu.addAction(self.remove_col_action)

        self.add_row_action.triggered.connect(lambda: self.add_row())
        self.add_col_action.triggered.connect(lambda: self.add_column())
        self.remove_row_action.triggered.connect(lambda: self.remove_row())
        self.remove_col_action.triggered.connect(lambda: self.remove_col())

        self.add_rowcol_menu.exec(self.mapToGlobal(position)) #shows menu at the cursor position

    def resizeEvent(self, event: QResizeEvent):
        """This method is called whenever the graphics view is resized.
        It ensures that the image is always scaled to fit the view."""
        super().resizeEvent(event)
        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self.pixmap_item)

    def _displayArray(self):
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
            )
        else:
            self.acquired_series = None
            self.setDisplayedImage(None)

    def set_displayed_image(self, displayed_image):
        self.displayed_image = displayed_image

    def setDisplayedImage(self, image):
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
