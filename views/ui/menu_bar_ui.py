from PyQt6.QtGui import QAction, QActionGroup

class MenuBar:
    __instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ to implement singleton behaviour."""
        if cls.__instance is None:
            cls.__instance = super(MenuBar, cls).__new__(cls)
        return cls.__instance

    def __init__(self, main_view, main_controller, load_examination_callback):
        """Initialises the menu bar, stores sections and controller."""
        if hasattr(self, '_initialized') and self._initialized:
            # Prevent re-initialisation if the instance already exists
            return
        self.main_view = main_view
        self.menu_bar = self.main_view.menuBar()
        self.sections = {}
        self.main_controller = main_controller
        self.load_examination_callback = load_examination_callback

        self.setup_menu_bar()

        # Mark this instance as initialized to prevent reinitialization
        self._initialized = True

    def add_section(self, section_name):
        """Adds a section to the menu."""
        section = Section(self.menu_bar, section_name)
        self.sections[section_name] = section
        return section

    def setup_menu_bar(self):
        """Set up the entire menu bar with relevant sections and actions."""
        # Session section
        session_section = self.add_section("Session")
        session_section.add_action(
            "Save session", self.main_controller.export_examination
        )
        session_section.add_action("Load session", self.load_examination_callback)

        # Mode section
        mode_section = self.add_section("Mode")
        mode_section.add_mode_action_group()
        mode_section.add_mode_action(
            "Scanning Mode",
            lambda: self.main_view._stackedLayout.setCurrentIndex(0),
            checked=True,
        )
        mode_section.add_mode_action(
            "Viewing Mode", lambda: self.main_view._stackedLayout.setCurrentIndex(1)
        )

        # Tools section
        tools_section = self.add_section("Tools")
        tools_section.add_mode_action_group()
        
        tools_section.add_mode_action(
            "Measure Distance",
            lambda: self.main_controller.handle_measureDistanceButtonClicked(),
        )

        tools_section.add_mode_action(
            "Window Level",
            lambda: self.main_controller.handle_toggleWindowLevelButtonClicked(),
        )


class Section:
    def __init__(self, menu_bar, section_name):
        """Initialises a section and prepares to manage its actions."""
        self.menu_bar = menu_bar
        self.section_name = section_name
        self.menu = self.menu_bar.addMenu(section_name)
        self.actions = {}
        self.action_group = None

    def add_action(self, action_name, triggered_function, checkable=False):
        """Adds a regular action to the section."""
        action = QAction(action_name, self.menu)

        if checkable:
            action.setCheckable(True)
            action.setChecked(False)

        action.triggered.connect(triggered_function)
        self.actions[action_name] = action
        self.menu.addAction(action)

    def add_mode_action_group(self):
        """Creates an action group for mutually exclusive actions."""
        self.action_group = QActionGroup(self.menu)
        self.action_group.setExclusive(
            True
        )  # Ensure only one action can be checked at a time

    def add_mode_action(self, action_name, triggered_function, checked=False):
        """Adds an action to the action group with mutually exclusive checking."""
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
