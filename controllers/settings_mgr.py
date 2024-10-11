import glob
from PyQt6.QtCore import QSettings
from events import EventEnum
from simulator.scanner import Scanner


class SettingsManager:
    _instance = None

    # singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, scanner: Scanner, main_ctrl, main_view, file_name: str):
        if not hasattr(self, "initialized"):
            self.scanner = scanner
            self.main_controller = main_ctrl
            self.file_name = file_name
            self.main_view = main_view
            self.settings = QSettings(file_name, QSettings.Format.IniFormat)
            self.initialized = True

    def setup_settings(self, settings_file: str = None) -> None:
        # The settings file are for now saved in the working directory.
        # This might change in the future to a more appropriate location such as native app data directory.
        if settings_file is None:
            settings_file = "./settings.ini"

        self.settings = QSettings(settings_file, QSettings.Format.IniFormat)

        state_name = self.settings.value(
            "currentState", defaultValue="IdleState", type=str
        )

        if state_name == "ScanCompleteState" or state_name == "ReadyToScanState":
            exam_name = self.settings.value("exam_name", defaultValue="", type=str)
            model_name = self.settings.value("model_name", defaultValue="", type=str)
            self.main_controller.prepare_model_data()
            self.main_controller.handle_newExaminationOkButton_clicked(
                exam_name, model_name
            )
            scannerState = self.settings.value(
                "scannerState", defaultValue={}, type=dict
            )
            scan_list_items = scannerState.get("scanlist")
            scan_list_params = scannerState.get("params")
            scan_list_status = scannerState.get("status")
            scan_list_data = scannerState.get("data")

            if scan_list_items is not None:
                for i in range(len(scan_list_items)):
                    # self.scanner.scanlist.add_scanlist_element(
                    #     scan_list_items[i], scan_list_params[i]
                    # )
                    # scanlist params are stored now as a list
                    self.scanner.scanlist.add_scanlist_element_multi(
                        scan_list_items[i], scan_list_params[i]
                    )
                    self.main_controller.update(EventEnum.SCANLIST_ITEM_ADDED)
                    self.scanner.scanlist.notify_observers(
                        EventEnum.SCANLIST_ITEM_ADDED
                    )

                    self.scanner.scanlist.scanlist_elements[i].acquired_data = (
                        scan_list_data[i]
                    )
                    self.scanner.scanlist.scanlist_elements[i].scan_item.status = (
                        scan_list_status[i]
                    )
                    self.main_controller.update(EventEnum.SCAN_ITEM_STATUS_CHANGED)
                    self.scanner.scanlist.notify_observers(
                        EventEnum.SCAN_ITEM_STATUS_CHANGED
                    )

                    self.main_controller.update_scanlistListWidget(
                        self.scanner.scanlist
                    )

        self.main_view.restore_settings()

    def is_previous_session(self) -> bool:
        # Scan current working directory for settings files
        settings_files = glob.glob("settings.ini")

        from utils.logger import log

        log.info(f"settings_files: {settings_files}")

        if len(settings_files) > 0:
            return True
        return False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("SettingsManager not initialized")
        return cls._instance

    @property
    def settings_file(self):
        return self.file_name

    def settings(self):
        return self.settings

    def set_settings(self, settings):
        self.settings = settings

    def export_settings(self, settings_file: str = None) -> None:
        self.settings.sync()
        self.main_view.save_settings()

        settings_tmp = QSettings(settings_file, QSettings.Format.IniFormat)
        # settings_tmp.clear()

        for key in self.settings.allKeys():
            settings_tmp.setValue(key, self.settings.value(key))
