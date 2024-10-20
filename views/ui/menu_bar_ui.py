from PyQt6.QtGui import QAction, QActionGroup


class MenuBar:
    def __init__(self, main_view):
        """Initialises the menu bar and stores sections."""
        self.main_view = main_view
        self.menu_bar = self.main_view.menuBar()
        self.sections = {}

    def add_section(self, section_name) -> 'Section':
        """Adds a section to the menu."""
        section = Section(self.menu_bar, section_name)
        self.sections[section_name] = section
        return section


class Section:
    def __init__(self, menu_bar, section_name):
        """Initialises a section and prepares to manage its actions."""
        self.menu_bar = menu_bar
        self.section_name = section_name
        self.menu = self.menu_bar.addMenu(section_name)
        self.actions = {}
        self.action_group = None

    def add_action(self, action_name, triggered_function, checkable=False) -> QAction:
        """Adds a regular action to the section."""
        action = QAction(action_name, self.menu)

        if checkable:
            action.setCheckable(True)
            action.setChecked(False)

        action.triggered.connect(triggered_function)
        self.actions[action_name] = action
        self.menu.addAction(action)

        return action

    def add_mode_action_group(self):
        """Creates an action group for mutually exclusive mode actions."""
        self.action_group = QActionGroup(self.menu)
        self.action_group.setExclusive(
            True
        )  # Ensure only one action can be checked at a time

    def add_mode_action(self, action_name, triggered_function, checked=False):
        """Adds an action to the manual mode group without any checked state."""
        if self.action_group is None:
            raise Exception("Call add_mode_action_group before adding mode actions.")

        action = QAction(action_name, self.menu)
        action.setCheckable(True)
        action.triggered.connect(triggered_function)

        self.action_group.addAction(action)
        self.menu.addAction(action)

        self.actions[action_name] = action

        if checked:
            action.setChecked(True)
        else:
            action.setChecked(False)
