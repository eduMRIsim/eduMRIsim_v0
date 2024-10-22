import glob
import os

from PyQt5.QtCore import QStandardPaths
from PyQt6.QtCore import QSettings

from events import EventEnum
from simulator.scanner import Scanner
from utils.logger import log


class SettingsManager:
    _instance = None

    # singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, scanner: Scanner, main_ctrl, main_view, file_name: str = None):
        if not hasattr(self, "initialized"):
            self.scanner = scanner
            self.main_controller = main_ctrl

            if file_name is None:
                file_name = os.path.join(
                    QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                    "eduMRIsim",
                    "sessions",
                    "settings.ini",
                )
            else:
                self.file_name = file_name

            self.main_view = main_view
            self.settings = QSettings(file_name, QSettings.Format.IniFormat)
            self.initialized = True

            self.os_settings_dir = (
                QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
                + "/eduMRIsim/"
            )

            os.makedirs(self.os_settings_dir, exist_ok=True)
            log.info(f"SETTINGSDIR={self.os_settings_dir}")

            os.makedirs(self.os_settings_dir + "/sessions/", exist_ok=True)
            log.info(f"SESSIONDIR={self.os_settings_dir}/sessions/")

            os.makedirs(self.os_settings_dir + "/scan_items/", exist_ok=True)
            log.info(f"SCANITEMDIR={self.os_settings_dir}/scan_items/")

    def setup_settings(self, settings_file: str = None) -> None:
        # The settings file are for now saved in the working directory.
        # This might change in the future to a more appropriate location such as native app data directory.
        if settings_file is None:
            settings_file = os.path.join(
                self.os_settings_dir, "sessions", "settings.ini"
            )

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
            active_idx = scannerState.get("active_idx", 0)

            if scan_list_items is not None:
                for i in range(len(scan_list_items)):
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
                    self.scanner.scanlist.scanlist_elements[i].scan_item.add_observer(
                        self.main_controller
                    )

                    self.main_controller.update(EventEnum.SCAN_ITEM_STATUS_CHANGED)
                    self.scanner.scanlist.notify_observers(
                        EventEnum.SCAN_ITEM_STATUS_CHANGED
                    )

                    self.main_controller.update_scanlistListWidget(
                        self.scanner.scanlist
                    )
                # Set active scan item index

            if len(self.scanner.scanlist.scanlist_elements) > 0:
                # Ensure the active index is within valid range
                if 0 <= active_idx < len(self.scanner.scanlist.scanlist_elements):
                    self.scanner.scanlist.active_idx = active_idx
                else:
                    self.scanner.scanlist.active_idx = 0
            else:
                self.scanner.scanlist.active_idx = None

            # Update the UI
            self.main_controller.update(EventEnum.SCANLIST_ACTIVE_INDEX_CHANGED)
            self.main_controller.update_scanlistListWidget(self.scanner.scanlist)

        self.main_view.restore_settings()

    def is_previous_session(self) -> bool:
        settings_files = glob.glob(self.os_settings_dir + "/sessions/*.ini")

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
