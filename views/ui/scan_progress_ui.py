from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QProgressBar

from utils.logger import log
from views.styled_widgets import SecondaryActionButton, DestructiveActionButton


class ScanProgressInfoFrame(QFrame):
    def __init__(self, scanner):
        super().__init__()
        self.setStyleSheet(
            """
            ScanProgressInfoFrame {
                border: 1px solid #BFBFBF; /* Border color and thickness */
                border-radius: 5px; /* Radius for rounded corners */
            }
        """
        )
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.scanner = scanner
        self._createProgressBar()
        self._createScanButtons()

    @property
    def scanProgressBar(self):
        return self._scanProgressBar

    @property
    def startScanButton(self):
        return self._startScanButton

    @property
    def stopScanButton(self):
        return self._stopScanButton

    def _createProgressBar(self):
        scanProgressBarLayout = QHBoxLayout()

        self._scanProgressBar = QProgressBar()

        self._scanProgressBar.setValue(0)
        # Set a custom stylesheet for the progress bar to customize its appearance
        self._scanProgressBar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #6bcc7a; /* Set the color of the progress bar chunk */
            }
        """
        )
        scanProgressBarLayout.addWidget(self._scanProgressBar)

        self.layout.addLayout(scanProgressBarLayout)

    def save_state(self):
        return {"progress": self._scanProgressBar.value()}

    def restore_state(self, state):
        if state is not None:
            self._scanProgressBar.setValue(state.get("progress", 0))
        else:
            log.warning("No state found for ScanProgressInfoFrame.")

    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()

        self._startScanButton = SecondaryActionButton("Start Scan")
        scanButtonsLayout.addWidget(self._startScanButton)

        self._stopScanButton = DestructiveActionButton("Stop Scan")
        scanButtonsLayout.addWidget(self._stopScanButton)

        self.layout.addLayout(scanButtonsLayout)
