import json
import os
from datetime import datetime

import numpy as np
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QListWidgetItem

import views.UI_MainWindowState as UI_state
from controllers.settings_mgr import SettingsManager
from events import EventEnum
from simulator.load import load_json, load_model_data
from simulator.model import Model
from simulator.scanlist import (
    ScanItem,
    ScanItemStatusEnum,
    AcquiredImage,
    AcquiredSeries,
)
from simulator.scanner import Scanner
from utils.logger import log
from views.main_view_ui import Ui_MainWindow
from views.qmodels import DictionaryModel
from views.ui.color_scale import ColorScale
from views.ui.export_image_dialog_ui import ExportImageDialog
from views.ui.export_scanitem_dialog_ui import ExportScanItemDialog
from views.ui.load_examination_dialog_ui import LoadExaminationDialog
from views.ui.new_examination_dialog_ui import NewExaminationDialog
from views.ui.view_model_dialog_ui import ViewModelDialog


class MainController:
    """
    The MainController class defines what happens when the user interacts with the UI. It also defines in its update() method what happens when the scanner notifies the controller of changes, e.g., when a scan item is added to the scanlist, when the active scan item is changed, when the status of a scan item is changed, when the parameters of a scan item are changed, etc.
    """

    def __init__(self, scanner: Scanner, ui: Ui_MainWindow) -> None:
        self.new_examination_dialog_ui = None
        self.load_examination_dialog_ui = None
        self.scanner: Scanner = scanner
        self.ui: Ui_MainWindow = ui
        self.ui_signals()
        self.scan_indices_queue = []
        self.current_scan_index = 0
        self.color_scale = ColorScale.get_color_scale()

    def handle_startScanButton_clicked(self):
        if self.scanner.scan_started:
            # Scanning is already in progress, fast forward
            self.scanner.scan()
            return
        selected_items = self.ui.scanlistListWidget.selectedItems()
        if not selected_items:
            # No items selected
            log.info("No scan items selected")
            return
        else:
            # Get indices of selected items
            self.scan_indices_queue = [
                self.ui.scanlistListWidget.row(item) for item in selected_items
            ]
            self.current_scan_index = 0
            # Start scanning
            self.scan_next_item()

    def scan_next_item(self):
        if self.current_scan_index < len(self.scan_indices_queue):
            index = self.scan_indices_queue[self.current_scan_index]
            # Set the active scan item to this index
            self.scanner.scanlist.active_idx = index
            # Start the scan
            self.scanner.scan()
            # Increment the current_scan_index for next scan item
            self.current_scan_index += 1
        else:
            # All scans completed, clear the scan indices queue
            self.scan_indices_queue = []
            self.current_scan_index = 0
            log.info("All scans completed.")

    def handle_scan_completed(self):
        # Start the next scan
        self.scan_next_item()

        # Reselect the scan item that just completed scanning
        if self.current_scan_index > 0:
            # Get the index of the scan item that just completed
            index = self.scan_indices_queue[self.current_scan_index - 1]
            # Set the active index in the scanlist to reselect the scan item
            self.scanner.scanlist.active_idx = index

            # Update the UI to reflect the reselected scan item
            current_list_item = self.ui.scanlistListWidget.item(index)
            self.ui.scanlistListWidget.setCurrentItem(current_list_item)

        # Since the scan item is now complete hide volumes
        self.ui.scanPlanningWindow1.setScanVolumes([])
        self.ui.scanPlanningWindow2.setScanVolumes([])
        self.ui.scanPlanningWindow3.setScanVolumes([])

        # Update the scan list widget to reflect any changes
        self.update_scanlistListWidget(self.scanner.scanlist)

    def ui_signals(self):
        self.load_examination_dialog_ui = LoadExaminationDialog()
        self.new_examination_dialog_ui = NewExaminationDialog()

        self.ui.startScanButton.clicked.connect(self.handle_startScanButton_clicked)
        self.scanner.scan_completed.connect(self.handle_scan_completed)

        self.ui.importScanItemButton.clicked.connect(
            self.handle_importScanItemButton_clicked
        )

        # Connect signals to slots, i.e., define what happens when the user interacts with the UI by connecting
        # signals from UI to functions that handle the signals.

        # Signals related to examinations
        self.ui.loadExaminationButton.clicked.connect(
            lambda: self.load_examination_dialog_ui.open_file_dialog()
        )
        self.ui.newExaminationButton.clicked.connect(
            self.handle_newExaminationButton_clicked
        )
        self.ui.stopExaminationButton.clicked.connect(
            self.handle_stopExaminationButton_clicked
        )

        # Signals related to scanlist
        self.ui.addScanItemButton.clicked.connect(self.handle_addScanItemButton_clicked)
        self.ui.scanlistListWidget.dropEventSignal.connect(self.handle_add_to_scanlist)
        self.ui.scanlistListWidget.fileDroppedEventSignal.connect(
            self.handle_add_to_scanlist_from_saved
        )
        self.ui.scanlistListWidget.itemClicked.connect(
            self.handle_scanlistListWidget_clicked
        )

        # Signals related to anatomical model
        self.ui.viewModelButton.clicked.connect(self.handle_viewModelButton_clicked)

        # Signals related to scan parameters
        self.ui.parameterFormLayout.formActivatedSignal.connect(
            self.handle_parameterFormLayout_activated
        )
        self.ui.stackParameterFormLayout.stackSignal.connect(self.handleStackAction)
        self.ui.scanParametersCancelChangesButton.clicked.connect(
            self.handle_scanParametersCancelChangesButton_clicked
        )
        self.ui.scanParametersSaveChangesButton.clicked.connect(
            self.handle_scanParametersSaveChangesButton_clicked
        )

        self.ui.scanParametersExportButton.clicked.connect(
            self.handle_scanParametersExportButton_clicked
        )

        self.ui.scanParametersResetButton.clicked.connect(
            self.handle_scanParametersResetButton_clicked
        )

        # Signals related to scan planning windows
        self.ui.scanPlanningWindow1.dropEventSignal.connect(
            self.handle_scanPlanningWindow1_dropped
        )

        # change stack event from scan planning window
        self.ui.scanPlanningWindow1.stackSignal.connect(
            self.handleStackActionFromWindow
        )
        self.ui.scanPlanningWindow2.stackSignal.connect(
            self.handleStackActionFromWindow
        )
        self.ui.scanPlanningWindow3.stackSignal.connect(
            self.handleStackActionFromWindow
        )

        self.ui.scanPlanningWindow2.dropEventSignal.connect(
            self.handle_scanPlanningWindow2_dropped
        )
        self.ui.scanPlanningWindow3.dropEventSignal.connect(
            self.handle_scanPlanningWindow3_dropped
        )
        # Signals for grid in viewing mode
        self.ui.gridViewingWindow.connect_drop_signals(self.handle_dropped_cells)
        self.ui.gridViewingWindow.gridUpdated.connect(self.handle_update_grid)

        # Signals from new examination dialog
        self.new_examination_dialog_ui.newExaminationCancelButton.clicked.connect(
            lambda: self.new_examination_dialog_ui.accept()
        )
        self.new_examination_dialog_ui.newExaminationOkButton.clicked.connect(
            lambda: self.handle_newExaminationOkButton_clicked(
                self.new_examination_dialog_ui.examNameLineEdit.text(),
                self.new_examination_dialog_ui.modelComboBox.currentText(),
            )
        )

        # Signals and UIs related to exporting images
        self.export_image_dialog_ui = ExportImageDialog()

        self.export_scanitem_dialog = ExportScanItemDialog()

        self.ui.scannedImageWidget.acquiredImageExportButton.clicked.connect(
            lambda: self.handle_viewingPortExport_triggered(0)
        )
        self.ui.scannedImageFrame.export_action.triggered.connect(
            lambda: self.handle_viewingPortExport_triggered(0)
        )
        self.ui.scanPlanningWindow1ExportButton.clicked.connect(
            lambda: self.handle_viewingPortExport_triggered(1)
        )
        self.ui.scanPlanningWindow1.export_action.triggered.connect(
            lambda: self.handle_viewingPortExport_triggered(1)
        )
        self.ui.scanPlanningWindow2ExportButton.clicked.connect(
            lambda: self.handle_viewingPortExport_triggered(2)
        )
        self.ui.scanPlanningWindow2.export_action.triggered.connect(
            lambda: self.handle_viewingPortExport_triggered(2)
        )
        self.ui.scanPlanningWindow3ExportButton.clicked.connect(
            lambda: self.handle_viewingPortExport_triggered(3)
        )
        self.ui.scanPlanningWindow3.export_action.triggered.connect(
            lambda: self.handle_viewingPortExport_triggered(3)
        )

        self.ui.scannedImageFrame.export_image_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportImageToDicomdir_triggered(0)
        )
        self.ui.scanPlanningWindow1.export_image_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportImageToDicomdir_triggered(1)
        )
        self.ui.scanPlanningWindow2.export_image_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportImageToDicomdir_triggered(2)
        )
        self.ui.scanPlanningWindow3.export_image_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportImageToDicomdir_triggered(3)
        )

        self.ui.scannedImageFrame.export_series_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportSeriesToDicomdir_triggered(0)
        )
        self.ui.scanPlanningWindow1.export_series_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportSeriesToDicomdir_triggered(1)
        )
        self.ui.scanPlanningWindow2.export_series_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportSeriesToDicomdir_triggered(2)
        )
        self.ui.scanPlanningWindow3.export_series_with_dicomdir_action.triggered.connect(
            lambda: self.handle_exportSeriesToDicomdir_triggered(3)
        )

        self.ui.scannedImageFrame.export_examination_with_dicomdir_action.triggered.connect(
            lambda: self.export_image_dialog_ui.export_examination_to_dicom_with_dicomdir(
                self.ui.scanner.examination
            )
        )
        self.ui.scanPlanningWindow1.export_examination_with_dicomdir_action.triggered.connect(
            lambda: self.export_image_dialog_ui.export_examination_to_dicom_with_dicomdir(
                self.ui.scanner.examination
            )
        )
        self.ui.scanPlanningWindow2.export_examination_with_dicomdir_action.triggered.connect(
            lambda: self.export_image_dialog_ui.export_examination_to_dicom_with_dicomdir(
                self.ui.scanner.examination
            )
        )
        self.ui.scanPlanningWindow3.export_examination_with_dicomdir_action.triggered.connect(
            lambda: self.export_image_dialog_ui.export_examination_to_dicom_with_dicomdir(
                self.ui.scanner.examination
            )
        )

    def prepare_model_data(self):
        jsonFilePath = "repository/models/models.json"
        self.model_data = load_json(jsonFilePath)
        model_names = list(self.model_data.keys())
        self.populate_modelComboBox(model_names)

    def export_examination(self):
        default_filename = f"session-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.ini"

        file_path, _ = QFileDialog.getSaveFileName(
            self.ui, "Save Session", default_filename
        )

        # If canceled, return without doing anything
        if not file_path:
            log.info("File save canceled.")
            return

        # Ensure the file path has a valid .ini extension
        if not file_path.endswith(".ini"):
            file_path += ".ini"

        settings_manager = SettingsManager.get_instance()
        settings_manager.export_settings(file_path)
        log.info(f"Session saved to {file_path}")

    def handle_newExaminationButton_clicked(self):
        jsonFilePath = "repository/models/models.json"
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
        jsonFilePath = "repository/exam_cards/scan_items.json"
        self.exam_card_data = load_json(jsonFilePath)
        self.ui.editingStackedLayout.setCurrentIndex(1)
        self.populate_examCardListView(self.exam_card_data)

    def populate_examCardListView(self, exam_card_data):
        self.exam_card_qmodel = DictionaryModel(exam_card_data)
        self.ui.examCardListView.setModel(self.exam_card_qmodel)

    def handle_add_to_scanlist_from_saved(self, file_path):
        log.warning("File path: " + file_path)
        if file_path.endswith(".json"):
            log.info("File path: " + file_path)
            file_path = file_path
            # check if file is json and is valid path
            if not os.path.exists(file_path):
                log.error("Invalid file path")
                return
            scan_parameters = load_json(file_path)
            file_name = file_path.split("/")[-1].split(".")[0]
            self.scanner.scanlist.add_scanlist_element(file_name, scan_parameters[0])
        else:
            log.error("Invalid file format")
            return

    def handle_add_to_scanlist(self, selected_indexes):
        # Executed when the user drags and drops items from the examCardListView to the scanlistListWidget.
        for index in selected_indexes:
            name = self.ui.examCardListView.model().itemFromIndex(index).text()
            scan_parameters = self.ui.examCardListView.model().get_data(index)
            self.scanner.scanlist.add_scanlist_element(name, scan_parameters)

    def handleStackActionFromWindow(self, stack_index):
        self.scanner.active_scan_item.selected_stack_index = stack_index
        # TODO: call change stack function under acquired series viewer that would set active states of polygons and update them

    # implement event handler to catch stack change event from stack parameters tab, then change stack under acquiredseries viewer and update scan parameters
    def handleStackAction(self, act):
        if act["event"] == EventEnum.STACK_CHANGED:
            new_stack_index = act["stack_index"]
            self.scanner.active_scan_item.change_active_stack(new_stack_index)
            changed_stack_index = self.scanner.active_scan_item.selected_stack_index
            self.ui.scanPlanningWindow1.change_stack(changed_stack_index)
            self.ui.scanPlanningWindow2.change_stack(changed_stack_index)
            self.ui.scanPlanningWindow3.change_stack(changed_stack_index)
            self.populate_parameterFormLayout(self.scanner.active_scan_item)
        elif act["event"] == EventEnum.ADD_STACK:
            self.scanner.active_scan_item.add_stack()
            self.ui.scanPlanningWindow1.setScanVolumes(
                self.scanner.active_scan_item.scan_volumes
            )
            self.ui.scanPlanningWindow2.setScanVolumes(
                self.scanner.active_scan_item.scan_volumes
            )
            self.ui.scanPlanningWindow3.setScanVolumes(
                self.scanner.active_scan_item.scan_volumes
            )
        elif act["event"] == EventEnum.DELETE_STACK:
            # extra guard to only allow deleting stack if there are more than 1 stacks in the current scan item
            if self.scanner.active_scan_item.get_number_of_stacks() == 1:
                return
            delete_stack_index = self.scanner.active_scan_item.selected_stack_index
            # delete stack in scan item
            self.scanner.active_scan_item.delete_stack(delete_stack_index)
            # delete stacks under scan planning windows
            self.ui.scanPlanningWindow1.delete_stack(delete_stack_index)
            self.ui.scanPlanningWindow2.delete_stack(delete_stack_index)
            self.ui.scanPlanningWindow3.delete_stack(delete_stack_index)
            # update stack parameters ui
            index_position = (
                self.scanner.active_scan_item.get_order_position_of_active_stack()
            )
            self.ui.stackParameterFormLayout.delete_stack_event(
                index_position, len(self.scanner.active_scan_item.scan_parameters)
            )
            # change active stacks in scan planning windows to other stack
            self.ui.scanPlanningWindow1.change_stack(
                self.scanner.active_scan_item.selected_stack_index
            )
            self.ui.scanPlanningWindow2.change_stack(
                self.scanner.active_scan_item.selected_stack_index
            )
            self.ui.scanPlanningWindow3.change_stack(
                self.scanner.active_scan_item.selected_stack_index
            )

    def update_scanlistListWidget(self, scanlist):
        self.ui.scanlistListWidget.clear()
        list = scanlist.scanlist_elements
        for idx, item in enumerate(list):
            list_item = QListWidgetItem(item.name)
            if item.scan_item.status == ScanItemStatusEnum.READY_TO_SCAN:
                list_item.setIcon(QIcon("resources/icons/checkmark-outline.png"))
            elif item.scan_item.status == ScanItemStatusEnum.BEING_MODIFIED:
                list_item.setIcon(QIcon("resources/icons/edit-outline.png"))
            elif item.scan_item.status == ScanItemStatusEnum.BEING_SCANNED:
                list_item.setIcon(QIcon("resources/icons/edit-outline.png"))
            elif item.scan_item.status == ScanItemStatusEnum.INVALID:
                list_item.setIcon(QIcon("resources/icons/alert-circle-outline.png"))
            elif item.scan_item.status == ScanItemStatusEnum.COMPLETE:
                list_item.setIcon(
                    QIcon("resources/icons/checkmark-circle-2-outline.png")
                )
            if idx in self.scan_indices_queue[self.current_scan_index :]:
                # Highlight ongoing queue scanitems
                list_item.setBackground(QtGui.QColor("#BFBFBF"))
            self.ui.scanlistListWidget.addItem(list_item)
        active_idx = self.scanner.scanlist.active_idx
        if active_idx is not None:
            current_list_item = self.ui.scanlistListWidget.item(active_idx)
            self.ui.scanlistListWidget.setCurrentItem(current_list_item)

    def handle_scanlistListWidget_clicked(self, item):
        index = self.ui.scanlistListWidget.row(item)
        self.scanner.scanlist.active_idx = index

    def populate_parameterFormLayout(self, scan_item: ScanItem):
        # self.ui.parameterFormLayout.set_parameters(scan_item.scan_parameters)
        active_params = scan_item.get_current_active_parameters()
        self.ui.parameterFormLayout.set_parameters(active_params)

    def populate_stackFormLayout(self):
        stacks_params = {
            "nr_of_stacks": len(self.scanner.active_scan_item.scan_parameters),
            "selected_stack_index": 0,
        }
        self.ui.stackParameterFormLayout.set_stacks_params(stacks_params)

    def handle_viewModelButton_clicked(self):
        rightlayout = self.ui.layout
        self.ui.layout.clearLayout(rightlayout)
        scanlist = self.save_complete_scanlist_items(self.scanner.scanlist)
        if not scanlist:
            return
        else:
            self.ui._createViewWindow()
            self.restore_complete_scanlist_items()
            self.ui.state = UI_state.ViewState()
            self.ui.update_UI()
            # handle drops
            self.ui.gridViewingWindow.connect_drop_signals(self.handle_dropped_cells)

    def handle_importScanItemButton_clicked(self):
        path = self.export_scanitem_dialog.open_file_dialog(save=False)

        if path is None or path == "":
            log.info("No file selected")
            return

        # get filename from path
        filename = path.split("/")[-1].split(".")[0]

        with open(path, "r") as f:
            scan_parameters = json.load(f)

        self.scanner.scanlist.add_scanlist_element(filename, scan_parameters[0])

        log.info(f"ScanItem {filename} imported")

    def handle_scanningButton_clicked(self):
        rightlayout = self.ui.layout
        scanlist = self.save_complete_scanlist_items(self.scanner.scanlist)
        self.ui.layout.clearLayout(rightlayout)
        self.ui._createMainWindow()
        self.ui.state = UI_state.ReadyToScanAgainState()
        self.restore_complete_scanlist_items()
        self.ui_signals()

    def handle_viewModelButton_clicked(self):
        # view model for the view model dialogue
        view_model_dialog = ViewModelDialog(self.scanner.model)
        view_model_dialog.exec()

    def handle_dropped_cells(self, row: int, col: int, selected_index: int):
        grid_cell = self.ui.gridViewingWindow.get_grid_cell(row, col)
        if grid_cell is not None:
            scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
            acquired_series = scanlist_element.acquired_data
            grid_cell.setAcquiredSeries(acquired_series)
            self.update_scanlistListWidget(self.scanner.scanlist)
        else:
            log.error("This cell doesn't exist")

    def connect_drop_signals(self):
        # Connect the drop event signals from the grid cells to the handle_dropped_cells method
        self.ui.gridViewingWindow.connect_drop_signals(self.handle_dropped_cells)

    def handle_update_grid(self):
        # Used to reconnect all cells to accept drops after rows/columns have been removed
        self.ui.gridViewingWindow.reconnect_all_signals(self.handle_dropped_cells)

    def handle_hide_checkboxes(self, checked):
        if checked:
            self.ui.gridViewingWindow.hide_checkboxes()

    def handle_start_contrastLinking(self):
        self.ui.gridViewingWindow.show_checkboxes()
        self.ui.gridViewingWindow.start_contrast_linking()

        for row in self.ui.gridViewingWindow.grid_cells:
            for cell in row:
                cell.checkbox.stateChanged.connect(
                    lambda state, cell=cell: self.handle_check_uncheck(state, cell)
                )

    def handle_check_uncheck(self, state, cell):
        # used to connect/disconnect a cell depending on if it is checked or not;
        # stateChanged ouputs 2 for checked and 0 for unchecked
        if state == 2:
            self.ui.gridViewingWindow.connect_cell(cell)
        elif state == 0:  #
            self.ui.gridViewingWindow.disconnect_cell(cell)

    def handle_stop_contrastLinking(self):
        self.ui.gridViewingWindow.stop_contrast_linking()
        self.handle_hide_checkboxes(True)

    def handle_parameterFormLayout_activated(self):
        self.scanner.active_scan_item.status = ScanItemStatusEnum.BEING_MODIFIED

    def handle_scanParametersCancelChangesButton_clicked(self):
        self.scanner.active_scan_item.cancel_changes()
        self.populate_parameterFormLayout(self.scanner.scanlist.active_scan_item)

    def handle_scanParametersExportButton_clicked(self):
        params = self.scanner.active_scanlist_element.scan_item.scan_parameters
        path = self.export_scanitem_dialog.open_file_dialog()

        if path is None or path == "":
            log.info("No file selected")
            return

        with open(path, "w") as f:
            json.dump(params, f)

        log.info(
            f"Item {self.scanner.active_scanlist_element.scan_item.name} parameters exported"
        )

        self.ui._savedItemsTab.populate_list(None)

    def handle_scanParametersSaveChangesButton_clicked(self):
        scan_parameters = self.ui.parameterFormLayout.get_parameters()
        self.scanner.scanlist.active_scan_item.validate_scan_parameters_single(
            scan_parameters
        )
        self.scanner.scanlist.active_scan_item.perform_rotation_check_single(
            scan_parameters
        )
        # self.scanner.scanlist.active_scan_item.validate_scan_parameters(scan_parameters)
        # self.scanner.scanlist.active_scan_item.perform_rotation_check(scan_parameters)

    def handle_scanParametersResetButton_clicked(self):
        self.scanner.scanlist.active_scan_item.reset_parameters()

    def handle_scan_item_status_change(self, status):
        if status == ScanItemStatusEnum.READY_TO_SCAN:
            self.ui.state = UI_state.ReadyToScanState()
        elif status == ScanItemStatusEnum.BEING_MODIFIED:
            self.ui.state = UI_state.BeingModifiedState()
        elif status == ScanItemStatusEnum.BEING_SCANNED:
            self.ui.state = UI_state.BeingScannedState()
        elif status == ScanItemStatusEnum.INVALID:
            self.ui.state = UI_state.InvalidParametersState()
        elif status == ScanItemStatusEnum.COMPLETE:
            self.ui.state = UI_state.ScanCompleteState()
            self.ui.scannedImageFrame.setScanCompleteAcquiredData(
                self.scanner.active_scanlist_element.acquired_data
            )

    def handle_scanPlanningWindow1_dropped(self, selected_index):
        # Executed when the user drags and drops a scan item from the scanlistListWidget to the scanPlanningWindow1. If the scan item's acquired series is not None, the acquired series is displayed in the scanPlanningWindow1.
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        acquired_series = scanlist_element.acquired_data
        self.ui.scanPlanningWindow1.setAcquiredSeries(acquired_series)
        self.update_scanlistListWidget(
            self.scanner.scanlist
        )  # necessary to update scanlist current item so that correct item remains highlighted (i.e., active scan item remains highlighted).

    def handle_scanPlanningWindow2_dropped(self, selected_index):
        # Executed when the user drags and drops a scan item from the scanlistListWidget to the scanPlanningWindow2. If the scan item's acquired series is not None, the acquired series is displayed in the scanPlanningWindow2.
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        acquired_series = scanlist_element.acquired_data
        self.ui.scanPlanningWindow2.setAcquiredSeries(acquired_series)
        self.update_scanlistListWidget(
            self.scanner.scanlist
        )  # necessary to update scanlist current item so that correct item remains highlighted (i.e., active scan item remains highlighted).

    def handle_scanPlanningWindow3_dropped(self, selected_index):
        # Executed when the user drags and drops a scan item from the scanlistListWidget to the scanPlanningWindow3. If the scan item's acquired series is not None, the acquired series is displayed in the scanPlanningWindow3.
        scanlist_element = self.scanner.scanlist.scanlist_elements[selected_index]
        acquired_series = scanlist_element.acquired_data
        self.ui.scanPlanningWindow3.setAcquiredSeries(acquired_series)
        self.update_scanlistListWidget(
            self.scanner.scanlist
        )  # necessary to update scanlist current item so that correct item remains highlighted (i.e., active scan item remains highlighted).

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

    def handle_changeColorMapping(self, mapping):
        """
        Changes color mapping to("bw" or "rgb").
        """
        ColorScale.set_color_scale(mapping)  # Update the global color scale

        # Update the grid cells
        for row in range(len(self.ui.gridViewingWindow.grid_cells)):
            for col in range(len(self.ui.gridViewingWindow.grid_cells[row])):
                grid_cell = self.ui.gridViewingWindow.get_grid_cell(row, col)
                if grid_cell is not None:
                    grid_cell.setColorScale(ColorScale.get_color_scale())
                    log.debug(f"Color mapping changed to {mapping} for GridCell ({row}, {col})")

        # Apply the color scale to all AcquiredSeriesViewer2D instances
        viewers = [
            self.ui.scanPlanningWindow1,
            self.ui.scanPlanningWindow2,
            self.ui.scanPlanningWindow3,
        ]

        for viewer in viewers:
            if viewer is not None:
                viewer.setColorScale(ColorScale.get_color_scale())
                log.debug(f"Color mapping changed to {mapping} for {viewer}.")

        log.debug(f"Color mapping changed to {mapping} globally.")

    def handle_viewingPortExport_triggered(self, index: int):
        if index not in range(0, 4):
            raise ValueError(
                f"Index {index} does not refer to a valid image viewing port"
            )

        if index == 0:
            image = self.ui.scannedImageFrame.displayed_image
            series = self.ui.scannedImageFrame.acquired_series
        elif index == 1:
            image = self.ui.scanPlanningWindow1.displayed_image
            series = self.ui.scanPlanningWindow1.acquired_series
        elif index == 2:
            image = self.ui.scanPlanningWindow2.displayed_image
            series = self.ui.scanPlanningWindow2.acquired_series
        else:
            image = self.ui.scanPlanningWindow3.displayed_image
            series = self.ui.scanPlanningWindow3.acquired_series
        parameters = self._return_parameters_from_image_in_scanlist(image)
        study = self.ui.scanner.examination
        self.export_image_dialog_ui.export_file_dialog(image, series, study, parameters)

    def handle_exportImageToDicomdir_triggered(self, index: int):
        if index not in range(0, 4):
            raise ValueError(
                f"Index {index} does not refer to a valid image viewing port"
            )

        if index == 0:
            image = self.ui.scannedImageFrame.displayed_image
            series = self.ui.scannedImageFrame.acquired_series
        elif index == 1:
            image = self.ui.scanPlanningWindow1.displayed_image
            series = self.ui.scanPlanningWindow1.acquired_series
        elif index == 2:
            image = self.ui.scanPlanningWindow2.displayed_image
            series = self.ui.scanPlanningWindow2.acquired_series
        else:
            image = self.ui.scanPlanningWindow3.displayed_image
            series = self.ui.scanPlanningWindow3.acquired_series
        parameters = self._return_parameters_from_image_in_scanlist(image)
        study = self.ui.scanner.examination
        self.export_image_dialog_ui.export_image_to_dicom_with_dicomdir(
            image, series, study, parameters
        )

    def handle_exportSeriesToDicomdir_triggered(self, index: int):
        if index not in range(0, 4):
            raise ValueError(
                f"Index {index} does not refer to a valid image viewing port"
            )

        if index == 0:
            series = self.ui.scannedImageFrame.acquired_series
        elif index == 1:
            series = self.ui.scanPlanningWindow1.acquired_series
        elif index == 2:
            series = self.ui.scanPlanningWindow2.acquired_series
        else:
            series = self.ui.scanPlanningWindow3.acquired_series
        parameters_list = []
        for image in series.list_acquired_images:
            parameters = self._return_parameters_from_image_in_scanlist(image)
            parameters_list.append(parameters)
        study = self.ui.scanner.examination
        self.export_image_dialog_ui.export_series_to_dicom_with_dicomdir(
            series, study, parameters_list
        )

    def handle_measureDistanceButtonClicked(self):
        if not self.ui._scannedImageFrame.measuring_enabled:
            self.ui._scannedImageFrame.measuring_enabled = True
            log.warn("Measuring enabled")
        else:
            self.ui._scannedImageFrame.measuring_enabled = False
            self.ui._scannedImageFrame.measure.hide_items()
            log.warn("Measuring disabled")

    def handle_toggleWindowLevelButtonClicked(self):
        """Toggle the window-level mode"""
        return  # not used

    def _return_parameters_from_image_in_scanlist(self, image: AcquiredImage) -> dict:
        """Find an image in the current scan list, and return the parameters of the scan list item associated with the image.

        Args:
            image (AcquiredImage): the image that is to be found in the scan list.

        Returns:
            The parameters from the scan list element that is associated with the image argument of this method.

        Raises:
             ValueError: If the image argument of this method was not found in the scan list.
        """

        parameters: dict | None = None  # Return variable
        found = False  # Flag to check if the image was found

        # Loop over all scan list elements
        for scanlist_element in self.scanner.scanlist.scanlist_elements:
            # For each scan list element, loop over all (acquired) images
            acquired_series: AcquiredSeries = scanlist_element.acquired_data
            acquired_image: AcquiredImage
            if acquired_series is None:
                continue
            for acquired_image in acquired_series.list_acquired_images:
                # If the image data does not match, continue to the next image
                if not np.array_equal(acquired_image.image_data, image.image_data):
                    continue

                geometry_parameters_correct = (
                    True  # Flag to check if the geometry parameters match
                )

                # Loop over the key-value pairs in the geometry parameters dictionary of this acquired image
                for (
                    key,
                    value,
                ) in acquired_image.image_geometry.geometry_parameters.items():
                    # This isinstance check is for (in)equality in case the current value is of type np.ndarray
                    if isinstance(value, np.ndarray):
                        if not np.array_equal(
                            value, image.image_geometry.geometry_parameters[key]
                        ):
                            geometry_parameters_correct = False
                    # If we don't have an np.ndarray as our value, just check for (in)equality
                    elif value != image.image_geometry.geometry_parameters[key]:
                        geometry_parameters_correct = False

                    # If any of the geometry parameters don't match, stop checking this dictionary
                    if not geometry_parameters_correct:
                        break
                # If any of the geometry parameters don't match, continue to the next image
                if not geometry_parameters_correct:
                    continue

                # If both the image data and all the geometry parameters match, we have found (acquired) image that we were looking for
                found = True
                parameters = scanlist_element.scan_item.scan_parameters[0]
                break

            # If we found the image that we were looking for, break out of the scan list element loop
            if found:
                break

        # If the parameters variable is still None after checking all possible options, raise an error
        if parameters is None:
            raise ValueError("Image not found in scan list")

        # Return the parameters dictionary
        return parameters

    def update(self, event):
        """
        The update() method defines what happens when events are emitted by parts of the scanner that the MainController is observing. The MainController is observing the scanlist, the active scan item, and the scanner. The update() method is called when the scanner notifies the MainController of changes, e.g., when a scan item is added to the scanlist, when the active scan item is changed, when the status of a scan item is changed, when the parameters of a scan item are changed, etc.
        """
        if event == EventEnum.SCANLIST_ITEM_ADDED:
            self.update_scanlistListWidget(self.scanner.scanlist)

        if event == EventEnum.SCANLIST_ACTIVE_INDEX_CHANGED:
            self.handle_scan_item_status_change(self.scanner.active_scan_item.status)
            self.ui.editingStackedLayout.setCurrentIndex(
                0
            )  # Switch to scan parameter editor view
            self.ui.scannedImageFrame.setScanCompleteAcquiredData(
                self.scanner.active_scanlist_element.acquired_data
            )  # Display acquired series in scannedImageFrame. If it is None, the scannedImageFrame will display a blank image.
            current_list_item = self.ui.scanlistListWidget.item(
                self.scanner.scanlist.active_idx
            )
            self.ui.scanlistListWidget.setCurrentItem(current_list_item)
            self.populate_parameterFormLayout(self.scanner.active_scan_item)
            self.populate_stackFormLayout()
            self.scanner.active_scan_item.add_observer(self)
            self.ui.scanPlanningWindow1.selected_stack_indx = 0
            self.ui.scanPlanningWindow2.selected_stack_indx = 0
            self.ui.scanPlanningWindow3.selected_stack_indx = 0

            # Set scan volume on planning windows only if the active scan item is not completed
            # TODO: change over to active_scan_item.scan_volumes
            if self.scanner.active_scan_item.status != ScanItemStatusEnum.COMPLETE:
                # self.ui.scanPlanningWindow1.setScanVolume(
                #     self.scanner.active_scan_item.scan_volume
                # )
                # self.ui.scanPlanningWindow2.setScanVolume(
                #     self.scanner.active_scan_item.scan_volume
                # )
                # self.ui.scanPlanningWindow3.setScanVolume(
                #     self.scanner.active_scan_item.scan_volume
                # )
                self.ui.scanPlanningWindow1.setScanVolumes(
                    self.scanner.active_scan_item.scan_volumes
                )
                self.ui.scanPlanningWindow2.setScanVolumes(
                    self.scanner.active_scan_item.scan_volumes
                )
                self.ui.scanPlanningWindow3.setScanVolumes(
                    self.scanner.active_scan_item.scan_volumes
                )
            else:
                # Clear the scan volume if the scan is completed
                # self.ui.scanPlanningWindow1.setScanVolume(None)
                # self.ui.scanPlanningWindow2.setScanVolume(None)
                # self.ui.scanPlanningWindow3.setScanVolume(None)
                self.ui.scanPlanningWindow1.setScanVolumes([])
                self.ui.scanPlanningWindow2.setScanVolumes([])
                self.ui.scanPlanningWindow3.setScanVolumes([])

        if event == EventEnum.SCAN_ITEM_STATUS_CHANGED:
            self.handle_scan_item_status_change(self.scanner.active_scan_item.status)
            self.update_scanlistListWidget(self.scanner.scanlist)

        if event == EventEnum.SCAN_ITEM_PARAMETERS_CHANGED:
            # self._scan_vo
            # self.scanner.active_scan_item.scan_volume.clamp_to_scanner_dimensions()
            self.scanner.active_scan_item.find_scan_volume_with_stack_index(
                self.scanner.active_scan_item.selected_stack_index
            ).clamp_to_scanner_dimensions()
            self.populate_parameterFormLayout(self.scanner.active_scan_item)
