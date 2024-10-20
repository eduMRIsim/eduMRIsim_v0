from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QTabWidget,
    QScrollArea,
    QGridLayout,
    QLineEdit,
    QLabel,
    QComboBox,
    QPushButton,
)

from typing import Optional
from events import EventEnum
from utils.block_signals import block_signals
from views.styled_widgets import (
    PrimaryActionButton,
    SecondaryActionButton,
    DestructiveActionButton,
    HeaderLabel,
)


class ScanParametersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self._createScanParametersTabWidget()
        self._createButtons()

    @property
    def parameterFormLayout(self):
        return self.scanParametersTabWidget.parameterFormLayout

    @property
    def stackParametersFormLayout(self):
        return self.scanParametersTabWidget.stackParametersFormLayout

    @property
    def scanParametersSaveChangesButton(self):
        return self._scanParametersSaveChangesButton

    @property
    def scanParametersExportButton(self):
        return self._scanParametersExportButton

    @property
    def scanParametersCancelChangesButton(self):
        return self._scanParametersCancelChangesButton

    @property
    def scanParametersResetButton(self):
        return self._scanParametersResetButton

    def _createScanParametersTabWidget(self):
        self.scanParametersTabWidget = ScanParametersTabWidget()
        self.layout.addWidget(self.scanParametersTabWidget)

    def _createButtons(self):
        buttonsLayout = QHBoxLayout()
        self._scanParametersSaveChangesButton = PrimaryActionButton("Save")
        self._scanParametersExportButton = SecondaryActionButton("Export")
        self._scanParametersCancelChangesButton = SecondaryActionButton("Cancel")
        self._scanParametersResetButton = DestructiveActionButton("Reset")
        buttonsLayout.addWidget(self._scanParametersSaveChangesButton, 1)
        buttonsLayout.addWidget(self._scanParametersExportButton, 1)
        buttonsLayout.addWidget(self._scanParametersCancelChangesButton, 1)
        buttonsLayout.addSpacerItem(
            QSpacerItem(
                self._scanParametersSaveChangesButton.sizeHint().width(),
                self._scanParametersSaveChangesButton.sizeHint().height(),
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum,
            )
        )
        buttonsLayout.addWidget(self._scanParametersResetButton, 1)
        self.layout.addLayout(buttonsLayout)


class ScanParametersTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.parameterTab = ParameterTab()
        self.stackParametersTab = StackParametersTab()
        self.addTab(self.parameterTab, "Scan parameters")
        self.addTab(self.stackParametersTab, "Stack parameters")

    @property
    def parameterFormLayout(self):
        return self.parameterTab.parameterFormLayout

    @property
    def stackParametersFormLayout(self):
        return self.stackParametersTab.stackParametersFormLayout


class StackParametersTab(QScrollArea):
    def __init__(self):
        super().__init__()
        container_widget = self.createContainerWidget()
        self.setWidget(container_widget)
        self.setWidgetResizable(True)

    def createContainerWidget(self):
        self.horizontalLayout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self._stackParametersFormLayout = StackParametersFormLayout()
        self.layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        self.layout.addLayout(self.stackParametersFormLayout)
        self.layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        # self.horizontalLayout.addItem(QSpacerItem(10, 0,  QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.horizontalLayout.addLayout(self.layout)
        self.horizontalLayout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.setStyleSheet("QLineEdit { border: 1px solid  #BFBFBF; }")
        containerWidget = QWidget()
        containerWidget.setLayout(self.horizontalLayout)
        return containerWidget

    @property
    def stackParametersFormLayout(self):
        return self._stackParametersFormLayout


class ParameterTab(QScrollArea):
    def __init__(self):
        super().__init__()
        container_widget = self.createContainerWidget()
        self.setWidget(container_widget)
        self.setWidgetResizable(True)

    def createContainerWidget(self):
        self.horizontalLayout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self._parameterFormLayout = ParameterFormLayout()
        self.layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        self.layout.addLayout(self.parameterFormLayout)
        self.layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        # self.horizontalLayout.addItem(QSpacerItem(10, 0,  QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.horizontalLayout.addLayout(self.layout)
        self.horizontalLayout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.setStyleSheet("QLineEdit { border: 1px solid  #BFBFBF; }")
        containerWidget = QWidget()
        containerWidget.setLayout(self.horizontalLayout)
        return containerWidget

    @property
    def parameterFormLayout(self):
        return self._parameterFormLayout


