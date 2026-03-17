from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import *
from selenium.webdriver.common.by import By
from selenium_mcp.utils.logger import logger


@mcp.tool()
def get_page_title(session_id: str):
    """
    Retrieve the title of the current web page.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {
        "session_id: str,
        "page_title": str (title of the page),
        "status": str,
        "message": str
        }
    """
    log_info = f"get_page_title: session ID = {session_id}"
    logger.info(f"Getting page title - {log_info}")

    status = "failure"
    message = None
    page_title = None

    try:
        driver = get_driver(session_id)
        page_title = driver.title
        status = "success"
        message = "Page title retrieved successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not retrieve the page title"

    return {
        "session_id": session_id,
        "page_title": page_title,
        "status": status,
        "message": message
    }


@mcp.tool()
def get_page_text(session_id: str, max_chars: int = 5000):
    """
    Retrieve visible text from the page body.

    Purpose
    -------
    Provides page text for reasoning, validation, or extraction.
    Text is truncated to `max_chars` characters; check the returned
    `truncated` flag to know whether content was cut.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    max_chars : int
        Maximum characters to return (default: 5000).

    Returns
    -------
    dict
        {
        "session_id": str, 
        "page_text": str (Page text extract),
        truncated": bool (True, if the page_text is truncated. Else, False), 
        "total_chars": int,
        "status": str,
        "message": str
        }
    """
    log_info = f"get_page_text: session ID = {session_id}, max characters = {max_chars}"
    logger.info(f"Getting page text - {log_info}")
    status = "failure"
    message = None
    full_text = None
    total = None
    truncated = None

    try:
        driver = get_driver(session_id)
        full_text = driver.find_element(By.TAG_NAME, "body").text
        total = len(full_text)
        truncated = total > max_chars

        status = "success"
        message = "Page text extracted successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not extract page text"

    return {
        "session_id": session_id,
        "page_text": full_text[:max_chars],
        "truncated": truncated,
        "total_characters": total,
        "status": status,
        "message": message
    }
