from mcp.server.fastmcp import FastMCP
from utils.logger import logger

logger.info("Initializing Selenium MCP Server...")

mcp = FastMCP(
    "selenium-mcp-server"
)
