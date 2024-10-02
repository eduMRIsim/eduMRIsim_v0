from PyQt5.QtWidgets import QAction, QActionGroup

class MenuBar:
    def __init__(self, main_view):
        self.main_view = main_view
        self.menu_bar = self.main_view.menuBar()
        self.sections = {}

    def add_section(self, section_name):
        """Adds a section to the menu."""
        section = Section(self.menu_bar, section_name)
        self.sections[section_name] = section
        return section

class Section:
    def __init__(self, menu_bar, section_name):
        self.menu_bar = menu_bar
        self.section_name = section_name
        self.menu = self.menu_bar.addMenu(section_name)
        self.actions = {}

    def add_action(self, action_name, triggered_function):
        """Adds an action to a section."""
        action = Action(self.menu, action_name, triggered_function)
        self.actions[action_name] = action
        self.menu.addAction(action.qaction)
        return action

    def add_action_group(self):
        """Creates an action group."""
        action_group = QActionGroup(self.menu)
        action_group.setExclusive(True)  # Ensures only one action can be checked at a time
        return action_group

    def add_action_to_group(self, action_name, triggered_function, action_group, checked=False):
        """Adds an action to a group."""
        action = Action(self.menu, action_name, triggered_function, checkable=True)
        action_group.addAction(action.qaction)
        self.actions[action_name] = action
        self.menu.addAction(action.qaction)
        if checked:
            action.set_checked(True)
        return action

class Action:
    def __init__(self, parent_menu, action_name, triggered_function, checkable=False):
        self.action_name = action_name
        self.qaction = QAction(action_name, parent_menu)
        self.qaction.triggered.connect(triggered_function)
        if checkable:
            self.qaction.setCheckable(True)

    def set_checked(self, checked=True):
        """Sets an action to be checked or unchecked."""
        self.qaction.setChecked(checked)

    def is_checked(self):
        """Returns whether the action is currently checked."""
        return self.qaction.isChecked()
