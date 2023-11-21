from PyQt5.QtWidgets import  QComboBox, QDialog, QFormLayout, QHBoxLayout, QPushButton, QLineEdit, QVBoxLayout


class NewExaminationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New examination")
        self.layout = QVBoxLayout()

        self._createModelComboBox()
        self._createExamInfoForm()
        self._newExaminationOkButton = QPushButton("OK")
        self._newExaminationCancelButton = QPushButton("Cancel")

        self.layout.addLayout(self.examInfoForm)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self._newExaminationOkButton)
        horizontal_layout.addWidget(self._newExaminationCancelButton)
        self.layout.addLayout(horizontal_layout)

        self.setLayout(self.layout)

    @property
    def newExaminationOkButton(self):
        return self._newExaminationOkButton
    
    @property
    def newExaminationCancelButton(self):
        return self._newExaminationCancelButton
    
    @property
    def modelComboBox(self):
        return self._modelComboBox
    
    @property
    def uploadModelButton(self):
        return self._uploadModelButton
    
    @property
    def examNameLineEdit(self):
        return self._examNameLineEdit

    
    def _createModelComboBox(self):
        self._modelComboBox = QComboBox()

    def _createExamInfoForm(self):
        self.examInfoForm = QFormLayout()
        horizontal_layout = QHBoxLayout()
        self._uploadModelButton = QPushButton("Upload")
        horizontal_layout.addWidget(self._modelComboBox)
        horizontal_layout.addWidget(self._uploadModelButton)
        self.examInfoForm.addRow("Select model:", horizontal_layout)
        self._examNameLineEdit = QLineEdit()
        self.examInfoForm.addRow("Exam name:", self._examNameLineEdit)

