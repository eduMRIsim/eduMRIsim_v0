from enum import Enum, auto


class EventEnum(Enum):
    """Enum class for events. Each event is represented by a unique value. The values are automatically assigned by the auto() function. The events are used to notify the observers of changes in the model (i.e., model of the model-view-controller architecture which in this app is an abstraction of the scanner).

    In the future it might make sense to create a separate class for each event type, but for now, we will keep it simple and use this enum class. It may also make sense in the future to create Event classes that contain more information about the event, such as the object that triggered the event, the data associated with the event, etc instead of using just an enumeration.
    """

    # Scan volume events
    SCAN_VOLUME_DISPLAY_TRANSLATED = (
        auto()
    )  # Event for when the scan volume display is translated, i.e., when the user moves the scan volume display object in a viewing window on the UI
    SCAN_VOLUME_CHANGED = (
        auto()
    )  # Event for when the scan volume is updated, i.e., when the scan volume parameters are changed
    SCAN_VOLUME_DISPLAY_ROTATED = auto()  # Event for when the scan volume is rotated
    SCAN_VOLUME_DISPLAY_SCALED = auto()

    # Scanlist events
    SCANLIST_ITEM_ADDED = (
        auto()
    )  # Event for when a scanlist item is added to the scanlist
    SCANLIST_ITEM_REMOVED = (
        auto()
    )  # Event for when a scanlist item is removed from the scanlist
    SCANLIST_ACTIVE_INDEX_CHANGED = (
        auto()
    )  # Event for when the active index of the scanlist is changed

    # Scan item events
    SCAN_ITEM_STATUS_CHANGED = (
        auto()
    )  # Event for when the status of a scanlist element is changed, e.g., from 'BEING_MODIFIED' to 'READY_TO_SCAN'
    SCAN_ITEM_PARAMETERS_CHANGED = (
        auto()
    )  # Event for when the scan parameters of a scan item are changed

    # stack events
    STACK_CHANGED = auto()
    ADD_STACK = auto()
    DELETE_STACK = auto()
