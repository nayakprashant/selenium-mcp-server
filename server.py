from mcp_instance import mcp

from tools.browser_tools import *
from tools.navigation_tools import *
from tools.interaction_tools import *
from tools.element_tools import *
from tools.page_tools import *
from tools.debug_tools import *

from utils.logger import logger

if __name__ == "__main__":
    logger.info("Selenium MCP server v0.2.0 started...")
    mcp.run(transport="stdio")
