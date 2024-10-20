from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt, pyqtSlot

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
        self._createEtaLabel()
        self._createScanButtons()
        self.scanner.scan_started_signal.connect(self.on_scan_started)
        self.scanner.scan_finished_signal.connect(self.on_scan_finished)

    @property
    def scanEtaLabel(self):
        return self._scanEtaLabel

    @property
    def startScanButton(self):
        return self._startScanButton

    @property
    def stopScanButton(self):
        return self._stopScanButton

    def _createEtaLabel(self):
        # Create a horizontal layout to hold the ETA label
        scanEtaLabelLayout= QHBoxLayout()

        # Create a QLabel to display the ETA
        self._scanEtaLabel = QLabel()
        self._scanEtaLabel.setText("Time Remaining: 00:00")  # Initialize with default text
        self._scanEtaLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the text

        # Optionally, set a custom stylesheet for the label to customize its appearance
        self._scanEtaLabel.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            """
        )

        # Add the ETA label to the layout
        scanEtaLabelLayout.addWidget(self._scanEtaLabel)

        # Add the layout to the parent layout
        self.layout.addLayout(scanEtaLabelLayout)

    def save_state(self):
        return {"progress": self._scanEtaLabel.text()}

    def restore_state(self, state):
        if state is not None:
            self._scanEtaLabel.setText(state.get("progress", 0))
        else:
            log.warning("No state found for ScanProgressInfoFrame.")

    def _createScanButtons(self):
        scanButtonsLayout = QHBoxLayout()

        self._startScanButton = SecondaryActionButton("Start Scan")
        scanButtonsLayout.addWidget(self._startScanButton)

        self._stopScanButton = DestructiveActionButton("Stop Scan")
        scanButtonsLayout.addWidget(self._stopScanButton)

        self.layout.addLayout(scanButtonsLayout)

    @pyqtSlot()
    def on_scan_started(self):
        """Slot to handle scan started signal."""
        self._startScanButton.setText("Fast Forward")

    @pyqtSlot()
    def on_scan_finished(self):
        """Slot to handle scan finished signal."""
        self._startScanButton.setText("Start Scan")

