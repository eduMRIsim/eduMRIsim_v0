from view import NewExaminationDialog, LoadExaminationDialog

class Controller:

    def __init__(self, view):
        self._view = view
        self._connectSignalsandSlots()

    def _connectSignalsandSlots(self):
        new_examination_button = self._view.getNewExaminationButton()
        new_examination_button.clicked.connect(lambda:NewExaminationDialog().exec())

        load_examination_button = self._view.getLoadExaminationButton()
        load_examination_button.clicked.connect(lambda: LoadExaminationDialog().exec())

