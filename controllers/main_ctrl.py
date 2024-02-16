from views.new_examination_dialog_ui import NewExaminationDialog
from views.load_examination_dialog_ui import LoadExaminationDialog
from simulator.load import Loader
from views.qmodels import DictionaryModel
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon
from views.view_model_dialog_ui import ViewModelDialog
import numpy as np
from simulator.model import Model 
from simulator.scan_item import ScanItemStatusEnum



class MainController:
    def __init__(self, scanner, ui) -> None:
        self.scanner = scanner
        self._ui = ui

        self._load_examination_dialog_ui = LoadExaminationDialog()
        self._new_examination_dialog_ui = NewExaminationDialog()

        self._ui.loadExaminationButton.clicked.connect(lambda: self._load_examination_dialog_ui.exec())
        self._ui.newExaminationButton.clicked.connect(self.handle_newExaminationButton_clicked)
        self._ui.addScanItemButton.clicked.connect(self.handle_addScanItemButton_clicked)
        self._ui.examCardListView.doubleClicked.connect(self.handle_examCardListView_dclicked)
        self._ui.scanlistListWidget.itemDoubleClicked.connect(self.handle_scanlistListWidget_dclicked)
        self._ui.viewModelButton.clicked.connect(self.handle_viewModelButton_clicked)
        self._ui.stopExaminationButton.clicked.connect(lambda: self._ui.state.enter_idle_state(self._ui))
        self._ui.parameterFormLayout.formActivatedSignal.connect(self.handle_parameter_form_activated)
        self._ui.scanParametersCancelChangesButton.clicked.connect(self.handle_scanParametersCancelChangesButton_clicked)
        self._ui.scanParametersSaveChangesButton.clicked.connect(self.handle_scanParametersSaveChangesButton_clicked)
        self._ui.scanParametersResetButton.clicked.connect(self.handle_scanParametersResetButton_clicked)
        self._ui.startScanButton.clicked.connect(self.handle_startScanButton_clicked)  

        self._new_examination_dialog_ui.newExaminationCancelButton.clicked.connect(lambda: self._new_examination_dialog_ui.accept())
        self._new_examination_dialog_ui.newExaminationOkButton.clicked.connect(lambda: self.handle_newExaminationOkButton_clicked(self._new_examination_dialog_ui.examNameLineEdit.text(), self._new_examination_dialog_ui.modelComboBox.currentText()))      

    def handle_newExaminationButton_clicked(self):
        jsonFilePath = 'repository/models/models.json'
        self.model_data = Loader.load(jsonFilePath)
        model_names = list(self.model_data.keys())
        self.populate_modelComboBox(model_names)
        self._new_examination_dialog_ui.exec()    

    def populate_modelComboBox(self, list):
        self._new_examination_dialog_ui.modelComboBox.clear()
        self._new_examination_dialog_ui.modelComboBox.addItems(list)

    def handle_addScanItemButton_clicked(self):
        jsonFilePath = 'repository/exam_cards/exam_cards.json'
        self.exam_card_data = Loader.load(jsonFilePath)
        self._ui.editingStackedLayout.setCurrentIndex(1)
        self.populate_examCardListView(self.exam_card_data)       

    def populate_examCardListView(self, exam_card_data):
        self.exam_card_qmodel = DictionaryModel(exam_card_data)
        self._ui.examCardListView.setModel(self.exam_card_qmodel)

    def handle_examCardListView_dclicked(self, index):
        scan_item = self._ui.examCardListView.model().get_data(index)
        key = self._ui.examCardListView.model().itemFromIndex(index).text()
        self.handle_add_to_scanlist(key, scan_item)

    def handle_add_to_scanlist(self, name, scan_parameters):
        self.scanner.scanlist.add_scan_item(name, scan_parameters)
        self.update_scanlistListWidget(self.scanner.scan_items)
    
    def update_scanlistListWidget(self, list):
        self._ui.scanlistListWidget.clear()
        #self._ui.scanlistListWidget.addItems([item.name for item in list])

        #test icon code
        for item in list:
            list_item = QListWidgetItem(item.name)
            if item.status == ScanItemStatusEnum.READY_TO_SCAN:
                list_item.setIcon(QIcon("resources/icons/checkmark-outline.png"))  
            elif item.status == ScanItemStatusEnum.BEING_MODIFIED:
                list_item.setIcon(QIcon("resources/icons/edit-outline.png"))
            elif item.status == ScanItemStatusEnum.INVALID:
                list_item.setIcon(QIcon("resources/icons/alert-circle-outline.png"))
            elif item.status == ScanItemStatusEnum.COMPLETE:
                list_item.setIcon(QIcon("resources/icons/checkmark-circle-2-outline.png"))
            self._ui.scanlistListWidget.addItem(list_item)  
        try:
            self._ui.testInfoLabel.setText(self.scanner.current_scan_item.status.name)
        except:
            self._ui.testInfoLabel.setText("No current scan item")

    def handle_scanlistListWidget_dclicked(self, item):
        self._ui.editingStackedLayout.setCurrentIndex(0)    
        index = self._ui.scanlistListWidget.row(item)
        self.scanner.scanlist.current_scan_item_index = index
        self.populate_parameterFormLayout()
        if self.scanner.current_scan_item.status == ScanItemStatusEnum.READY_TO_SCAN:
            self._ui.state.enter_ready_to_scan_state(self._ui)
        elif self.scanner.current_scan_item.status == ScanItemStatusEnum.BEING_MODIFIED:
            self._ui.state.enter_being_modified_state(self._ui)
        elif self.scanner.current_scan_item.status == ScanItemStatusEnum.INVALID:
            self._ui.state.enter_invalid_state(self._ui)
        elif self.scanner.current_scan_item.status == ScanItemStatusEnum.COMPLETE:
            self._ui.state.enter_scan_complete_state(self._ui)
        self._ui.testInfoLabel.setText(self.scanner.current_scan_item.status.name)


    def populate_parameterFormLayout(self):
        self._ui.parameterFormLayout.setData(self.scanner.current_scan_item.scan_parameters, self.scanner.current_scan_item.messages)
             
    def handle_viewModelButton_clicked(self):
        view_model_dialog = ViewModelDialog(self.scanner.model)
        view_model_dialog.exec()    

    def handle_parameter_form_activated(self):
        self._ui.state.enter_being_modified_state(self._ui)
        self.scanner.current_scan_item.status = ScanItemStatusEnum.BEING_MODIFIED
        self.update_scanlistListWidget(self.scanner.scan_items)

    def handle_scanParametersCancelChangesButton_clicked(self):
        self.populate_parameterFormLayout()
        if self.scanner.current_scan_item.valid == True:
            self._ui.state.enter_ready_to_scan_state(self._ui)
            self.scanner.current_scan_item.status = ScanItemStatusEnum.READY_TO_SCAN
        else:
            self._ui.state.enter_invalid_state(self._ui)
            self.scanner.current_scan_item.status = ScanItemStatusEnum.INVALID
        self.update_scanlistListWidget(self.scanner.scan_items)
        

    def handle_scanParametersSaveChangesButton_clicked(self, scan_parameters):
        scan_parameters = self._ui.parameterFormLayout.getData()
        self.scanner.current_scan_item.validate_scan_parameters(scan_parameters)
        self.populate_parameterFormLayout()
        if self.scanner.current_scan_item.valid == True:
            self._ui.state.enter_ready_to_scan_state(self._ui)
        else:
            self._ui.state.enter_invalid_state(self._ui)
        self.update_scanlistListWidget(self.scanner.scan_items)

    def handle_scanParametersResetButton_clicked(self):
        self.scanner.current_scan_item.scan_parameters = self.scanner.current_scan_item.scan_parameters_original
        self.scanner.current_scan_item.messages = {}
        self.populate_parameterFormLayout()
        self.scanner.current_scan_item.status = ScanItemStatusEnum.READY_TO_SCAN
        self._ui.state.enter_ready_to_scan_state(self._ui)
        self.update_scanlistListWidget(self.scanner.scan_items)

    def handle_startScanButton_clicked(self):
        array = self.scanner.scan()
        self._ui.scannedImageFrame.setArray(array)
        self._ui.scannedImageFrame.displayArray()
        self.scanner.current_scan_item.status = ScanItemStatusEnum.COMPLETE
        self._ui.state.enter_scan_complete_state(self._ui)
        self.update_scanlistListWidget(self.scanner.scan_items)

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
        self._new_examination_dialog_ui.accept()
        self._ui.state.enter_exam_state(self._ui)
        self._ui.examinationNameLabel.setText(exam_name)
        self._ui.modelNameLabel.setText(model_name)        