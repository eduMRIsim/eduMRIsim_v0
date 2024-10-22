from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QLabel,
    QWidget,
    QGridLayout,
)

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
        self.scanner.scan_progress.connect(self.update_scan_progress)

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
        progressContainer = QWidget()
        progressLayout = QGridLayout()
        progressLayout.setContentsMargins(0, 0, 0, 0)
        progressLayout.setSpacing(0)
        progressContainer.setLayout(progressLayout)
        self._scanProgressBar = QProgressBar()
        self._scanProgressBar.setTextVisible(False)
        self._scanProgressBar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #6bcc7a; /* Set the color of the progress bar chunk */
            }
            """
        )
        self._scanEtaLabel = QLabel()
        self._scanEtaLabel.setText("Time Remaining: 00:00")
        self._scanEtaLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the text
        # Set label to have a transparent background
        self._scanEtaLabel.setStyleSheet(
            """
            QLabel {
                background-color: transparent;
                font-size: 14px;
                color: #333333;
            }
            """
        )

        # Add both widgets
        progressLayout.addWidget(self._scanProgressBar, 0, 0)
        progressLayout.addWidget(self._scanEtaLabel, 0, 0)

        # Add the progress container to the main layout
        self.layout.addWidget(progressContainer)

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

    # Sync progress bar to scan progress
    def update_scan_progress(self, remaining_time: float, progress_percentage: float):
        """Update the progress bar & ETA timer during scanning."""

        self._scanProgressBar.setValue(int(progress_percentage))

        if remaining_time <= 0:
            # Scan is complete
            self._scanEtaLabel.setText("Scan Complete")
        else:
            seconds_remaining = int(round(remaining_time / 1000))
            # Format the time as mm:ss
            minutes, seconds = divmod(seconds_remaining, 60)
            eta_display = f"Time Remaining: {minutes:02d}:{seconds:02d}"
            self._scanEtaLabel.setText(eta_display)

    @pyqtSlot()
    def on_scan_started(self):
        """Slot to handle scan started signal."""
        self._startScanButton.setText("Fast Forward")

    @pyqtSlot()
    def on_scan_finished(self):
        """Slot to handle scan finished signal."""
        self._startScanButton.setText("Start Scan")
