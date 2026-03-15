from instance.mcp_instance import mcp

from tools.browser_tools import *
from tools.navigation_tools import *
from tools.interaction_tools import *
from tools.element_tools import *
from tools.page_tools import *
from tools.debug_tools import *

from utils.logger import logger

SELENIUM_MCP_SERVER_VERSION = "0.2.1"

if __name__ == "__main__":
    logger.info(
        f"Starting Selenium MCP Server v{SELENIUM_MCP_SERVER_VERSION}...")
    mcp.run(transport="stdio")
