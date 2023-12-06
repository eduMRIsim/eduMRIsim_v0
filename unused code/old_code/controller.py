from view import NewExaminationDialog, LoadExaminationDialog, ViewModelDialog
from examination import Examination
from model import Model
from load import Loader
import numpy as np 

class Controller:

    def __init__(self, view, scanner):
        self._view = view
        self._scanner = scanner
        self._connectSignalsandSlots()

    def _connectSignalsandSlots(self):
        self.new_examination_button = self._view.getNewExaminationButton()
        model_names = self.getModelNames()
        self.new_examination_dialog = NewExaminationDialog(model_names)
        self.new_examination_button.clicked.connect(lambda:self.new_examination_dialog.exec())

        self.new_examination_OK_button = self.new_examination_dialog.getOkButton()
        self.new_examination_OK_button.clicked.connect(self.newExaminationOKButtonPressed)

        self.new_examination_cancel_button = self.new_examination_dialog.getCancelButton()
        self.new_examination_cancel_button.clicked.connect(self.newExaminationCancelButtonPressed)

        load_examination_button = self._view.getLoadExaminationButton()
        load_examination_button.clicked.connect(lambda: LoadExaminationDialog().exec())

        view_model_button = self._view.getViewModelButton()
        view_model_button.clicked.connect(lambda: ViewModelDialog(self.model).exec())

    def getModelNames(self):
        loader = Loader()
        jsonFilePath = 'models/models.json'
        self.model_data = loader.load_model(jsonFilePath)
        model_names = list(self.model_data.keys())
        return model_names
    
    def newExaminationOKButtonPressed(self):
        exam_name = self.new_examination_dialog.examNameLineEdit.text()
        model_name = self.new_examination_dialog.modelComboBox.currentText()
        selected_model_info = self.model_data.get(model_name)
        description = selected_model_info["description"]
        t1map_file_path = selected_model_info["T1mapFilePath"]
        t2map_file_path = selected_model_info["T2mapFilePath"]
        pdmap_file_path = selected_model_info["PDmapFilePath"]

        t1map = np.load(t1map_file_path)
        t2map = np.load(t2map_file_path)
        pdmap = np.load(pdmap_file_path)

        self.examination = Examination(exam_name)
        self.model = Model(model_name, description, t1map, t2map, pdmap)
        self.examination.set_model(self.model)
        self._scanner.set_examination(self.examination)
        self.new_examination_dialog.accept() # Close the dialog
        self._view.examination_info_stacked_layout.setCurrentIndex(1)
        self._view.examination_info_stacked_layout.setTextExaminationInfoFrame(exam_name, model_name)
        add_scan_item_button = self._view.getAddScanItemButton()
        add_scan_item_button.setVisible(True)
    
    def newExaminationCancelButtonPressed(self):
        self.new_examination_dialog.accept() # Close the dialog
