import logging
from rich.logging import RichHandler
from PyQt6 import QtCore
import numpy as np

# Set up logging
# To log messages, use "from utils.logger import log"
# You can send messages depending on their severity level:
# log.debug("Debug message")
# log.info("Info message")
# log.warning("Warning message")
# log.error("Error message")
# log.critical("Critical message")

# you can launch the application with the --log-level flag to set the log level
# e.g. python main.py --log-level DEBUG

# When deploying the application, you can set the log level to INFO or WARNING

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


# Context is not used, but it is required by the Qt message handler
# This function routes Qt messages to Python's logging module (which is linked to the RichHandler)
def qt_message_handler(mode, context, message):
    """
    Intercept Qt log messages and send them to Python's logging module.
    """
    if mode == QtCore.QtMsgType.QtInfoMsg:
        log.info(f"QtInfo: {message}")
    elif mode == QtCore.QtMsgType.QtWarningMsg:
        log.warning(f"QtWarning: {message}")
    elif mode == QtCore.QtMsgType.QtCriticalMsg:
        log.error(f"QtCritical: {message}")
    elif mode == QtCore.QtMsgType.QtFatalMsg:
        log.critical(f"QtFatal: {message}")
    else:
        log.debug(f"QtDebug: {message}")


def numpy_handler():
    np.seterr(all="warn")
    logging.captureWarnings(True)
