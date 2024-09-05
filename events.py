from enum import Enum


class EventEnum(Enum):
    SCAN_VOLUME_DISPLAY_TRANSLATED = 1 # Event for when the scan volume display is translated, i.e., when the user moves the scan volume display object in a viewing window on the UI
    SCAN_VOLUME_UPDATED = 2 # Event for when the scan volume is updated, i.e., when the scan volume parameters are changed 