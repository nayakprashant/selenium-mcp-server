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
    str
        Page title.
    """

    logger.info(f"get_page_title: session ID = {session_id}")
    driver = get_driver(session_id)
    return driver.title


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
        {"text": str, "truncated": bool, "total_chars": int}
    """

    logger.info(
        f"get_page_text: session ID = {session_id}, max characters = {max_chars}")
    driver = get_driver(session_id)
    full_text = driver.find_element(By.TAG_NAME, "body").text
    total = len(full_text)
    truncated = total > max_chars
    return {
        "text": full_text[:max_chars],
        "truncated": truncated,
        "total_chars": total,
    }
