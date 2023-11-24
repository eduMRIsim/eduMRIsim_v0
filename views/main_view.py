from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot
from views.main_view_ui import Ui_MainWindow
from views.new_examination_dialog_ui import NewExaminationDialog
from views.load_examination_dialog_ui import LoadExaminationDialog
from views.view_model_dialog_ui import ViewModelDialog
from views.qmodels import DictionaryModel
from scanner import Scanner

class MainView(QMainWindow):
    def __init__(self, scanner, main_controller):
        super().__init__()

        self._main_controller = main_controller
        self._scanner = scanner
        self._ui = Ui_MainWindow(self._scanner, self)
        self._load_examination_dialog_ui = LoadExaminationDialog()
        self._new_examination_dialog_ui = NewExaminationDialog()

        self._ui.loadExaminationButton.clicked.connect(lambda: self._load_examination_dialog_ui.exec())
        self._ui.newExaminationButton.clicked.connect(self._main_controller.handle_newExaminationButton_clicked)
        self._ui.addScanItemButton.clicked.connect(self._main_controller.handle_addScanItemButton_clicked)
        self._ui.examCardListView.doubleClicked.connect(self.on_examCardListView_dclicked)

        self._new_examination_dialog_ui.newExaminationCancelButton.clicked.connect(lambda: self._new_examination_dialog_ui.accept())
        self._new_examination_dialog_ui.newExaminationOkButton.clicked.connect(lambda: self._main_controller.handle_newExaminationOkButton_clicked(self._new_examination_dialog_ui.examNameLineEdit.text(), self._new_examination_dialog_ui.modelComboBox.currentText()))

        self._main_controller.populate_modelComboBox.connect(self.on_populate_modelComboBox)
        self._main_controller.open_newExaminationDialog.connect(lambda: self._new_examination_dialog_ui.exec())
        self._main_controller.close_newExaminationDialog.connect(lambda: self._new_examination_dialog_ui.accept())
        self._main_controller.start_new_examination.connect(self.on_start_new_examination)
        self._main_controller.show_examCardTabWidget.connect(lambda: self._ui.editingStackedLayout.setCurrentIndex(1))
        self._main_controller.populate_examCardListView.connect(self.on_populate_examCardListView)
        self._main_controller.update_scanlistListWidget.connect(self.on_update_scanlistListWidget) 

    @pyqtSlot(list)
    def on_populate_modelComboBox(self, list):
        self._new_examination_dialog_ui.modelComboBox.clear()
        self._new_examination_dialog_ui.modelComboBox.addItems(list)

    @pyqtSlot(str, str)
    def on_start_new_examination(self, exam_name, model_name):
        self._new_examination_dialog_ui.accept()
        self._ui.examinationNameLabel.setText(exam_name)
        self._ui.modelNameLabel.setText(model_name)
        self._ui.examinationInfoStackedLayout.setCurrentIndex(1)
        self._ui.addScanItemButton.setVisible(True)
        self._ui.scanlistListWidget.setVisible(True)

    @pyqtSlot(dict)
    def on_populate_examCardListView(self, exam_card_data):
        self.exam_card_qmodel = DictionaryModel(exam_card_data)
        self._ui.examCardListView.setModel(self.exam_card_qmodel)    

    def on_examCardListView_dclicked(self, index):
        scan_item = self._ui.examCardListView.model().get_data(index)
        key = self._ui.examCardListView.model().itemFromIndex(index).text()
        self._main_controller.handle_add_to_scanlist(key, scan_item)

    @pyqtSlot(list)
    def on_update_scanlistListWidget(self, list):
        self._ui.scanlistListWidget.clear()
        self._ui.scanlistListWidget.addItems([item.name for item in list])
