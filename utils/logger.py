import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("selenium_mcp_server.log")
    ],
    force=True
)

logger = logging.getLogger("selenium-mcp-server")
