from mcp.server.fastmcp import FastMCP
from selenium_mcp.utils.logger import logger

logger.info(
    f"Initializing Selenium MCP Server...")

mcp = FastMCP(
    "selenium-mcp-server"
)
