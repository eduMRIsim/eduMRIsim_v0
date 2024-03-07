from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton

class ParameterFormLayout(QGridLayout):
    def __init__(self):
        super().__init__()
        self.scanTechniqueComboBox = QComboBox()
        self.scanTechniqueComboBox.addItems(["GE", "SE"])
        self.TELineEdit = QLineEdit()
        self.TRLineEdit = QLineEdit()
        self.TILineEdit = QLineEdit()
        #self.sliceLineEdit = QLineEdit()


        self.scanTechniqueMessageLabel = QLabel()
        self.scanTechniqueMessageLabel.setStyleSheet("color: red")    
        self.TEMessageLabel = QLabel()
        self.TEMessageLabel.setStyleSheet("color: red")
        self.TRMessageLabel = QLabel()
        self.TRMessageLabel.setStyleSheet("color: red")
        self.TIMessageLabel = QLabel()
        self.TIMessageLabel.setStyleSheet("color: red")
        #self.sliceMessageLabel = QLabel()
        #self.sliceMessageLabel.setStyleSheet("color: red")

        self.setHorizontalSpacing(0)

        self.addWidget(QLabel("Scan Technique:"), 0, 0, Qt.AlignLeft)
        self.addWidget(self.scanTechniqueComboBox, 0, 1, Qt.AlignLeft)
        self.addWidget(self.scanTechniqueComboBox, 0, 2, Qt.AlignLeft)

        self.addWidget(QLabel("TE:"), 1, 0, Qt.AlignLeft)
        self.addWidget(self.TELineEdit, 1, 1, Qt.AlignLeft)
        self.addWidget(self.TEMessageLabel, 1, 2, Qt.AlignLeft)

        self.addWidget(QLabel("TR:"), 2, 0, Qt.AlignLeft)
        self.addWidget(self.TRLineEdit, 2, 1, Qt.AlignLeft)
        self.addWidget(self.TRMessageLabel, 2, 2, Qt.AlignLeft)

        self.addWidget(QLabel("TI:"), 3, 0, Qt.AlignLeft)
        self.addWidget(self.TILineEdit, 3, 1, Qt.AlignLeft)
        self.addWidget(self.TIMessageLabel, 3, 2, Qt.AlignLeft)

        #self.addWidget(QLabel("slice:"), 4, 0, Qt.AlignLeft)
        #self.addWidget(self.sliceLineEdit, 4, 1, Qt.AlignLeft)
        #self.addWidget(self.sliceMessageLabel, 4, 2, Qt.AlignLeft)

        self.setColumnStretch(0, 1)
        self.setColumnStretch(1, 2)
        self.setColumnStretch(2, 2)




if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget

    class TestWindow(QWidget):
        def __init__(self):
            super().__init__()

            self.form_layout = ParameterFormLayout()

            toggle_button = QPushButton('Toggle Read-Only')
            toggle_button.clicked.connect(self.toggleParameterFormLayoutEnabled)

            layout = QVBoxLayout(self)
            layout.addLayout(self.form_layout)
            layout.addWidget(toggle_button)

        def toggleParameterFormLayoutEnabled(self):
            self.form_layout.setEnabled(False)

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())