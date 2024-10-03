from PyQt5.QtWidgets import QAction, QActionGroup

class MenuBar:
    def __init__(self, main_view):
        """Initialises the menu bar and stores sections."""
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
        """Initialises a section and prepares to manage its actions."""
        self.menu_bar = menu_bar
        self.section_name = section_name
        self.menu = self.menu_bar.addMenu(section_name)
        self.actions = {}
        self.action_group = None

    def add_action(self, action_name, triggered_function):
        """Adds a regular action to the section."""
        action = QAction(action_name, self.menu)
        action.triggered.connect(triggered_function)
        self.actions[action_name] = action
        self.menu.addAction(action)

    def add_mode_action_group(self):
        """Creates a manual action group."""
        self.action_group = {}  # Dictionary to store mode actions

    def add_mode_action(self, action_name, triggered_function, condition=None):
        """Adds an action to the manual mode group without any checked state."""
        if self.action_group is None:
            raise Exception("Call add_mode_action_group before adding mode actions.")
        
        # Create the action
        action = QAction(action_name, self.menu)
        action.triggered.connect(lambda: self._switch_mode(action_name, triggered_function, condition))
        self.action_group[action_name] = action
        self.menu.addAction(action)

        self.actions[action_name] = action

    def _switch_mode(self, action_name, triggered_function, condition):
        """Switches the mode if the condition is met."""
        if condition is None or condition():  # Check if the condition is satisfied
            triggered_function()  # Execute the function linked to the mode
        else:
            print(f"Condition for {action_name} not met.")
