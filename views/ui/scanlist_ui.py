from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QListWidget

from views.styled_widgets import PrimaryActionButton


class ScanlistInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            ScanlistInfoFrame {
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """
        )
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._addScanItemButton = PrimaryActionButton("Add Scan Item")
        self._scanlistListWidget = ScanlistListWidget()
        self.layout.addWidget(self._scanlistListWidget)
        self.layout.addWidget(self._addScanItemButton)

    @property
    def addScanItemButton(self):
        return self._addScanItemButton

    @property
    def scanlistListWidget(self):
        return self._scanlistListWidget


class ScanlistListWidget(QListWidget):
    dropEventSignal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: none;")
        self.setDragDropMode(self.DragDropMode.DragDrop)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setAcceptDrops(True)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            self.setCurrentItem(item)
            self.itemDoubleClicked.emit(
                item
            )  # Manually emit the itemDoubleClicked signal

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        e.accept()

    def dragMoveEvent(self, e: QDragMoveEvent) -> None:
        e.accept()

    def dropEvent(self, e: QDropEvent):
        # Get the widget that received the drop event
        widget = e.source()
        # do not accept drops from itself
        if widget == self:
            e.ignore()
        else:
            selected_indexes = widget.selectedIndexes()
            self.dropEventSignal.emit(selected_indexes)
            e.accept()

    def save_state(self):
        state = {
            "items": [self.item(i).text() for i in range(self.count())],
            "selected": self.currentRow(),
        }

        return state

    def restore_state(self, state):
        self.clear()
        items = state.get("items", [])
        for item in items:
            self.addItem(item)

        selected = state.get("selected", -1)
        if selected != -1:
            self.setCurrentRow(state["selected"])
