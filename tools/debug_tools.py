from instance.mcp_instance import mcp
from core.session_manager import *
import os
from utils.logger import logger
from utils.generics import hex_token

SCREENSHOT_DIR = os.getenv("MCP_SCREENSHOT_DIR")


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
