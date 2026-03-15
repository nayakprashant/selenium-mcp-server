from mcp.server.fastmcp import FastMCP
from utils.logger import logger
from core.version import SELENIUM_MCP_SERVER_VERSION

logger.info(
    f"Initializing Selenium MCP Server - v{SELENIUM_MCP_SERVER_VERSION}")

mcp = FastMCP(
    "selenium-mcp-server"
)
