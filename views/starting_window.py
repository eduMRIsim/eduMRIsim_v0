from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt


class StartingWindow(QWidget):
    def __init__(self, start_new_examination_callback, load_examination_callback):
        super(StartingWindow, self).__init__()
        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel("Welcome to eduMRIsim")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold;")

        # New Session header
        new_session_header = QLabel("Create New Session")
        new_session_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        new_session_header.setStyleSheet(
            "font-size: 24px; font-weight: semi-bold; margin-top: 20px;"
        )

        # Load Session header
        load_session_header = QLabel("Load Session")
        load_session_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        load_session_header.setStyleSheet(
            "font-size: 24px; font-weight: semi-bold; margin-top: 20px;"
        )

        # Create buttons
        self.new_examination_button = QPushButton("New Examination")
        self.new_examination_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_examination_button.clicked.connect(start_new_examination_callback)

        self.load_examination_button = QPushButton("Load from .ini file")
        self.load_examination_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_examination_button.clicked.connect(
            load_examination_callback
        )  # Connect to load examination

        self.load_previous_examination_button = QPushButton("Load previous session")
        self.load_previous_examination_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Add widgets to layout
        layout.addWidget(welcome_label)
        layout.addWidget(new_session_header)
        layout.addWidget(self.new_examination_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(load_session_header)
        layout.addWidget(self.load_examination_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(
            self.load_previous_examination_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addStretch(1)

        # Set layout
        self.setLayout(layout)
        self.setWindowTitle("Starting Screen")
        self.resize(600, 400)
