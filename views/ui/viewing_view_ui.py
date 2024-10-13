import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor, QResizeEvent, QImage, QPixmap, QDropEvent, QPen, QAction
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QSizePolicy, QGraphicsLineItem, QGraphicsTextItem, QMenu,
)

from simulator.scanlist import AcquiredSeries
from views.items.measurement_tool import MeasurementTool
from views.items.zoomin import ZoomableView
from views.ui.scanlist_ui import ScanlistListWidget


class gridViewingWindowLayout(QFrame):
    def __init__(self):
        super().__init__()

        rightLayout = QVBoxLayout()

        self.grid_cells = []

        # creates default 2x2 grid
        self.right_layout = QGridLayout()
        for i in range(2):
            rows = []  # list of elements in each row
            for j in range(2):
                empty_widget = GridCell(self, i, j)
                rows.append(empty_widget)
                self.right_layout.addWidget(empty_widget, i, j)
            self.grid_cells.append(rows)

        rightLayout.addLayout(self.right_layout)
        self.setLayout(rightLayout)

    def connect_drop_signals(self, drop_handler):
        for i in range(len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                grid_cell = self.grid_cells[i][j]
                grid_cell.dropEventSignal.connect(drop_handler)

    def get_grid_cell(self, i: int, j: int) -> "GridCell":
        if i < len(self.grid_cells) and j < len(self.grid_cells[i]):
            return self.grid_cells[i][j]
        else:
            print(f"Invalid cell access: row {i}, column {j}.")
            return None
    
    def add_row(self):
        '''Adds a new row of GridCell instances into the grid. '''
        row_index = len(self.grid_cells) 
        new_row= []  

        if self.grid_cells:
            nr_columns = len(self.grid_cells[0])
        else:
            nr_columns = 0

        if row_index < 5:
            for j in range(nr_columns):
                new_cell = GridCell(self, row_index, j)
                if row_index > 0:
                    new_cell.dropEventSignal.connect(self.grid_cells[row_index-1][j].dropEventSignal)
                new_row.append(new_cell)
                self.right_layout.addWidget(new_cell, row_index, j)

            self.grid_cells.append(new_row)
            #self.reconnect_signals()

            # reconnect signals
            #for j in range(nr_columns):
               #if row_index > 0:
                   # new_cell.dropEventSignal.connect(self.grid_cells[row_index - 1][j].dropEventSignal)
            
        else:
            print("Row limit reached!")

    def add_column(self):
        '''Adds a new column of GridCell instances into the grid. '''
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
                    new_cell.dropEventSignal.connect(self.grid_cells[i][col_index-1].dropEventSignal)
                new_col.append(new_cell)
                self.right_layout.addWidget(new_cell, i, col_index)

            for i in range(nr_rows):
                if len(self.grid_cells) <= i:
                    self.grid_cells.append([])
                self.grid_cells[i].append(new_col[i])

            #self.reconnect_signals()
            # reconnect signals
            for i in range(nr_rows):
                if col_index > 0:
                    new_col[i].dropEventSignal.connect(self.grid_cells[i][col_index - 1].dropEventSignal)
        else:
            print("Column limit reached!")

    def remove_row(self, row_index):
        '''Removes the row of the cell you right-click on. '''

        if row_index < 0 or row_index >= len(self.grid_cells):
            print("There's no row here")
            return
    
        if len(self.grid_cells) < 3:
            print("Default grid; can't remove this row.")
            return

        for j in range(len(self.grid_cells[row_index])): 
            widget_to_remove = self.grid_cells[row_index][j]
            widget_to_remove.dropEventSignal.disconnect()
            self.right_layout.removeWidget(widget_to_remove) 
            widget_to_remove.deleteLater()
        
        self.grid_cells.pop(row_index)

        for i in range(row_index, len(self.grid_cells)):  
            for j in range(len(self.grid_cells[i])):
                widget = self.grid_cells[i][j]
                widget.row = i # updates the row index for every widget
                self.right_layout.addWidget(widget, i, j)

        self.reconnect_signals()
        self.update() 
    
    def remove_col(self, col_index):
        '''Removes the column of the cell you right-click on. '''

        if col_index < 0 or col_index >= len(self.grid_cells[0]):
            print("There's no column here")
            return
    
        if len(self.grid_cells[0]) < 3:
            print("Default grid; can't remove this column.")
            return

        for i in range(len(self.grid_cells)): 
            widget_to_remove = self.grid_cells[i][col_index]
            widget_to_remove.dropEventSignal.disconnect()
            print(f'signal disconnected for row {i} in column {col_index}')
            self.right_layout.removeWidget(widget_to_remove) 
            widget_to_remove.deleteLater()  
            self.grid_cells[i].pop(col_index)

        for i in range(len(self.grid_cells)):
            for j in range(col_index, len(self.grid_cells[i])):
                widget = self.grid_cells[i][j]
                widget.col = j # updates the col index for every widget
                self.right_layout.addWidget(widget, i, j) 
        
        self.reconnect_signals()
        self.update() 

    def reconnect_signals(self):
        '''Reconnects the drop event signals for all cells in the grid.'''
        for i in range(len(self.grid_cells)):
            for j in range(len(self.grid_cells[i])):
                    widget = self.grid_cells[i][j]
                    if j > 0:  
                        widget.dropEventSignal.connect(self.grid_cells[i][j - 1].dropEventSignal)
                        print(f"Connect cell [{i},{j}] to left cell at column {j - 1}")
                    else:
                        print(f"no left neighbour for [{i},{j}]")
                    if i > 0:
                        widget.dropEventSignal.connect(self.grid_cells[i - 1][j].dropEventSignal)
                        print(f"Connect cell [{i},{j}] to above cell at row {i - 1}")
                    else:
                        print(f"no top neighbour for [{i},{j}]")
                

class GridCell(ZoomableView):
    dropEventSignal = pyqtSignal(int, int, int)

    def __init__(self, parent_layout, row: int, col: int):
        super().__init__()

        self.row = row  # row index
        self.col = col  # col index
        self.parent_layout = parent_layout # reference to the parent layout

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

    def add_row(self):
        '''Trigger add_row method of the parent.'''
        #if self.parent():
           #self.parent().add_row()
        self.parent_layout.add_row()

    def add_column(self):
        '''Trigger add_column method of the parent.'''
        #if self.parent():
            #self.parent().add_column()
        self.parent_layout.add_column()

    def remove_row(self):
        self.parent_layout.remove_row(self.row)

    def remove_col(self):
        self.parent_layout.remove_col(self.row)

    def contextMenuEvent(self, position):
        '''Context menu for adding a row or column.'''
        #super().contextMenuEvent(event)

        # Initialize add row/col actions in the context menu
        self.add_rowcol_menu = QMenu(self)
        self.add_row_action = QAction("Add row")
        self.add_rowcol_menu.addAction(self.add_row_action)
        self.add_col_action = QAction("Add column")
        self.add_rowcol_menu.addAction(self.add_col_action)
        self.remove_row_action = QAction("Remove row")
        self.add_rowcol_menu.addAction(self.remove_row_action)
        self.remove_col_action = QAction("Remove column")
        self.add_rowcol_menu.addAction(self.remove_col_action)


        # Actions trigger the methods from this class which trigger the methods in the parent
        self.add_row_action.triggered.connect(lambda: self.add_row())
        self.add_col_action.triggered.connect(lambda: self.add_column())
        self.remove_row_action.triggered.connect(lambda: self.remove_row())
        self.remove_col_action.triggered.connect(lambda: self.remove_col())

        #self.add_rowcol_menu.exec(event.globalPos())
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
