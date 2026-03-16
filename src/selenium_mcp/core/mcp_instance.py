from mcp.server.fastmcp import FastMCP
from selenium_mcp.utils.logger import logger

try:
    mcp = FastMCP(
        "selenium-mcp-server"
    )
except Exception as e:
    logger.error(f"Initialization failed. Error: {e}")
