from PyQt5.QtWidgets import QAction


class MenuBar:
    def __init__(self, main_view):
        self.main_view = main_view
        self.menu_bar = self.main_view.menuBar()
        self.menus = {}

    def add_section(self, menu_name):
        """Adds new section to the menu."""
        menu = self.menu_bar.addMenu(menu_name)
        self.menus[menu_name] = menu
        return menu

    def add_action(self, section_name, action_name, triggered_function):
        """Adds an action to a section."""
        if section_name in self.menus:
            action = QAction(action_name, self.main_view)
            action.triggered.connect(triggered_function)
            self.menus[section_name].addAction(action)
        else:
            raise ValueError(f"Menu '{section_name}' does not exist.")
