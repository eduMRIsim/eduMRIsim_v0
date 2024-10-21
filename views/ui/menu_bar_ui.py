from PyQt6.QtGui import QAction, QActionGroup, QShortcut

from views.ui.shortcut_dialog_ui import ShortcutDialog


class MenuBar:
    __instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ to implement singleton behaviour."""
        if cls.__instance is None:
            cls.__instance = super(MenuBar, cls).__new__(cls)
        return cls.__instance

    def __init__(self, main_view, main_controller, load_examination_callback):
        """Initialises the menu bar, stores sections and controller."""
        if hasattr(self, "_initialized") and self._initialized:
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

    def add_section(self, section_name) -> "Section":
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

        save_session_shortcut = QShortcut("Ctrl+S", self.main_view)
        save_session_shortcut.activated.connect(self.main_controller.export_examination)

        load_session_shortcut = QShortcut("Ctrl+L", self.main_view)
        load_session_shortcut.activated.connect(self.load_examination_callback)

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

        switch_modes_shortcut = QShortcut("Ctrl+M", self.main_view)
        switch_modes_shortcut.activated.connect(
            lambda: self.main_view._stackedLayout.setCurrentIndex(
                1 if self.main_view._stackedLayout.currentIndex() == 0 else 0
            )
        )

        # Tools section
        tools_section = self.add_section("Tools")
        tools_section.add_action(
            "Measure Distance",
            lambda: self.main_controller.handle_measureDistanceButtonClicked(),
            checkable=True,
        )
        # measure_distance_shortcut = QShortcut("Ctrl+D", self.main_view)
        # measure_distance_shortcut.activated.connect(lambda: self.main_controller.handle_measureDistanceButtonClicked())

        window_level_action: QAction = tools_section.add_action(
            "Window Level Mode",
            lambda: self.main_controller.handle_toggleWindowLevelButtonClicked(),
            checkable=True,
        )

        def update_window_level_action():
            window_level_action.toggle()
            self.main_controller.handle_toggleWindowLevelButtonClicked()

        window_level_shortcut = QShortcut("Ctrl+W", self.main_view)
        window_level_shortcut.activated.connect(lambda: update_window_level_action())

        # WARNING: not implemented yet
        tools_section.add_action("Measure Area", self.test_action, checkable=False)
        measure_area_shortcut = QShortcut("Ctrl+A", self.main_view)
        measure_area_shortcut.activated.connect(self.test_action)

        # Help section
        help_section = self.add_section("Help")
        help_section.add_action("Keyboard Shortcuts", lambda: ShortcutDialog().exec())
        help_shortcut = QShortcut("Ctrl+H", self.main_view)
        help_shortcut.activated.connect(lambda: ShortcutDialog().exec())

        # Color Scale section
        color_scale_section = self.add_section("Color Scale")
        color_scale_section.add_mode_action_group()
        color_scale_section.add_mode_action(
            "Black and White",
            lambda: self.main_controller.handle_changeColorMapping("bw"),
            checked=True,
        )
        color_scale_section.add_mode_action(
            "RGB", lambda: self.main_controller.handle_changeColorMapping("rgb")
        )

        # Contrast linking section
        contrast_linking_section = self.add_section("Contrast Linking")
        contrast_linking_section.menu.aboutToShow.connect(
            lambda: self.main_controller.handle_show_checkboxes(True)
        )
        contrast_linking_section.add_mode_action_group()
        contrast_linking_section.add_mode_action(
            "Start linking",
            lambda: self.main_controller.handle_start_contrastLinking(),
            checked=False,
        )
        contrast_linking_section.add_mode_action(
            "Stop linking",
            lambda: self.main_controller.handle_stop_contrastLinking(),
            checked=False,
        )

    def test_action(self):
        pass


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