from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QListView


class ExamCardTabWidget(QTabWidget):
    def __init__(self, examCardTab):
        super().__init__()
        self.addTab(examCardTab, "Scan items")


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
