from instance.mcp_instance import mcp
from core.session_manager import *
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger import logger


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
    logger.info(f"open_url: session ID = {session_id}, url = {url}")
    driver = get_driver(session_id)
    driver.get(url)
    return {"session_id": session_id, "message": f"Opened {url}"}


@mcp.tool()
def navigate_back(session_id: str):
    """
    Navigate back one step in browser history.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """

    logger.info(f"navigate_back: session ID = {session_id}")
    driver = get_driver(session_id)
    driver.back()
    return {"session_id": session_id, "message": "Navigated back to previous page"}


@mcp.tool()
def navigate_forward(session_id: str):
    """
    Navigate forward in browser history.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """

    logger.info(f"navigate_forward: session ID = {session_id}")
    driver = get_driver(session_id)
    driver.forward()
    return {"session_id": session_id, "message": "Navigated forward in browser history"}


@mcp.tool()
def refresh_page(session_id: str):
    """
    Reload the current web page.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """

    logger.info(f"refresh_page: session ID = {session_id}")
    driver = get_driver(session_id)
    driver.refresh()
    return {"session_id": session_id, "message": "Page refreshed"}


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
        {"status": "page_ready"} or {"status": "timeout", "message": str}
    """

    logger.info(
        f"wait_for_page: session ID = {session_id}, timeout = {timeout}")
    driver = get_driver(session_id)
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return {"status": "page_ready"}
    except TimeoutException:
        return {
            "status": "timeout",
            "message": f"Page did not load within {timeout} seconds",
        }
