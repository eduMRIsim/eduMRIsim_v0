from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from load import Loader
from examination import Examination
from model import Model
import numpy as np


class MainController(QObject):
    populate_modelComboBox = pyqtSignal(list)
    open_newExaminationDialog = pyqtSignal()
    close_newExaminationDialog = pyqtSignal()
    start_new_examination = pyqtSignal(str, str)
    show_examCardTabWidget = pyqtSignal()
    populate_examCardListView = pyqtSignal(dict)
    update_scanlistListWidget = pyqtSignal(list)
    populate_parameterFormLayout = pyqtSignal(dict, dict)
    open_viewModelDialog = pyqtSignal(Model) 

    def __init__(self, scanner):
        super().__init__()

        self._scanner = scanner
        self._loader = Loader()

    @property
    def scanner(self):
        return self._scanner

    @pyqtSlot()
    def handle_newExaminationButton_clicked(self):
        jsonFilePath = 'repository/models/models.json'
        self.model_data = self._loader.load(jsonFilePath)
        model_names = list(self.model_data.keys())
        self.populate_modelComboBox.emit(model_names)
        self.open_newExaminationDialog.emit() 

    @pyqtSlot()
    def handle_newExaminationOkButton_clicked(self, exam_name, model_name):
        selected_model_data = self.model_data.get(model_name)
        description = selected_model_data["description"]
        t1map_file_path = selected_model_data["T1mapFilePath"]
        t2map_file_path = selected_model_data["T2mapFilePath"]
        pdmap_file_path = selected_model_data["PDmapFilePath"]
        t1map = np.load(t1map_file_path)
        t2map = np.load(t2map_file_path)
        pdmap = np.load(pdmap_file_path)
        model = Model(model_name, description, t1map, t2map, pdmap)
        self.scanner.start_examination(exam_name, model)
        self.close_newExaminationDialog.emit()
        self.start_new_examination.emit(exam_name, model_name)
        
    @pyqtSlot()
    def handle_addScanItemButton_clicked(self):
        jsonFilePath = 'repository/exam_cards/exam_cards.json'
        self.exam_card_data = self._loader.load(jsonFilePath)
        self.show_examCardTabWidget.emit()
        self.populate_examCardListView.emit(self.exam_card_data)

    def handle_add_to_scanlist(self, name, scan_parameters):
        self.scanner.examination.add_scan_item(name, scan_parameters)
        self.update_scanlistListWidget.emit(self.scanner.scanlist)

    def handle_scanlistListWidget_dclicked(self, index):
        self.scanner.current_scan_item = self.scanner.scanlist[index]
        self.populate_parameterFormLayout.emit(self.scanner.current_scan_item.scan_parameters, {})

    def handle_scanParametersCancelChangesButton_clicked(self):
        self.populate_parameterFormLayout.emit(self.scanner.current_scan_item.scan_parameters, {})

    def handle_viewModelButton_clicked(self):
        self.open_viewModelDialog.emit(self.scanner.model)

    def handle_scanParametersSaveChangesButton_clicked(self, scan_parameters):
        [valid, messages] = self.scanner.current_scan_item.validate_scan_parameters(scan_parameters)
        if valid == True:
            self.populate_parameterFormLayout.emit(self.scanner.current_scan_item.scan_parameters, messages)
        else:
            self.populate_parameterFormLayout.emit(scan_parameters, messages)