from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QFrame, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QSpacerItem, \
    QSizePolicy


class SegmentedButtonFrame(QFrame):
    def __init__(self, button_texts, parent=None):
        super().__init__(parent)

        # Create a QHBoxLayout to hold the segmented button
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Create an instance of the SegmentedButton class and add it to the layout 
        self.segmented_button = SegmentedButton(button_texts)
        self.layout.addWidget(self.segmented_button)

        stylesheet = """
        SegmentedButtonFrame {
            background-color: #f0f0f0;
            padding: 0;
        }

        SegmentedButton {
            border: none; /* Remove border from SegmentedButton */
            padding: 0; /* Remove padding from SegmentedButton */
        }        
        """

        self.setStyleSheet(stylesheet)

class SegmentedButton(QWidget):
    def __init__(self, button_texts, parent=None):
        super().__init__(parent)
        self.buttons = []

        # Create a QHBoxLayout to hold the buttons
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Create buttons and add them to the layout
        for text in button_texts:
            button = QPushButton(text)
            button.setCheckable(True)
            button.clicked.connect(self.handle_button_click)
            self.buttons.append(button)
            self.layout.addWidget(button)

        # Set the first button as checked by default
        self.buttons[0].setChecked(True)

        self.setStyleSheet(
            """
            SegmentedButton QPushButton {
                border-radius: 4px;
                background-color: #f0f0f0;
                color: #333;
                padding: 4px 16px;
            }

            SegmentedButton QPushButton:checked {
                background-color: #fff;
                border: none;
            }
            """
        )            

    def handle_button_click(self, checked):
        # Get the button that emitted the signal
        button = self.sender()
        
        # Deselect all other buttons when a button is clicked
        for other_button in self.buttons:
            if other_button != button:
                other_button.setChecked(False)        

        # Ensure the clicked button remains checked
        button.setChecked(True)

# class PrimaryActionButton(QPushButton):
#     def __init__(self, text=""):
#         super().__init__(text)
#         self.setStyleSheet(
#             """
#             QPushButton {
#                 background-color: #417d9d;
#                 color: white;
#                 border-radius: 5px;
#                 padding: 5px 20px;
#             }
#             QPushButton:hover {
#                 background-color: #34647d; /* Change to a darker shade on hover */
#             }
#             QPushButton:disabled {
#                 background-color: #aac6d9; /* Lighter shade for disabled state */
#                 color: #7a7a7a; /* Adjust text color for better readability */
#             }
#             """
            
#         )

class PrimaryActionButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.default_stylesheet = (
            """
            QPushButton {
                background-color: #417d9d;
                color: white;
                border-radius: 5px;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #34647d; /* Change to a darker shade on hover */
            }
            QPushButton:disabled {
                background-color: #aac6d9; /* Lighter shade for disabled state */
                color: #7a7a7a; /* Adjust text color for better readability */
            }
            """
        )
            
        self.highlighted_stylesheet = (
            """
            QPushButton {
                background-color: #2c566c; /* Darker background for highlighted state */
                color: white;
                border-radius: 5px;
                padding: 5px 20px;
            }
            """	
        )

        self.setStyleSheet(self.default_stylesheet)

    def set_highlighted(self, highlighted: bool):
        if highlighted:
            self.setStyleSheet(self.highlighted_stylesheet)
        else:
            self.setStyleSheet(self.default_stylesheet)

# class SecondaryActionButton(QPushButton):
#     def __init__(self, text=""):
#         super().__init__(text)
#         self.setStyleSheet(
#             """
#             QPushButton {
#                 background-color: #c1e5f5;
#                 color: #417d9d;
#                 border-radius: 5px;
#                 padding: 5px 20px;
#             }
#             QPushButton:hover {
#                 background-color: #a9d8f3; /* Darker shade on hover */
#             }
#             QPushButton:disabled {
#                 background-color: #e6f3f8; /* Lighter shade for disabled state */
#                 color: #7a7a7a; /* Adjust text color for better readability */
#             }
#             """
#         )

class SecondaryActionButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.default_stylesheet = """
            QPushButton {
                background-color: #c1e5f5;
                color: #417d9d;
                border-radius: 5px;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #a9d8f3; /* Darker shade on hover */
            }
            QPushButton:disabled {
                background-color: #e6f3f8; /* Lighter shade for disabled state */
                color: #7a7a7a; /* Adjust text color for better readability */
            }
        """
        self.highlighted_stylesheet = """
            QPushButton {
                background-color: #a9d8f3; /* Darker background for highlighted state */
                color: #417d9d;
                border-radius: 5px;
                padding: 5px 20px;
            }
        """
        self.setStyleSheet(self.default_stylesheet)

    def set_highlighted(self, highlighted: bool):
        if highlighted:
            self.setStyleSheet(self.highlighted_stylesheet)
        else:
            self.setStyleSheet(self.default_stylesheet)

class TertiaryActionButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #ebf3f7;
                color: #417d9d;
                border-radius: 5px;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #d9e8f2; /* Slightly darker shade on hover */
            }
            QPushButton:disabled {
                background-color: #f5f9fc; /* Lighter shade for disabled state */
                color: #7a7a7a; /* Adjust text color for better readability */
            }            
            """
        )

class DestructiveActionButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: #417d9d;
                border-radius: 5px;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #ffcccc; /* Light red shade on hover */
            }
            QPushButton:disabled {
                background-color: #f2f2f2; /* Lighter shade for disabled state */
                color: #7a7a7a; /* Adjust text color for better readability */
            }
            """
        ) 

class InfoFrame(QFrame):
    def __init__(self, exam_name, model_name):  
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("""
            InfoFrame {
                background-color: white; /* Background color */
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """)

        # Add labels for each section
        section1_layout = QHBoxLayout()
        section1_text_layout = QVBoxLayout()
        section1_header = HeaderLabel("Examination")
        self.section1_text = QLabel(exam_name)
        self.section1_text.setStyleSheet("padding: 0; margin: 0;")
        self.section1_text.setContentsMargins(0, 0, 0, 0)
        section1_text_layout.addWidget(section1_header)
        section1_text_layout.addWidget(self.section1_text)
        # reduce vertical space between header and text
        section1_text_layout.setContentsMargins(0, 0, 0, 0)
        section1_text_layout.setSpacing(0)
        self.section1_stop_button = SecondaryActionButton("Stop")
        # change alignment of button
        self.section1_stop_button.setFixedWidth(100)
        section1_layout.addLayout(section1_text_layout)
        section1_layout.addWidget(self.section1_stop_button)
        layout.addLayout(section1_layout)

        # Add a horizontal line between sections
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Add labels for each section
        section2_layout = QHBoxLayout()
        section2_text_layout = QVBoxLayout()
        section2_header = HeaderLabel("Model")
        self.section2_text = QLabel(model_name)
        section2_text_layout.addWidget(section2_header)
        section2_text_layout.addWidget(self.section2_text)
        section1_text_layout.setContentsMargins(0, 0, 0, 0)
        section2_text_layout.setSpacing(0)
        self.section2_view_button = SecondaryActionButton("View")
        self.section2_view_button.setFixedWidth(100)
        section2_layout.addLayout(section2_text_layout)
        section2_layout.addWidget(self.section2_view_button)
        layout.addLayout(section2_layout)


# class InfoFrame(QFrame):
#     def __init__(self, exam_name, model_name):  
#         super().__init__()
#         layout = QVBoxLayout()
#         self.setLayout(layout)
#         self.setStyleSheet("""
#             InfoFrame {
#                 background-color: white; /* Background color */
#                 border: 1px solid #BFBFBF; /* Border color and thickness */
#                 border-radius: 5px; /* Radius for rounded corners */
#             }
#         """)

#         # Add labels for each section
#         section1_header = HeaderLabel("Examination")
#         self.section1_text = QLabel(exam_name)
#         layout.addWidget(section1_header)
#         layout.addWidget(self.section1_text)
#         section1_button_layout = QHBoxLayout()
#         section1_save_button = SecondaryActionButton("Save")
#         section1_edit_button = TertiaryActionButton("Edit")
#         self.section1_stop_button = DestructiveActionButton("Stop")
#         # section1_save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         # section1_edit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         # self.section1_stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         # print size of buttons
#         section1_button_layout.addWidget(section1_save_button, 1)
#         section1_button_layout.addWidget(section1_edit_button, 1)
#         spacer = QSpacerItem(section1_save_button.sizeHint().width(), section1_save_button.sizeHint().height(), QSizePolicy.Expanding, QSizePolicy.Minimum)
#         section1_button_layout.addItem(spacer)
#         section1_button_layout.addWidget(self.section1_stop_button, 1)
#         layout.addLayout(section1_button_layout)
#         # Add a horizontal line between sections
#         line = QFrame()
#         line.setFrameShape(QFrame.HLine)
#         line.setFrameShadow(QFrame.Sunken)
#         layout.addWidget(line)

#         section2_header = HeaderLabel("Model")
#         self.section2_text = QLabel(model_name)
#         section2_button_layout = QHBoxLayout()
#         self.section2_view_button = SecondaryActionButton("View")
#         section2_edit_button = TertiaryActionButton("Edit")
#         section2_button_layout.addWidget(self.section2_view_button,1)
#         section2_button_layout.addWidget(section2_edit_button,1)
#         section2_button_layout.addItem(spacer)
#         layout.addWidget(section2_header)
#         layout.addWidget(self.section2_text)
#         layout.addLayout(section2_button_layout)



class HeaderLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        self.setStyleSheet("color: #7F7F7F")
        self.setAlignment(Qt.AlignLeft)
