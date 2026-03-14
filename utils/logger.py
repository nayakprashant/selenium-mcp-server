import logging
import os

log_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "selenium_mcp_server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_path)
    ],
    force=True
)

logger = logging.getLogger("selenium-mcp-server")
