from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton

from utils.logger import log


class ShortcutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard Shortcuts")
        # self.setMinimumSize(300, 200)

        layout = QVBoxLayout()
        table = QTableWidget()

        shortcuts = [
            ("Ctrl+L", "Load session"),
            ("Ctrl+S", "Save session"),
            ("Ctrl+M", "Switch between scanning mode and viewing mode"),
            ("Ctrl+D", "Measure distance"),
            ("Ctrl+W", "Toggle window leveling"),
            ("Ctrl+A", "Measure area"),
            ("Ctrl+H", "Show keyboard shortcuts (this dialog)"),
        ]

        table.setRowCount(len(shortcuts))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Shortcut", "Description"])
        table.setVerticalHeaderLabels(["" for _ in range(len(shortcuts))])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for i, (shortcut, description) in enumerate(shortcuts):
            table.setItem(i, 0, QTableWidgetItem(shortcut))
            table.setItem(i, 1, QTableWidgetItem(description))

        # Align headers to the left
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Resize to fit contents and add padding
        table.resizeColumnsToContents()
        for column in range(table.columnCount()):
            table.setColumnWidth(column, table.columnWidth(column) + 20)  # Adding extra 20 pixels

        layout.addWidget(table)

        # Calculate minimum size of the dialog to fit the table
        table_width = sum(table.columnWidth(column) for column in range(table.columnCount()))
        self.setMinimumSize(table_width + 50, table.verticalHeader().length() + 50)  # Adding padding

        self.setLayout(layout)

