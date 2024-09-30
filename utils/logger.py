import logging
from rich.logging import RichHandler

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
