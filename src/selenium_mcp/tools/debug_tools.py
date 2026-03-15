from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import *
import os
from selenium_mcp.utils.logger import logger
from selenium_mcp.utils.generics import hex_token
from pathlib import Path

DEFAULT_SCREENSHOT_DIR = Path.home() / ".selenium-mcp" / "screenshot"

SCREENSHOT_DIR = Path(
    os.getenv("SELENIUM_MCP_SCREENSHOT_DIR", DEFAULT_SCREENSHOT_DIR)
)

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


@mcp.tool()
def take_screenshot(session_id: str):
    """
    Capture a screenshot of the current browser window.

    Purpose
    -------
    Useful for debugging, failure reporting, or visual analysis.
    Screenshots are saved to the directory set by the
    MCP_SCREENSHOT_DIR environment variable (default: system temp dir).

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {"status": "success", "path": str}  — absolute file path
    """
    logger.info(f"take_screenshot: session ID = {session_id}")
    driver = get_driver(session_id)
    filename = f"screenshot_{session_id}_{hex_token(5)}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(path)
    return {"status": "success", "path": path}
