from views.new_examination_dialog_ui import NewExaminationDialog
from views.load_examination_dialog_ui import LoadExaminationDialog
from simulator.load import Loader
from views.qmodels import DictionaryModel
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon
from views.view_model_dialog_ui import ViewModelDialog
import numpy as np
from simulator.model import Model 
from simulator.scanlist import ScanlistElementStatusEnum
import views.UI_MainWindowState as UI_state 


class MainController:
    def __init__(self, scanner, ui) -> None:
        self.scanner = scanner
        self._ui = ui

        self._load_examination_dialog_ui = LoadExaminationDialog()
        self._new_examination_dialog_ui = NewExaminationDialog() 

        self._ui.loadExaminationButton.clicked.connect(lambda: self._load_examination_dialog_ui.exec())
        self._ui.newExaminationButton.clicked.connect(self.handle_newExaminationButton_clicked)
        self._ui.addScanItemButton.clicked.connect(self.handle_addScanItemButton_clicked)
        self._ui.scanlistListWidget.dropEventSignal.connect(self.handle_add_to_scanlist)
        self._ui.scanlistListWidget.itemClicked.connect(self.handle_scanlistListWidget_dclicked)
        self._ui.viewModelButton.clicked.connect(self.handle_viewModelButton_clicked)
        self._ui.stopExaminationButton.clicked.connect(self.handle_stopExaminationButton_clicked)
        self._ui.parameterFormLayout.formActivatedSignal.connect(self.handle_parameterFormLayout_activated)
        self._ui.scanParametersCancelChangesButton.clicked.connect(self.handle_scanParametersCancelChangesButton_clicked)
        self._ui.scanParametersSaveChangesButton.clicked.connect(self.handle_scanParametersSaveChangesButton_clicked)
        self._ui.scanParametersResetButton.clicked.connect(self.handle_scanParametersResetButton_clicked)
        self._ui.startScanButton.clicked.connect(self.handle_startScanButton_clicked)  
        self._ui.scanPlanningWindow1.dropEventSignal.connect(self.handle_scanPlanningWindow1_dropped)
        self._ui.scanPlanningWindow2.dropEventSignal.connect(self.handle_scanPlanningWindow2_dropped)
        self._ui.scanPlanningWindow3.dropEventSignal.connect(self.handle_scanPlanningWindow3_dropped)

        self._new_examination_dialog_ui.newExaminationCancelButton.clicked.connect(lambda: self._new_examination_dialog_ui.accept())
        self._new_examination_dialog_ui.newExaminationOkButton.clicked.connect(lambda: self.handle_newExaminationOkButton_clicked(self._new_examination_dialog_ui.examNameLineEdit.text(), self._new_examination_dialog_ui.modelComboBox.currentText()))      

    def handle_newExaminationButton_clicked(self):
        jsonFilePath = 'repository/models/models.json'
        self.model_data = Loader.load(jsonFilePath)
        model_names = list(self.model_data.keys())
        self.populate_modelComboBox(model_names)
        self._new_examination_dialog_ui.exec()    

    def handle_stopExaminationButton_clicked(self):
        self.scanner.stop_examination()
        self._ui.parameterFormLayout.clearForm()
        self._ui.scanlistListWidget.clear()
        self._ui.scannedImageFrame.setArray(None)
        self._ui.scanPlanningWindow1.setArray(None)
        self._ui.scanPlanningWindow2.setArray(None)
        self._ui.scanPlanningWindow3.setArray(None)
        self._ui.scannedImageFrame.displayArray()
        self._ui.scanPlanningWindow1.displayArray()
        self._ui.scanPlanningWindow2.displayArray()
        self._ui.scanPlanningWindow3.displayArray()
        self._ui.state = UI_state.IdleState()
        self._ui.update_UI()

    def populate_modelComboBox(self, list):
        self._new_examination_dialog_ui.modelComboBox.clear()
        self._new_examination_dialog_ui.modelComboBox.addItems(list)

    def handle_addScanItemButton_clicked(self):
        jsonFilePath = 'repository/exam_cards/exam_cards.json'
        self.exam_card_data = Loader.load(jsonFilePath)
        self._ui.editingStackedLayout.setCurrentIndex(1)
        self.populate_examCardListView(self.exam_card_data)       
        self.update_scanlistListWidget(self.scanner.scanlist)

    def populate_examCardListView(self, exam_card_data):
        self.exam_card_qmodel = DictionaryModel(exam_card_data)
        self._ui.examCardListView.setModel(self.exam_card_qmodel)

    # def handle_examCardListView_dclicked(self, index):
    #     scan_parameters = self._ui.examCardListView.model().get_data(index)
    #     key = self._ui.examCardListView.model().itemFromIndex(index).text()
    #     self.handle_add_to_scanlist(key, scan_parameters)

    # def handle_add_to_scanlist(self, name, scan_parameters):
    #     self.scanner.scanlist.add_scanlist_element(name, scan_parameters)
    #     self.update_scanlistListWidget(self.scanner.scanlist)

    def handle_add_to_scanlist(self, selected_indexes):
        for index in selected_indexes:
            name = self._ui.examCardListView.model().itemFromIndex(index).text()
            scan_parameters = self._ui.examCardListView.model().get_data(index)
            self.scanner.scanlist.add_scanlist_element(name, scan_parameters)
        self.update_scanlistListWidget(self.scanner.scanlist)
    
    def update_scanlistListWidget(self, scanlist):
        self._ui.scanlistListWidget.clear()
        list = scanlist.scanlist_elements
        #test icon code
        for item in list:
            list_item = QListWidgetItem(item.name)
            if item.status == ScanlistElementStatusEnum.READY_TO_SCAN:
                list_item.setIcon(QIcon("resources/icons/checkmark-outline.png"))  
            elif item.status == ScanlistElementStatusEnum.BEING_MODIFIED:
                list_item.setIcon(QIcon("resources/icons/edit-outline.png"))
            elif item.status == ScanlistElementStatusEnum.INVALID:
                list_item.setIcon(QIcon("resources/icons/alert-circle-outline.png"))
            elif item.status == ScanlistElementStatusEnum.COMPLETE:
                list_item.setIcon(QIcon("resources/icons/checkmark-circle-2-outline.png"))
            self._ui.scanlistListWidget.addItem(list_item)  
        active_idx = self.scanner.scanlist.active_idx
        if active_idx is not None:
            current_list_item = self._ui.scanlistListWidget.item(active_idx)
            self._ui.scanlistListWidget.setCurrentItem(current_list_item)
        progress = scanlist.get_progress()
        self._ui.scanProgressBar.setValue(int(progress * 100))    

        # try:
        #     self._ui.testInfoLabel.setText(scanlist.active_scan_item.status.name)
        # except:
        #     self._ui.testInfoLabel.setText("No current scan item")

    def handle_scanlistListWidget_dclicked(self, item):
        self._ui.editingStackedLayout.setCurrentIndex(0)    
        index = self._ui.scanlistListWidget.row(item)
        self.scanner.scanlist.active_idx = index
        self._ui.scannedImageFrame.setArray(self.scanner.scanlist.active_scanlist_element.acquired_data)
        self._ui.scannedImageFrame.displayArray()
        current_list_item = self._ui.scanlistListWidget.item(index)
        self._ui.scanlistListWidget.setCurrentItem(current_list_item)
        self.populate_parameterFormLayout(self.scanner.scanlist.active_scan_item)
        self.handle_scanlist_element_status_change(self.scanner.scanlist.active_scanlist_element.status)
        #self._ui.testInfoLabel.setText(self.scanner.active_scan_item.status.name)

    def populate_parameterFormLayout(self, scan_item):
        self._ui.parameterFormLayout.setData(scan_item.scan_parameters, scan_item.messages)
             
    def handle_viewModelButton_clicked(self):
        view_model_dialog = ViewModelDialog(self.scanner.model)
        view_model_dialog.exec()    

    def handle_parameterFormLayout_activated(self):
        self.scanner.scanlist.active_scanlist_element.status = ScanlistElementStatusEnum.BEING_MODIFIED
        self._ui.state = UI_state.BeingModifiedState()
        self._ui.update_UI()
        self.update_scanlistListWidget(self.scanner.scanlist)

    def handle_scanParametersCancelChangesButton_clicked(self):
        self.scanner.scanlist.active_scan_item.cancel_changes()
        self.handle_scanlist_element_status_change(self.scanner.scanlist.active_scanlist_element.status)
        self.populate_parameterFormLayout(self.scanner.scanlist.active_scan_item)
        self.update_scanlistListWidget(self.scanner.scanlist)
        
    def handle_scanParametersSaveChangesButton_clicked(self):
        scan_parameters = self._ui.parameterFormLayout.getData()
        self.scanner.scanlist.active_scan_item.validate_scan_parameters(scan_parameters)
        self.populate_parameterFormLayout(self.scanner.scanlist.active_scan_item)
        self.handle_scanlist_element_status_change(self.scanner.scanlist.active_scanlist_element.status)
        self.update_scanlistListWidget(self.scanner.scanlist)

    def handle_scanParametersResetButton_clicked(self):
        self.scanner.scanlist.active_scan_item.reset_parameters()
        self.populate_parameterFormLayout(self.scanner.scanlist.active_scan_item)
        self.handle_scanlist_element_status_change(self.scanner.scanlist.active_scanlist_element.status)
        self.update_scanlistListWidget(self.scanner.scanlist)

    def handle_startScanButton_clicked(self):
        array = self.scanner.scan()
        self._ui.scannedImageFrame.setArray(array)
        self._ui.scannedImageFrame.displayArray()
        self.scanner.scanlist.active_scanlist_element.status = ScanlistElementStatusEnum.COMPLETE
        self._ui.state = UI_state.ScanCompleteState()
        self._ui.update_UI()
        self.update_scanlistListWidget(self.scanner.scanlist)

    def handle_newExaminationOkButton_clicked(self, exam_name, model_name):
        selected_model_data = self.model_data.get(model_name)
        description = selected_model_data.get("description", None)
        t1map_file_path = selected_model_data.get("T1mapFilePath", None)
        t2map_file_path = selected_model_data.get("T2mapFilePath", None)
        t2smap_file_path = selected_model_data.get("T2smapFilePath", None)
        pdmap_file_path = selected_model_data.get("PDmapFilePath", None)
        t1map = np.load(t1map_file_path)
        t1map_ms = t1map * 1000
        t2map = np.load(t2map_file_path)
        t2map_ms = t2map * 1000
        if t2smap_file_path is not None:
            t2smap = np.load(t2smap_file_path)
            t2smap_ms = t2smap * 1000
            self._ui.parameterFormLayout.setScanTechniqueComboBox(["spin echo", "gradient echo"])
        else: 
            t2smap_ms = None
            self._ui.parameterFormLayout.setScanTechniqueComboBox(["spin echo"])

        pdmap = np.load(pdmap_file_path)
        model = Model(model_name, description, t1map_ms, t2map_ms, t2smap_ms, pdmap)
        self.scanner.start_examination(exam_name, model)
        self._new_examination_dialog_ui.accept()
        self._ui.state = UI_state.ExamState()
        self._ui.update_UI()
        self._ui.examinationNameLabel.setText(exam_name)
        self._ui.modelNameLabel.setText(model_name)        


    def handle_scanlist_element_status_change(self, status):
        if status == ScanlistElementStatusEnum.READY_TO_SCAN:
            self._ui.state = UI_state.ReadyToScanState()
            self._ui.update_UI()
        elif status == ScanlistElementStatusEnum.BEING_MODIFIED:
            self._ui.state = UI_state.BeingModifiedState()
            self._ui.update_UI()
        elif status == ScanlistElementStatusEnum.INVALID:
            self._ui.state = UI_state.InvalidParametersState()
            self._ui.update_UI()
        elif status == ScanlistElementStatusEnum.COMPLETE:
            self._ui.state = UI_state.ScanCompleteState()
            self._ui.update_UI()

    def handle_scanPlanningWindow1_dropped(self, selected_index):
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        array = scanlist_element.acquired_data
        self._ui.scanPlanningWindow1.setArray(array)
        self._ui.scanPlanningWindow1.displayArray()
        self.update_scanlistListWidget(self.scanner.scanlist)


    def handle_scanPlanningWindow2_dropped(self, selected_index):
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        array = scanlist_element.acquired_data
        self._ui.scanPlanningWindow2.setArray(array)
        self._ui.scanPlanningWindow2.displayArray()
        self.update_scanlistListWidget(self.scanner.scanlist)


    def handle_scanPlanningWindow3_dropped(self, selected_index):
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        array = scanlist_element.acquired_data
        self._ui.scanPlanningWindow3.setArray(array)
        self._ui.scanPlanningWindow3.displayArray()
        self.update_scanlistListWidget(self.scanner.scanlist)
