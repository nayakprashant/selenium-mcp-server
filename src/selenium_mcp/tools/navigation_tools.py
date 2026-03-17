from selenium_mcp.core.mcp_instance import mcp
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
