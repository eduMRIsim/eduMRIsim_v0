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
    QLinearGradient
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
    QLabel,
    QCheckBox
)

from simulator.scanlist import AcquiredSeries
from views.items.measurement_tool import MeasurementTool
from views.items.zoomin import ZoomableView
from views.ui.scanlist_ui import ScanlistListWidget
from utils.logger import log

import matplotlib.pyplot as plt


class gridViewingWindowLayout(QFrame):
    gridUpdated = pyqtSignal()  # signal to notify row/column removal

    def __init__(self):
        super().__init__()

        rightLayout = QVBoxLayout()

        self.grid_cells = []

        # initialize limits for rows/columns
        self.row_limit = 5
        self.column_limit = 5

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
        """Connects all GridCell instances in the grid to accept drops."""
        self.drop_handler = drop_handler
        self.reconnect_all_signals(drop_handler)

    def reconnect_all_signals(self, drop_handler):
        """Reconnects all GridCell instances in the grid to accept drops."""
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
        """Retrieves an instance of the GridCell."""
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
                cell.checkbox.setChecked(False)
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
    
    def start_contrast_linking(self):
        """Synchronizes window_levelling for the checked cells. """
        linked_cells = self.get_checked_cells()
        self.linked_cells = []
        for i, j in linked_cells:
            self.linked_cells.append(self.grid_cells[i][j])

        if not linked_cells:
            log.warn("No cells selected for contrast linking!.")
            return
        else:
            print(f"Contrast linking will be done for cells: {linked_cells}")

        for cell_i in self.linked_cells:
            for cell_j in self.linked_cells:
                # connect all cells to the same signal
                if cell_j != cell_i:
                    cell_i.contrastChanged.connect(
                        lambda window_center, window_width, cell = cell_j: self.synchronize_window_levelling(window_center, window_width, cell)
                    ) 
        
        print(f"Cells {len(linked_cells)} are contrast linked.")
    
    def synchronize_window_levelling(self, window_center, window_width, cell):
        """Synchronizes the window levelling for all the linked cells ."""
        cell.window_center = window_center
        cell.window_width = window_width

        cell._displayArray(window_center, window_width)
        cell.updateColorScale(window_center, window_width)
    
    def stop_contrast_linking(self):
        """Stops contrast linking for the selected cells."""
        linked_cells = self.get_checked_cells()
        
        if not linked_cells:
            log.warn("No cells selected for contrast linking!.")
            return

        for cell in self.linked_cells:
            try:
                cell.contrastChanged.disconnect() 
            except Exception as e:
                pass

        for i in range(len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                self.grid_cell = self.grid_cells[i][j]
                self.grid_cell.resetTransform()
                if self.grid_cell.pixmap_item:
                    self.grid_cell.fitInView(cell.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
                    self.grid_cell.centerOn(cell.pixmap_item)
                else: 
                    log.error("The cell has no pixmap item. ")
        
        print(f"Stopped contrast linking for {len(self.linked_cells)} cells.")
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

        if row_index < self.row_limit:
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

        if col_index < self.column_limit:
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
                log.warn(f"Unable to disconnect dropEventSignal: {e}")
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

        self.gridUpdated.emit()  # signals that the grid needs to be reconnected

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
                log.warn(f"Unable to disconnect dropEventSignal: {e}")
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

        self.gridUpdated.emit()  # signals that the grid needs to be reconnected


class GridCell(ZoomableView):
    dropEventSignal = pyqtSignal(int, int, int)

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
        
        # window level variables
        self.window_center = None
        self.window_width = None
        self.leveling_enabled = False
        self.previous_mouse_position = None
        
        # color scale bar
        self.color_scale = 'bw'
        self.color_scale_label = QLabel(self)
        self.color_scale_label.setFixedSize(20, 200)
        self.color_scale_label.setStyleSheet("background: black; border: 1px solid white")
        self.min_value_label = QLabel(self)
        self.min_value_label.setStyleSheet("color: white; font-size: 10px;")
        self.mid_value_label = QLabel(self)
        self.mid_value_label.setStyleSheet("color: white; font-size: 10px;")
        self.max_value_label = QLabel(self)
        self.max_value_label.setStyleSheet("color: white; font-size: 10px;")
        self.position_color_scale_elements() 

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

        # checkboxes for geometry linking
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
        """Ensures the checkboxes are positioned in the right bottom corner. """
        if self.checkbox.isVisible():
            checkbox_height = self.checkbox.size().height()
            checkbox_width = self.checkbox.size().width()
        else:
            checkbox_height = 0
            checkbox_width = 0

        padding = 10
        x_pos = self.width() - checkbox_width- padding 
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

        self.add_rowcol_menu.exec(
            self.mapToGlobal(position)
        )  # shows menu at the cursor position

    def resizeEvent(self, event: QResizeEvent):
        """This method is called whenever the graphics view is resized.
        It ensures that the image is always scaled to fit the view."""
        super().resizeEvent(event)
        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self.pixmap_item)
        self.update_checkbox_position()
        self.position_color_scale_elements()
        
    def toggle_window_level_mode(self):
        """Toggles window-leveling mode."""
        self.leveling_enabled = not self.leveling_enabled
        if self.leveling_enabled:
            log.info("Window-level mode enabled")
            # Initialize default values if they are None
            if self.window_center is None or self.window_width is None:
                self.window_center = np.mean(self.array)
                self.window_width = np.max(self.array) - np.min(self.array)
            
            self.position_color_scale_elements()
            
        else:
            log.info("Window-level mode disabled")

    def position_color_scale_elements(self):
        """Ensure the color scale and labels are positioned correctly."""
        padding = 20  

        self.color_scale_label.move(padding, self.height() // 2 - self.color_scale_label.height() // 2)

        self.min_value_label.move(self.color_scale_label.x() + self.color_scale_label.width() + 5,
                                  self.color_scale_label.y() - 5)
        self.mid_value_label.move(self.color_scale_label.x() + self.color_scale_label.width() + 5,
                                  self.color_scale_label.y() + self.color_scale_label.height() // 2 - 10)
        self.max_value_label.move(self.color_scale_label.x() + self.color_scale_label.width() + 5,
                                  self.color_scale_label.y() + self.color_scale_label.height() - 20)

        self.min_value_label.adjustSize()
        self.mid_value_label.adjustSize()
        self.max_value_label.adjustSize()

        
    def updateColorScale(self, window_center, window_width):
        """Updates the color scale bar based on the current color scale and window/level values."""
        
        if window_center is None:
            window_center = np.mean(self.array) if self.array is not None else 128
        if window_width is None:
            window_width = np.max(self.array) - np.min(self.array) if self.array is not None else 256

        min_value = max(0, window_center - window_width / 2)
        max_value = max(0, window_center + window_width / 2)

        # Create pixmap for color scale bar
        pixmap = QPixmap(self.color_scale_label.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, 0, self.color_scale_label.height())

        if self.color_scale == 'bw':
            min_grey_value = max(0, int(255 * (min_value / max(1, max_value))))
            max_grey_value = max(0, int(255 * (max_value / max(1, max_value))))
            gradient.setColorAt(0, QColor(min_grey_value, min_grey_value, min_grey_value))
            gradient.setColorAt(1, QColor(max_grey_value, max_grey_value, max_grey_value))
        
        elif self.color_scale == 'rgb':
            # Use the 'viridis' colormap to create the color gradient
            cmap = plt.get_cmap('viridis')
            for i in np.linspace(0, 1, 100):
                color = cmap(i)
                qcolor = QColor(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
                gradient.setColorAt(i, qcolor)

        painter.fillRect(0, 0, self.color_scale_label.width(), self.color_scale_label.height(), gradient)
        painter.end()

        self.color_scale_label.setPixmap(pixmap)

        self.min_value_label.setText(f"{int(min_value)}")
        self.mid_value_label.setText(f"{int(window_center)}")
        self.max_value_label.setText(f"{int(max_value)}")

        self.position_color_scale_elements()

    def setColorScale(self, color: str):
        if color in ['bw', 'rgb']:
            self.color_scale = color
            self._displayArray(self.window_center, self.window_width)
        else:
            raise ValueError("Invalid color scale. Use 'bw' or 'rgb'.")

    def _displayArray(self, window_center=None, window_width=None):
        """Display the image data with appropriate color scale."""
        if self.array is None:
            return
        
        # Normalize array
        array_norm = (self.array - np.min(self.array)) / (np.max(self.array) - np.min(self.array))
        
        # Update the color scale bar
        self.updateColorScale(window_center, window_width)

        # Calculate window/level
        if window_center is None or window_width is None:
            window_center = np.mean(self.array)
            window_width = np.max(self.array) - np.min(self.array)

        min_window = window_center - window_width / 2
        max_window = window_center + window_width / 2

        array_clamped = np.clip(self.array, min_window, max_window)
        array_norm = (array_clamped - min_window) / (max_window - min_window)

        if self.color_scale == 'bw':
            # Grayscale
            array_8bit = (array_norm * 255).astype(np.uint8)
            qimage = QImage(array_8bit.data, array_8bit.shape[1], array_8bit.shape[0], array_8bit.shape[1], QImage.Format.Format_Grayscale8)
        elif self.color_scale == 'rgb':
            # Apply colormap (viridis) to RGB
            color_mapped_array = plt.get_cmap('viridis')(array_norm)[:, :, :3]  # Get RGB values from viridis
            array_rgb = (color_mapped_array * 255).astype(np.uint8)
            qimage = QImage(array_rgb.data, array_rgb.shape[1], array_rgb.shape[0], array_rgb.shape[1] * 3, QImage.Format.Format_RGB888)

        # Set pixmap to display image
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)

        # Adjust view
        self.pixmap_item.setPos(0, 0)
        self.scene.setSceneRect(0, 0, qimage.width(), qimage.height())
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
