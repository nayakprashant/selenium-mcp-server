from core.mcp_instance import mcp
from core.browser_factory import create_driver
from core.session_manager import *

from utils.logger import logger

import uuid


@mcp.tool()
def open_browser(browser: str = "chrome", headless: bool = False):
    """
    Launch a new browser session.

    Purpose
    -------
    Creates a Selenium WebDriver instance and registers it in the MCP
    session store. The returned `session_id` must be passed to all
    subsequent browser tool calls.

    Typical Agent Workflow
    ----------------------
    1. open_browser
    2. open_url
    3. wait_for_page
    4. interact with elements

    Parameters
    ----------
    browser : str
        Browser type to launch (default: "chrome").
    headless : bool
        Run without a visible window (default: False). Set True on
        servers, Docker containers, or CI environments.

    Returns
    -------
    dict
        {"session_id": str, "browser": str, "headless": bool}

    Note
    -----
    Only call this tool ONCE per workflow, unless explicitly instructed.
    Do not call it again unless the previous browser session was closed.
    """
    logger.info(f"open_browser: browser = {browser}, headless = {headless}")
    driver = create_driver(browser, headless)

    session_id = str(uuid.uuid4())
    add_session(session_id, driver)
    logger.info(f"open_browser: session ID {session_id} created")
    return {
        "session_id": session_id,
        "browser": browser,
        "headless": headless
    }


@mcp.tool()
def close_browser(session_id: str):
    """
    Close the browser session and free its resources.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """

    logger.info(f"close_browser: session ID = {session_id}")

    driver = get_driver(session_id)
    driver.quit()
    del sessions[session_id]
    return {"message": "Browser closed", "session_id": session_id}


@mcp.tool()
def maximize_browser(session_id: str):
    """
    Maximize the browser window.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    logger.info(f"maximize_browser: session ID = {session_id}")
    driver = get_driver(session_id)
    driver.maximize_window()
    return {"session_id": session_id, "message": "Browser window maximized"}


@mcp.tool()
def fullscreen_browser(session_id: str):
    """
    Switch the browser to fullscreen mode.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    logger.info(f"fullscreen_browser: session ID = {session_id}")
    driver = get_driver(session_id)
    driver.fullscreen_window()
    return {"session_id": session_id, "message": "Browser switched to fullscreen mode"}
