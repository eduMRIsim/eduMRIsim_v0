from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)


class ShortcutDialog(QDialog):
    """
    Dialog to show keyboard shortcuts.

    This dialog shows all the keyboard shortcuts that are available in the application.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard Shortcuts")

        # These are all the shortcuts that are available in the application
        # If any new shortcuts are added, they should be added here
        shortcuts = [
            ("Ctrl+L", "Load session"),
            ("Ctrl+S", "Save session"),
            ("Ctrl+M", "Switch between scanning mode and viewing mode"),
            # ("Ctrl+D", "Measure distance"),
            ("Ctrl+W", "Toggle window leveling"),
            # ("Ctrl+A", "Measure area"),
            ("Ctrl+H", "Show keyboard shortcuts (this dialog)"),
            (
                "M",
                "Measure a distance in an image:\n"
                "1. Left click into a planning view window.\n"
                "2. Move the mouse cursor to one of the two end points of the line to be measured.\n"
                "3. Press the M key to start measuring from the mouse cursor.\n"
                "4. Move the mouse cursor to the other end point of the line to be measured.\n"
                "5. Press the M key again to stop measuring.",
            ),
            (
                "Z",
                "Zoom in and out of an image:\n"
                "1. Move the mouse cursor into the planning view window, over the image.\n"
                "2. Start holding the Z key to start zooming.\n"
                "3. While holding the Z key, hold left click and move the mouse cursor up and down to zoom in and out.\n"
                "4. Release left click and then the Z key to stop zooming.",
            ),
            (
                "P",
                "Pan an image:\n"
                "1. Move the mouse cursor into the planning view window, over the image.\n"
                "2. Start holding the P key to start panning.\n"
                "3. While holding the P key, hold left click and move the mouse cursor to pan the image.\n"
                "4. Release left click and then the P key to stop panning.",
            ),
        ]

        # Create a table to display the shortcuts
        table = QTableWidget()
        table.setRowCount(len(shortcuts))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Shortcut", "Description"])
        table.setVerticalHeaderLabels(["" for _ in range(len(shortcuts))])

        # Set table properties (the table should be read-only)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Add the shortcuts to the table
        for i, (shortcut, description) in enumerate(shortcuts):
            table.setItem(i, 0, QTableWidgetItem(shortcut))
            table.setItem(i, 1, QTableWidgetItem(description))

        # Align the table headers to the left
        header = table.horizontalHeader()
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # Resize the table to fit its contents, and add padding
        for row in range(table.rowCount()):
            table.setRowHeight(row, table.rowHeight(row) + 20)
            if row == 5 or row == 6 or row == 7:
                table.setRowHeight(row, table.rowHeight(row) + 50)
        table.resizeColumnsToContents()
        for column in range(table.columnCount()):
            table.setColumnWidth(
                column, table.columnWidth(column) + 20
            )  # Adding extra 20 pixels

        # Create the layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(table)

        # Calculate the minimum size of the dialog to fit the table
        table_width = sum(
            table.columnWidth(column) for column in range(table.columnCount())
        )
        self.setMinimumSize(
            table_width + 50, table.verticalHeader().length() + 50
        )  # Adding padding

        # Set the layout for the dialog
        self.setLayout(layout)
