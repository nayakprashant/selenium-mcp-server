from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import current_tab_index
from selenium_mcp.core.session_manager import *
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_mcp.utils.logger import logger


@mcp.tool()
def open_url(session_id: str, url: str):
    """
    Navigate the browser to a specific URL.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    url : str
        Full URL to open (must include scheme, e.g. https://).
    """
    log_info = f"open_url: session ID = {session_id}, url = {url}"
    logger.info(f"Opening URL - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        driver.get(url)
        status = "success"
        message = f"URL {url} opened successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = f"Could not open the URL - {url}"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def navigate_back(session_id: str):
    """
    Navigate back one step in browser history.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    log_info = f"navigate_back: session ID = {session_id}"
    logger.info(f"Navigating back - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        driver.back()
        status = "success"
        message = "Navigated back to the previous page"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Back navigation failed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def navigate_forward(session_id: str):
    """
    Navigate forward in browser history.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    log_info = f"navigate_forward: session ID = {session_id}"
    logger.info(f"Navigating forward - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        driver.forward()
        status = "success"
        message = "Navigated forward in browser history"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Forward navigation failed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def refresh_page(session_id: str):
    """
    Reload the current web page.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    log_info = f"refresh_page: session ID = {session_id}"
    logger.info(f"Refreshing page - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        driver.refresh()
        status = "success"
        message = "Page refreshed"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Page could not be refreshed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def wait_for_page(session_id: str, timeout: int = 10):
    """
    Wait until the page body element is present in the DOM.

    Purpose
    -------
    Call after `open_url` or any navigation to give the page time
    to load before attempting interactions.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    timeout : int
        Maximum seconds to wait (default: 10).

    Returns
    -------
    dict
        {
        "session_id": str,
        "timeout_set": timeout that was passed as a parameter,
        "status": str,
        "message": str
        }
    """
    log_info = f"wait_for_page: session ID = {session_id}, timeout = {timeout}"
    logger.info(f"Waiting for page to load - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        status = "success"
        message = "Page loaded successfuly and is ready to proceed"

    except TimeoutException:
        logger.exception(f"Error - {log_info}")
        message = f"Page did not load within {timeout} seconds"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = f"Page did not load"

    return {
        "session_id": session_id,
        "timeout_set": timeout,
        "status": status,
        "message": message
    }


@mcp.tool()
def get_tabs(session_id: str):
    """
    Retrieve all open browser tabs for the current session.

    Purpose
    -------
    Provides visibility into all tabs so the agent can decide which tab to switch to.

    Each tab is identified by an index and optional name.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {
            "session_id": str,
            "status": str,
            "message": str,
            "tabs": [
                {
                    "index": int,
                    "name": str,
                    "current": bool
                }
            ]
        }
    """
    log_info = f"get_tabs: session ID = {session_id}"
    logger.info(f"Getting tabs - {log_info}")

    status = "failure"
    message = None
    tabs_output = []

    try:
        driver = get_driver(session_id)

        # Always clean + sync before returning
        sync_tabs(session_id)

        tabs = get_tabs_for_session(session_id)

        for i, tab in enumerate(tabs):
            tabs_output.append({
                "index": i,
                "name": tab["name"],
                "current": driver.current_window_handle == tab["handle"]
            })

        status = "success"
        message = "Tabs retrieved successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not retrieve tabs"

    return {
        "session_id": session_id,
        "status": status,
        "message": message,
        "tabs": tabs_output
    }


@mcp.tool()
def get_current_tab(session_id: str):
    """
    Retrieve the currently active browser tab.

    Purpose
    -------
    Allows the agent to confirm which tab is currently active without listing all tabs.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {
            "session_id": str,
            "status": str,
            "message": str,
            "tab": {
                "index": int,
                "name": str,
                "current": bool
            }
        }
    """
    log_info = f"get_current_tab: session ID = {session_id}"
    logger.info(f"Getting current tab - {log_info}")

    status = "failure"
    message = None
    tab_info = None

    try:
        sync_tabs(session_id)

        tabs = get_tabs_for_session(session_id)
        index = get_current_tab_index(session_id)

        if tabs and index is not None and index < len(tabs):
            tab = tabs[index]

            tab_info = {
                "index": index,
                "name": tab["name"],
                "current": True
            }

            status = "success"
            message = "Current tab retrieved successfully"
        else:
            message = "No active tab found"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not get current tab"

    return {
        "session_id": session_id,
        "status": status,
        "message": message,
        "tab": tab_info
    }


@mcp.tool()
def switch_tab(session_id: str, index: int):
    """
    Switch to a specific browser tab using its index.

    Purpose
    -------
    Allows the agent to move between multiple open tabs in the same browser session.

    Always call `get_tabs` first to understand available tab indexes.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    index : int
        Index of the tab to switch to.

    Returns
    -------
    dict
        {
            "session_id": str,
            "status": str,
            "message": str
        }
    """
    log_info = f"switch_tab: session ID = {session_id}, index = {index}"
    logger.info(f"Switching tab - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)

        handle = get_valid_handle(session_id, index)

        if not handle:
            message = f"Invalid or stale tab index {index}"
        else:
            driver.switch_to.window(handle)
            current_tab_index[session_id] = index

            status = "success"
            message = f"Switched to tab {index}"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Tab switch failed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def open_new_tab(session_id: str, url: str = None):
    """
    Open a new browser tab and optionally navigate to a URL.

    Purpose
    -------
    Creates a new tab within the current browser session.
    The newly opened tab becomes the active tab.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    url : str, optional
        URL to open in the new tab. If not provided, a blank tab is opened.

    Returns
    -------
    dict
        {
            "session_id": str,
            "status": str,
            "message": str
        }
    """
    log_info = f"open_new_tab: session ID = {session_id}, url = {url}"
    logger.info(f"Opening new tab - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

        sync_tabs(session_id)

        tabs = get_tabs_for_session(session_id)
        current_tab_index[session_id] = len(tabs) - 1

        if url:
            driver.get(url)

        sync_tabs(session_id)

        status = "success"
        message = "New tab opened successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not open new tab"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def close_tab(session_id: str, index: int):
    """
    Close a specific browser tab using its index.

    Purpose
    -------
    Allows the agent to close tabs that are no longer needed.
    After closing, focus automatically shifts to a valid remaining tab.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    index : int
        Index of the tab to close.

    Returns
    -------
    dict
        {
            "session_id": str,
            "status": str,
            "message": str
        }
    """
    log_info = f"close_tab: session ID = {session_id}, index = {index}"
    logger.info(f"Closing tab - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)

        handle = get_valid_handle(session_id, index)

        if not handle:
            message = f"Invalid or stale tab index {index}"
        else:
            driver.switch_to.window(handle)
            driver.close()

            remove_tab_from_registry(session_id, handle)

            # SAFETY: switch to valid tab after close
            remaining = driver.window_handles
            if remaining:
                driver.switch_to.window(remaining[0])

            sync_tabs(session_id)

            # update index safely
            new_index = get_current_tab_index(session_id)
            current_tab_index[session_id] = new_index

            status = "success"
            message = f"Tab {index} closed successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Tab close failed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }


@mcp.tool()
def name_tab(session_id: str, index: int, name: str):
    """
    Assign a custom name to a browser tab.

    Purpose
    -------
    Helps the agent label tabs meaningfully for easier navigation across multiple tabs.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    index : int
        Index of the tab to name.
    name : str
        Custom name to assign to the tab.

    Returns
    -------
    dict
        {
            "session_id": str,
            "status": str,
            "message": str
        }
    """
    log_info = f"name_tab: session ID = {session_id}, index = {index}, name = {name}"
    logger.info(f"Naming tab - {log_info}")

    status = "failure"
    message = None

    try:
        sync_tabs(session_id)

        tabs = get_tabs_for_session(session_id)

        if not tabs or index >= len(tabs):
            message = f"Invalid tab index {index}"
        else:
            tabs[index]["name"] = name
            status = "success"
            message = f"Tab {index} named '{name}'"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Tab naming failed"

    return {
        "session_id": session_id,
        "status": status,
        "message": message
    }
