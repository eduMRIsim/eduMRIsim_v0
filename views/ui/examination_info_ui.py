from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStackedLayout, QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy

from views.styled_widgets import PrimaryActionButton


class ExaminationInfoStackedLayout(QStackedLayout):
    def __init__(self, preExaminationInfoFrame, examinationInfoFrame):
        super().__init__()
        self._preExaminationInfoFrame = preExaminationInfoFrame
        self.examination_info_frame = examinationInfoFrame
        self.addWidget(self._preExaminationInfoFrame)
        self.addWidget(self.examination_info_frame)


class PreExaminationInfoFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            PreExaminationInfoFrame {
                background-color: white; /* Background color */
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """
        )
        self.layout = QVBoxLayout()
        self.welcomeLabel = QLabel(
            "Welcome to eduMRIsim!", alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.welcomeLabel.setStyleSheet("QLabel { font-size: 24px; }")
        self.setLayout(self.layout)
        self.layout.addWidget(self.welcomeLabel)
        self.horizontalLayout = QHBoxLayout()
        self._createNewExaminationButton()
        self._createLoadExaminationButton()
        self.layout.addLayout(self.horizontalLayout)

    def _createNewExaminationButton(self):
        self._newExaminationButton = PrimaryActionButton("New Examination")
        self._newExaminationButton.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.horizontalLayout.addWidget(
            self._newExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter
        )

    def _createLoadExaminationButton(self):
        self._loadExaminationButton = PrimaryActionButton("Load Examination")
        self._loadExaminationButton.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.horizontalLayout.addWidget(
            self._loadExaminationButton, alignment=Qt.AlignmentFlag.AlignCenter
        )

    @property
    def newExaminationButton(self):
        return self._newExaminationButton

    @property
    def loadExaminationButton(self):
        return self._loadExaminationButton
