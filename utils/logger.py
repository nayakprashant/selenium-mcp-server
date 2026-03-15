import logging
import os
from logging.handlers import TimedRotatingFileHandler

# Go one level up from utils/
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logs folder in project root
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, "selenium_mcp_server.log")

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)

logger = logging.getLogger("selenium-mcp-server")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
