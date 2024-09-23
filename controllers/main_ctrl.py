from PyQt5.QtCore import QSettings

from controllers.settings_mgr import SettingsManager
from views.new_examination_dialog_ui import NewExaminationDialog
from views.load_examination_dialog_ui import LoadExaminationDialog
#from views.view_model_dialog_ui import ViewModelDialog
from views.view_model_dialog_ui import ViewWindow
from views.qmodels import DictionaryModel
import views.UI_MainWindowState as UI_state 

from PyQt5.QtWidgets import QListWidgetItem, QApplication
from PyQt5.QtGui import QIcon

from simulator.load import load_json, load_model_data
from simulator.model import Model 
from simulator.scanlist import ScanItemStatusEnum

from events import EventEnum


class MainController:
    '''
    The MainController class defines what happens when the user interacts with the UI. It also defines in its update() method what happens when the scanner notifies the controller of changes, e.g., when a scan item is added to the scanlist, when the active scan item is changed, when the status of a scan item is changed, when the parameters of a scan item are changed, etc.'''

    def __init__(self, scanner, ui) -> None:
        self.scanner = scanner
        self.ui = ui

        self.load_examination_dialog_ui = LoadExaminationDialog()
        self.new_examination_dialog_ui = NewExaminationDialog() 

        # Connect signals to slots, i.e., define what happens when the user interacts with the UI by connecting signals from UI to functions that handle the signals.

        # Signals related to examinations 
        self.ui.loadExaminationButton.clicked.connect(lambda: self.load_examination_dialog_ui.open_file_dialog())
        self.ui.newExaminationButton.clicked.connect(self.handle_newExaminationButton_clicked)
        self.ui.stopExaminationButton.clicked.connect(self.handle_stopExaminationButton_clicked)

        # Signals related to scanlist
        self.ui.addScanItemButton.clicked.connect(self.handle_addScanItemButton_clicked)
        self.ui.scanlistListWidget.dropEventSignal.connect(self.handle_add_to_scanlist)
        self.ui.scanlistListWidget.itemClicked.connect(self.handle_scanlistListWidget_clicked)

        # Signals related to anatomical model
        self.ui.viewModelButton.clicked.connect(self.handle_viewModelButton_clicked)

        # Signals related to scan parameters
        #self.ui.parameterFormLayout.formActivatedSignal.connect(self.handle_parameterFormLayout_activated)
        #self.ui.scanParametersCancelChangesButton.clicked.connect(self.handle_scanParametersCancelChangesButton_clicked)
        #self.ui.scanParametersSaveChangesButton.clicked.connect(self.handle_scanParametersSaveChangesButton_clicked)
        #self.ui.scanParametersResetButton.clicked.connect(self.handle_scanParametersResetButton_clicked)

        # Signals related to scanning
        self.ui.startScanButton.clicked.connect(self.scanner.scan)  

        # Signals related to scan planning windows
        #self.ui.scanPlanningWindow1.dropEventSignal.connect(self.handle_scanPlanningWindow1_dropped)
        #self.ui.scanPlanningWindow2.dropEventSignal.connect(self.handle_scanPlanningWindow2_dropped)
        #self.ui.scanPlanningWindow3.dropEventSignal.connect(self.handle_scanPlanningWindow3_dropped)

        # Signals from new examination dialog
        self.new_examination_dialog_ui.newExaminationCancelButton.clicked.connect(lambda: self.new_examination_dialog_ui.accept())
        self.new_examination_dialog_ui.newExaminationOkButton.clicked.connect(lambda: self.handle_newExaminationOkButton_clicked(self.new_examination_dialog_ui.examNameLineEdit.text(), self.new_examination_dialog_ui.modelComboBox.currentText()))      

    def prepare_model_data(self):
        jsonFilePath = 'repository/models/models.json'
        self.model_data = load_json(jsonFilePath)
        model_names = list(self.model_data.keys())
        self.populate_modelComboBox(model_names)

    def handle_newExaminationButton_clicked(self):
        jsonFilePath = 'repository/models/models.json'
        self.model_data = load_json(jsonFilePath)
        model_names = list(self.model_data.keys())
        self.populate_modelComboBox(model_names)
        self.new_examination_dialog_ui.exec()

    def populate_modelComboBox(self, list):
        self.new_examination_dialog_ui.modelComboBox.clear()
        self.new_examination_dialog_ui.modelComboBox.addItems(list)

    def handle_stopExaminationButton_clicked(self):
        self.scanner.stop_examination()
        self.ui.state = UI_state.IdleState()

    def handle_addScanItemButton_clicked(self):
        jsonFilePath = 'repository/exam_cards/scan_items.json'
        self.exam_card_data = load_json(jsonFilePath)
        self.ui.editingStackedLayout.setCurrentIndex(1)
        self.populate_examCardListView(self.exam_card_data)       

    def populate_examCardListView(self, exam_card_data):
        self.exam_card_qmodel = DictionaryModel(exam_card_data)
        self.ui.examCardListView.setModel(self.exam_card_qmodel)

    def handle_add_to_scanlist_name(self, name):
        # load scan parameters json file
        scan_parameters = load_json("scan_parameters/scan_parameters.json")

    def handle_add_to_scanlist(self, selected_indexes):
        # Executed when the user drags and drops items from the examCardListView to the scanlistListWidget.
        for index in selected_indexes:
            name = self.ui.examCardListView.model().itemFromIndex(index).text()
            scan_parameters = self.ui.examCardListView.model().get_data(index)
            self.scanner.scanlist.add_scanlist_element(name, scan_parameters)
    
    def update_scanlistListWidget(self, scanlist):
        self.ui.scanlistListWidget.clear()
        list = scanlist.scanlist_elements
        for item in list:
            list_item = QListWidgetItem(item.name)
            if item.scan_item.status == ScanItemStatusEnum.READY_TO_SCAN:
                list_item.setIcon(QIcon("resources/icons/checkmark-outline.png"))  
            elif item.scan_item.status == ScanItemStatusEnum.BEING_MODIFIED:
                list_item.setIcon(QIcon("resources/icons/edit-outline.png"))
            elif item.scan_item.status == ScanItemStatusEnum.INVALID:
                list_item.setIcon(QIcon("resources/icons/alert-circle-outline.png"))
            elif item.scan_item.status == ScanItemStatusEnum.COMPLETE:
                list_item.setIcon(QIcon("resources/icons/checkmark-circle-2-outline.png"))
            self.ui.scanlistListWidget.addItem(list_item)  
        active_idx = self.scanner.scanlist.active_idx
        if active_idx is not None:
            current_list_item = self.ui.scanlistListWidget.item(active_idx)
            self.ui.scanlistListWidget.setCurrentItem(current_list_item)
        progress = scanlist.get_progress()
        self.ui.scanProgressBar.setValue(int(progress * 100))    

    def handle_scanlistListWidget_clicked(self, item):
        index = self.ui.scanlistListWidget.row(item)
        self.scanner.scanlist.active_idx = index

    def populate_parameterFormLayout(self, scan_item):
        self.ui.parameterFormLayout.set_parameters(scan_item.scan_parameters)
             
    def handle_viewModelButton_clicked(self):   
        view_model_window = ViewWindow()
        view_model_window.exec_()

    def handle_parameterFormLayout_activated(self):
        self.scanner.active_scan_item.status = ScanItemStatusEnum.BEING_MODIFIED

    def handle_scanParametersCancelChangesButton_clicked(self):
        self.scanner.active_scan_item.cancel_changes()
        self.populate_parameterFormLayout(self.scanner.scanlist.active_scan_item)
        
    def handle_scanParametersSaveChangesButton_clicked(self):
        scan_parameters = self.ui.parameterFormLayout.get_parameters()
        self.scanner.scanlist.active_scan_item.validate_scan_parameters(scan_parameters)

    def handle_scanParametersResetButton_clicked(self):
        self.scanner.scanlist.active_scan_item.reset_parameters()

    def handle_scan_item_status_change(self, status):
        if status == ScanItemStatusEnum.READY_TO_SCAN:
            self.ui.state = UI_state.ReadyToScanState()
        elif status == ScanItemStatusEnum.BEING_MODIFIED:
            self.ui.state = UI_state.BeingModifiedState()
        elif status == ScanItemStatusEnum.INVALID:
            self.ui.state = UI_state.InvalidParametersState()
        elif status == ScanItemStatusEnum.COMPLETE:
            self.ui.state = UI_state.ScanCompleteState()
            self.ui.scannedImageFrame.setAcquiredSeries(self.scanner.active_scanlist_element.acquired_data)

    def handle_scanPlanningWindow1_dropped(self, selected_index):
        # Executed when the user drags and drops a scan item from the scanlistListWidget to the scanPlanningWindow1. If the scan item's acquired series is not None, the acquired series is displayed in the scanPlanningWindow1.
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        acquired_series = scanlist_element.acquired_data
        self.ui.scanPlanningWindow1.setAcquiredSeries(acquired_series)
        self.update_scanlistListWidget(self.scanner.scanlist) # necessary to update scanlist current item so that correct item remains highlighted (i.e., active scan item remains highlighted).

    def handle_scanPlanningWindow2_dropped(self, selected_index):
        # Executed when the user drags and drops a scan item from the scanlistListWidget to the scanPlanningWindow2. If the scan item's acquired series is not None, the acquired series is displayed in the scanPlanningWindow2.
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        acquired_series = scanlist_element.acquired_data
        self.ui.scanPlanningWindow2.setAcquiredSeries(acquired_series)
        self.update_scanlistListWidget(self.scanner.scanlist) # necessary to update scanlist current item so that correct item remains highlighted (i.e., active scan item remains highlighted).

    def handle_scanPlanningWindow3_dropped(self, selected_index):
        # Executed when the user drags and drops a scan item from the scanlistListWidget to the scanPlanningWindow3. If the scan item's acquired series is not None, the acquired series is displayed in the scanPlanningWindow3.
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        acquired_series = scanlist_element.acquired_data
        self.ui.scanPlanningWindow3.setAcquiredSeries(acquired_series)
        self.update_scanlistListWidget(self.scanner.scanlist) # necessary to update scanlist current item so that correct item remains highlighted (i.e., active scan item remains highlighted).

    def handle_newExaminationOkButton_clicked(self, exam_name, model_name):
        settings = SettingsManager.get_instance().settings

        settings.setValue("exam_name", exam_name)
        settings.setValue("model_name", model_name)

        selected_model_data = self.model_data.get(model_name)
        file_path = selected_model_data.get("file_path", None)
        model_data = load_model_data(file_path)
        model = Model(model_name, model_data)
        self.scanner.start_examination(exam_name, model)
        self.scanner.scanlist.add_observer(self)
        self.new_examination_dialog_ui.accept()
        self.ui.state = UI_state.ExamState()
        self.ui.examinationNameLabel.setText(exam_name)
        self.ui.modelNameLabel.setText(model_name)        

    def update(self, event):
        '''
        The update() method defines what happens when events are emitted by parts of the scanner that the MainController is observing. The MainController is observing the scanlist, the active scan item, and the scanner. The update() method is called when the scanner notifies the MainController of changes, e.g., when a scan item is added to the scanlist, when the active scan item is changed, when the status of a scan item is changed, when the parameters of a scan item are changed, etc.'''
        if event == EventEnum.SCANLIST_ITEM_ADDED:
            self.update_scanlistListWidget(self.scanner.scanlist)

        if event == EventEnum.SCANLIST_ACTIVE_INDEX_CHANGED: 
            self.handle_scan_item_status_change(self.scanner.active_scan_item.status)
            #self.ui.editingStackedLayout.setCurrentIndex(0) # Switch to scan parameter editor view
            self.ui.scannedImageFrame.setAcquiredSeries(self.scanner.active_scanlist_element.acquired_data) # Display acquired series in scannedImageFrame. If it is None, the scannedImageFrame will display a blank image.
            current_list_item = self.ui.scanlistListWidget.item(self.scanner.scanlist.active_idx)
            self.ui.scanlistListWidget.setCurrentItem(current_list_item)
            self.populate_parameterFormLayout(self.scanner.active_scan_item)
            self.scanner.active_scan_item.add_observer(self)
            self.ui.scanPlanningWindow1.setScanVolume(self.scanner.active_scan_item.scan_volume) 
            self.ui.scanPlanningWindow2.setScanVolume(self.scanner.active_scan_item.scan_volume)
            self.ui.scanPlanningWindow3.setScanVolume(self.scanner.active_scan_item.scan_volume)

        if event == EventEnum.SCAN_ITEM_STATUS_CHANGED:
            self.handle_scan_item_status_change(self.scanner.active_scan_item.status)
            self.update_scanlistListWidget(self.scanner.scanlist)

        if event == EventEnum.SCAN_ITEM_PARAMETERS_CHANGED:
            self.populate_parameterFormLayout(self.scanner.active_scan_item)
            