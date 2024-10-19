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
    QWheelEvent # scrolling
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
    QCheckBox,
    QLabel, # scan name
    QPushButton, # scrolling
    QGraphicsOpacityEffect # scrolling
)

from simulator.scanlist import AcquiredSeries
from views.items.measurement_tool import MeasurementTool
from views.items.zoomin import ZoomableView
from views.ui.scanlist_ui import ScanlistListWidget
from utils.logger import log


class gridViewingWindowLayout(QFrame):
    gridUpdated = pyqtSignal()  # signal to notify row/column removal

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
    
    def start_geometry_linking(self):
        """Synchronizes zooming, panning and scrolling for the checked cells. """
        linked_cells = self.get_checked_cells()
        self.linked_cells = []
        for i, j in linked_cells:
            self.linked_cells.append(self.grid_cells[i][j])
        
        reference_scan_plane = None
        for cell in self.linked_cells:
            # check if the cells have scans
            if cell.displayed_image is None:
                print(f"Cell at ({cell.row}, {cell.col}) does not have an image. Cannot link.")
                return
            
            # check if the cells have the same scan plane
            if reference_scan_plane is None:
                reference_scan_plane = cell.acquired_series.scan_plane
            elif cell.acquired_series.scan_plane != reference_scan_plane:
                print(f"Cells have different scan planes. Cannot link scans.")
                return
            
            # TODO check if the cells have the same rotation

        if not linked_cells:
            log.warn("No cells selected for geometry linking!.")
            return
        else:
            print(f"Geometry linking will be done for cells: {linked_cells}")

        # [i from the first tuple][j from the first tuple]
        reference_cell = self.grid_cells[linked_cells[0][0]][linked_cells[0][1]]

        # zoom and pan in the reference cell
        reference_zoom_level = reference_cell.transform().m11()  # get zoom level
        reference_h_pan = reference_cell.horizontalScrollBar().value() # get horizontal pan
        reference_v_pan = reference_cell.verticalScrollBar().value() # get vertical pan

        for cell in self.linked_cells:
            # connect to zoom and pan signals
            cell.zoomChanged.connect(self.synchronize_zoom_to_all_cells) 
            cell.panChanged.connect(self.synchronize_pan_to_all_cells) 
            # TODO move scrolling in ZoomableView and add a signal for it
            cell.scrollChanged.connect(self.synchronize_scroll_buttons)

            # apply the zoom level
            current_zoom = cell.transform().m11()
            if current_zoom != reference_zoom_level:
                cell.resetTransform()
                cell.updateLabelPosition() # do i need this
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

    def synchronize_scroll_buttons(self, new_index):
        """Synchronize the up and down button actions across all linked cells."""
        for cell in self.linked_cells:
            if cell.displayed_image_index != new_index:  # Only update if necessary
                cell.displayed_image_index = new_index
                cell.setDisplayedImage(
                    cell.acquired_series.list_acquired_images[new_index],
                    cell.acquired_series.scan_plane,
                    cell.acquired_series.series_name
                )
                cell.update_buttons_visibility()
    
    def stop_geometry_linking(self):
        """Stops geometry linking for the selected cells."""
        linked_cells = self.get_checked_cells()
        
        if not linked_cells:
            log.warn("No cells selected for geometry linking!.")
            return

        for cell in self.linked_cells:
            cell.zoomChanged.disconnect(self.synchronize_zoom_to_all_cells) # disconnects cells from zoom signal
            cell.panChanged.disconnect(self.synchronize_pan_to_all_cells) # disconnects cells from pan signal
            cell.scrollChanged.disconnect(self.synchronize_scroll_buttons)

        for i in range(len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                self.grid_cell = self.grid_cells[i][j]
                self.grid_cell.resetTransform()
                #self.updateLabelPosition()
        
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
    scrollChanged = pyqtSignal(int) # signal for scrolling # TODO move this to ZoomableView

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

        # TODO move scrolling and scan name/label to ZoomableView
        #  Display scan plane label
        self.scan_plane_label = QLabel(self)
        self.scan_plane_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.scan_plane_label.setStyleSheet("padding: 5px;")
        self.scan_plane_label.resize(100, 100)
        self.scan_plane_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.updateLabelPosition()

        # Display scan name
        self.series_name_label = QLabel(self)
        self.series_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.series_name_label.setStyleSheet(
            "color: white; font-size: 14px; padding: 5px;"
        )
        self.series_name_label.resize(200, 50)
        self.series_name_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.series_name_label.move(0, 0)

        # scrolling
        self.scroll_amount = 0
        self.up_button = QPushButton("▲")
        self.down_button = QPushButton("▼")
        self.up_button.setFixedSize(30, 30)
        self.down_button.setFixedSize(30, 30)
        self.up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.down_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.setSpacing(8)
        button_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        self.up_button.clicked.connect(self.go_up)
        self.down_button.clicked.connect(self.go_down)
        self.setLayout(button_layout)
        self.update_buttons_visibility()

        # measurement tool 
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
            self.update_buttons_visibility()

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

    def updateLabelPosition(self):
        if self.scan_plane_label.pixmap() is not None:
            label_width = self.scan_plane_label.pixmap().width()
            label_height = self.scan_plane_label.pixmap().height()
        else:
            label_width = 0
            label_height = 0

        padding = 10
        x_pos = self.width() - label_width - padding
        y_pos = self.height() - label_height - padding
        self.scan_plane_label.move(x_pos, y_pos)
        self.scan_plane_label.adjustSize()
        self.scan_plane_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

    def setDisplayedImage(self, image,  scan_plane="Unknown", series_name="Scan"):
        self.displayed_image = image
        if image is not None:
            self.array = image.image_data
            self.set_displayed_image(image)

            # Determine the scan plane
            icon_path = f"resources/icons/plane_orientation/{scan_plane.lower()}.svg"
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(
                100,
                100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.scan_plane_label.setPixmap(scaled_pixmap)
            self.scan_plane_label.resize(scaled_pixmap.width(), scaled_pixmap.height())

            # Set the scan name
            scan_number = self.displayed_image_index + 1
            self.series_name_label.setText(f"{series_name} ({scan_number}) ")

            self.updateLabelPosition()
        else:
            self.array = None
            self.scan_plane_label.clear()
            self.series_name_label.setText("")

        self._displayArray()

    def update_buttons_visibility(self):
        if self.acquired_series is None:
            self.up_button.hide()
            self.down_button.hide()
        else:
            self.up_button.show()
            self.down_button.show()

            # Reduce opacity of up button when on the first image
            if self.displayed_image_index == 0:
                self.up_button.setEnabled(False)
                self.set_button_opacity(self.up_button, 0.8)
            else:
                self.up_button.setEnabled(True)
                self.set_button_opacity(self.up_button, 1.0)

            # Reduce opacity of down button when on the last image
            if (
                self.displayed_image_index
                == len(self.acquired_series.list_acquired_images) - 1
            ):
                self.down_button.setEnabled(False)
                self.set_button_opacity(self.down_button, 0.8)
            else:
                self.down_button.setEnabled(True)
                self.set_button_opacity(self.down_button, 1.0)

    def set_button_opacity(self, button, opacity_value):
        opacity_effect = QGraphicsOpacityEffect(button)
        opacity_effect.setOpacity(opacity_value)
        button.setGraphicsEffect(opacity_effect)

    # up button functionality
    def go_up(self):
        if self.acquired_series is None:
            return
        if self.displayed_image_index > 0:
            self.displayed_image_index -= 1
            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
        self.update_buttons_visibility()
        self.scrollChanged.emit(self.displayed_image_index)

    # down button functionality
    def go_down(self):
        if self.acquired_series is None:
            return
        if (
            self.displayed_image_index
            < len(self.acquired_series.list_acquired_images) - 1
        ):
            self.displayed_image_index += 1
            self.setDisplayedImage(
                self.acquired_series.list_acquired_images[self.displayed_image_index],
                self.acquired_series.scan_plane,
                self.acquired_series.series_name,
            )
        self.update_buttons_visibility()
        self.scrollChanged.emit(self.displayed_image_index)

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
