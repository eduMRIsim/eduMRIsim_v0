from PyQt6.QtCore import QDir
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QListView

from views.styled_widgets import PrimaryActionButton


class ExamCardTabWidget(QTabWidget):
    def __init__(self, examCardTab, savedItemsTab):
        super().__init__()
        self.addTab(examCardTab, "Scan items")
        self.addTab(savedItemsTab, "Saved items")


class SavedItemsTab(QWidget):
    def __init__(self, directory_path):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._savedItemsListView = CustomListView()
        self._savedItemsListView.setDragDropMode(QListView.DragDropMode.DragOnly)
        self._savedItemsListView.setSelectionMode(
            QListView.SelectionMode.ExtendedSelection
        )
        self._savedItemsListView.setEditTriggers(
            QListView.EditTrigger.NoEditTriggers
        )
        self.layout.addWidget(self._savedItemsListView)

        self.populate_list(directory_path)

        self._importScanItemButton = PrimaryActionButton("Import Scan")
        self.layout.addWidget(self._importScanItemButton)


    def populate_list(self, directory_path):
        model = QFileSystemModel()
        model.setRootPath(directory_path)
        model.setFilter(QDir.Filter.Files)
        model.setNameFilters(["*.json"])

        self._savedItemsListView.setModel(model)
        self._savedItemsListView.setRootIndex(model.index(directory_path))

    @property
    def savedItemsListView(self):
        return self._savedItemsListView


class ExamCardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._examCardListView = QListView()
        self._examCardListView.setDragDropMode(QListView.DragDropMode.DragOnly)
        self._examCardListView.setSelectionMode(
            QListView.SelectionMode.ExtendedSelection
        )
        self._examCardListView.setEditTriggers(
            QListView.EditTrigger.NoEditTriggers
        )  # This is a flag provided by PyQt, which is used to specify that no editing actions should trigger item editing in the list view. It essentially disables editing for the list view, preventing users from directly editing the items displayed in the list.
        self.layout.addWidget(self._examCardListView)

    @property
    def examCardListView(self):
        return self._examCardListView

class CustomListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)