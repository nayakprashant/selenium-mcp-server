from os import EX_CANTCREAT

from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.browser_factory import create_driver
from selenium_mcp.core.session_manager import *

from selenium_mcp.utils.logger import logger

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
        {"session_id": str, "browser": str, "headless": bool, "status": str, "message": str}

    Note
    -----
    Only call this tool ONCE per workflow, unless explicitly instructed.
    Do not call it again unless the previous browser session was closed.
    """

    log_info = f"open_browser: browser = {browser}, headless = {headless}"
    logger.info(f"Opening browser - {log_info}")

    session_id = None
    message = None
    status = "failure"

    try:
        driver = create_driver(browser, headless)
        session_id = str(uuid.uuid4())

        logger.info(f"Adding driver to the session - {session_id}")
        add_session(session_id, driver)

        status = "success"
        message = "Browser session created"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Browser could not be launched"

    return {
        "session_id": session_id,
        "browser": browser,
        "headless": headless,
        "status": status,
        "message": message
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
    log_info = f"close_browser: session ID = {session_id}"
    logger.info(f"Closing browser - {log_info}")

    message = None
    status = "failure"

    try:
        driver = get_driver(session_id)
        driver.quit()
        del sessions[session_id]

        message = "Browser closed"
        status = "success"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Browser could not be closed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def maximize_browser(session_id: str):
    """
    Maximize the browser window.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    log_info = f"maximize_browser: session ID = {session_id}"
    logger.info(f"Maximizing browser - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        driver.maximize_window()
        status = "success"
        message = "Browser window maximized"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Unable to maximize the browser window"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def fullscreen_browser(session_id: str):
    """
    Switch the browser to fullscreen mode.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    log_info = f"fullscreen_browser: session ID = {session_id}"
    logger.info(f"Making browser fullscreen - {log_info}")

    message = None
    status = "failure"

    try:
        driver = get_driver(session_id)
        driver.fullscreen_window()

        status = "success"
        message = "Browser switched to fullscreen mode"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not make the browser fullscreen"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }
