from core.mcp_instance import mcp

from tools.browser_tools import *
from tools.navigation_tools import *
from tools.interaction_tools import *
from tools.element_tools import *
from tools.page_tools import *
from tools.debug_tools import *

from utils.logger import logger
from core.version import SELENIUM_MCP_SERVER_VERSION

if __name__ == "__main__":
    logger.info(
        f"Starting Selenium MCP Server - v{SELENIUM_MCP_SERVER_VERSION}")
    mcp.run(transport="stdio")