class ParameterFormLayout(QVBoxLayout):
    formActivatedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.isReadOnly = True
        self.editors = {}

    def createForm(self, parameters: dict) -> None:
        # Create form elements based on the data in "parameters".
        for parameter in parameters:
            name = parameter["name"]
            parameter_key = parameter["key"]
            editor_type = parameter["editor"]
            default_value = parameter["default_value"]
            unit = parameter["unit"]

            parameter_layout = QGridLayout()

            # Create the appropriate editor widget based on the editor type.
            if editor_type == "QLineEdit":
                editor = QLineEdit()
                editor.setText(default_value)
                if parameter_key != "StackIndex":
                    parameter_layout.addWidget(
                        QLabel(name), 0, 0, Qt.AlignmentFlag.AlignLeft
                    )
                parameter_layout.addWidget(editor, 1, 0, Qt.AlignmentFlag.AlignLeft)
                parameter_layout.addWidget(
                    HeaderLabel(unit), 1, 1, Qt.AlignmentFlag.AlignLeft
                )
                editor.textChanged.connect(lambda: self.formActivatedSignal.emit())
            elif editor_type == "QComboBox":
                editor = QComboBox()
                editor.addItems(default_value)
                editor.setCurrentIndex(0)
                parameter_layout.addWidget(
                    QLabel(name), 0, 0, Qt.AlignmentFlag.AlignLeft
                )
                parameter_layout.addWidget(editor, 1, 0, Qt.AlignmentFlag.AlignLeft)
                editor.currentIndexChanged.connect(
                    lambda: self.formActivatedSignal.emit()
                )
            else:
                raise ValueError(
                    f"Unknown editor type: {editor_type}"
                )  # Raise an error if the editor type is unknown. If the error is raised, the program will stop executing.

            if parameter_key == "StackIndex":
                editor.setVisible(False)
            editor.setFixedHeight(30)
            editor.setFixedWidth(300)
            editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            # Add the editor widget to the layout.

            self.addLayout(parameter_layout)

            # Add a vertical spacer (with expandable space)
            spacer = QSpacerItem(
                20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
            self.addSpacerItem(spacer)

            # Store the editor widget in the dictionary for later access.
            self.editors[parameter_key] = editor

    def save_state(self):
        params = self.get_parameters()
        return params

    def get_parameters(self):
        # Create a dictionary to store the current values of the editor widgets.
        parameters = {}

        # Get the current value of each editor widget and store it in a dictionary.
        for name, editor in self.editors.items():
            if isinstance(editor, QLineEdit):
                parameters[name] = editor.text()
            elif isinstance(editor, QComboBox):
                parameters[name] = editor.currentText()
            else:
                raise ValueError(f"Unknown editor type: {type(editor)}")

        return parameters

    def set_parameters(self, parameters):
        # Set the data into the editors
        # TODO: check if parameters is list of parameters or dictionary object
        with block_signals(self.editors.values()):
            for name, value in parameters.items():
                if (
                    name in self.editors
                ):  # Checks if the string name is a key in the self.editors dictionary.
                    editor = self.editors[
                        name
                    ]  # Get the editor widget from the dictionary.
                    if isinstance(editor, QLineEdit):
                        editor.setText(str(value))
                    elif isinstance(editor, QComboBox):
                        index = editor.findText(str(value))
                        if index != -1:
                            editor.setCurrentIndex(index)

    def setReadOnly(self, read_only: bool):
        for editor in self.editors.values():
            if isinstance(editor, QLineEdit):
                editor.setReadOnly(read_only)
            if isinstance(editor, QComboBox):
                editor.setEnabled(not read_only)
        self.isReadOnly = read_only

    def clearForm(self):
        with block_signals(self.editors.values()):
            for editor in self.editors.values():
                if isinstance(editor, QLineEdit):
                    editor.clear()
                elif isinstance(editor, QComboBox):
                    editor.setCurrentIndex(0)


class StackParametersFormLayout(QVBoxLayout):
    stackSignal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.isReadOnly = True
        self.editor: Optional[QComboBox] = None
        self.nr_of_stacks = 1
        self.delete_stack_btn: Optional[QPushButton] = None
        self.selected_stack_index = 0
        self.createForm()

    def get_stacks_params(self) -> dict:
        return {
            "nr_of_stacks": self.nr_of_stacks,
            "selected_stack_index": self.selected_stack_index,
        }

    def delete_stack_event(self, new_stack_index, nr_of_stacks):
        # TODO: disable delete stack button when only one stack is left
        self.editor.clear()
        self.nr_of_stacks = nr_of_stacks
        stack_indices = [str(stack_inx) for stack_inx in range(nr_of_stacks)]
        self.editor.addItems(stack_indices)
        self.selected_stack_index = new_stack_index
        self.editor.setCurrentIndex(new_stack_index)
        if nr_of_stacks == 1:
            self.delete_stack_btn.setDisabled(True)

    def set_stacks_params(self, params: dict) -> dict:
        if (
            params.get("nr_of_stacks") is not None
            and params.get("selected_stack_index") is not None
        ):
            nr_of_stacks = params["nr_of_stacks"]
            stack_indices = [str(stack_inx) for stack_inx in range(nr_of_stacks)]
            self.selected_stack_index = params["selected_stack_index"]
            self.nr_of_stacks = nr_of_stacks
            if nr_of_stacks > 1:
                self.delete_stack_btn.setDisabled(False)
            else:
                self.delete_stack_btn.setDisabled(True)
            self.editor.clear()
            self.editor.addItems(stack_indices)
            self.editor.setCurrentIndex(params["selected_stack_index"])
            # self.stack_change_handle(self.editor)

    def createForm(self) -> None:
        parameter_layout = QGridLayout()
        stack_indices_options = [
            str(stack_inx) for stack_inx in range(self.nr_of_stacks)
        ]
        editor = QComboBox()
        editor.addItems(stack_indices_options)
        editor.setCurrentIndex(self.selected_stack_index)
        editor.currentIndexChanged.connect(lambda: self.stack_change_handle(editor))

        parameter_layout.addWidget(
            QLabel("Stack index"), 0, 0, Qt.AlignmentFlag.AlignLeft
        )
        parameter_layout.addWidget(editor, 1, 0, Qt.AlignmentFlag.AlignLeft)

        editor.setFixedHeight(30)
        editor.setFixedWidth(300)
        editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Add the editor widget to the layout.

        self.addLayout(parameter_layout)

        # Add a vertical spacer (with expandable space)
        spacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.addSpacerItem(spacer)
        self.editor = editor

        add_stack_button = PrimaryActionButton("Add stack")
        add_stack_button.clicked.connect(self.add_stack_handle)
        delete_stack_button = PrimaryActionButton("Delete stack")
        delete_stack_button.clicked.connect(
            lambda: self.stackSignal.emit({"event": EventEnum.DELETE_STACK})
        )
        self.delete_stack_btn = delete_stack_button
        if self.nr_of_stacks == 1:
            delete_stack_button.setDisabled(True)
        self.addWidget(add_stack_button)
        self.addSpacerItem(spacer)

        self.addWidget(delete_stack_button)
        self.addSpacerItem(spacer)

    def add_stack_handle(self):
        self.stackSignal.emit({"event": EventEnum.ADD_STACK})
        self.editor.addItem(str(self.nr_of_stacks))
        if self.nr_of_stacks == 1:
            self.delete_stack_btn.setDisabled(False)
        self.nr_of_stacks += 1

    def stack_change_handle(self, editor):
        stack_indices = [str(stack_inx) for stack_inx in range(self.nr_of_stacks)]
        self.selected_stack_index = editor.currentIndex()
        self.stackSignal.emit(
            {
                "event": EventEnum.STACK_CHANGED,
                "stack_index": int(stack_indices[editor.currentIndex()]),
            }
        )
