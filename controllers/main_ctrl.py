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

    def __init__(self, scanner):
        super().__init__()

        self._scanner = scanner

    @pyqtSlot()
    def handle_newExaminationButton_clicked(self):
        loader = Loader()
        jsonFilePath = 'models/models.json'
        self.model_data = loader.load(jsonFilePath)
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
        self.examination = Examination(exam_name)
        self.model = Model(model_name, description, t1map, t2map, pdmap)
        self.examination.model = self.model
        self._scanner.examination = self.examination
        self.close_newExaminationDialog.emit()
        self.start_new_examination.emit(exam_name, model_name)
        
    @pyqtSlot()
    def handle_addScanItemButton_clicked(self):
        loader = Loader()
        jsonFilePath = 'exam_cards/exam_cards.json'
        self.exam_card_data = loader.load(jsonFilePath)
        self.show_examCardTabWidget.emit()
        self.populate_examCardListView.emit(self.exam_card_data)

    def handle_add_to_scanlist(self, key, scan_item):
        self.examination.scanlist.add_scan_item(key, scan_item)
        self.update_scanlistListWidget.emit(self.examination.scanlist.scanlist)
