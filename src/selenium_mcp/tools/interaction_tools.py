from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import *
from selenium_mcp.utils.logger import logger
from selenium_mcp.tools.element_tools import resolve_element
from selenium.webdriver.common.keys import Keys


from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException
)


@mcp.tool()
def click_element(session_id: str, index: int):
    """
    Click an interactive element on the current webpage using its index.

    Purpose
    -------
    This tool allows the agent to click buttons, links, or other interactive
    UI elements on the page. The element must first be discovered using
    `get_interactive_elements`, which returns a list of visible elements and
    assigns each one an index.

    The index returned by `get_interactive_elements` must be used with this
    tool to select the correct element.

    Recommended Agent Workflow
    --------------------------
    1. Navigate to the desired page using `open_url`.
    2. Wait for the page to load using `wait_for_page`.
    3. Call `get_interactive_elements` to discover clickable elements.
    4. Review the returned elements and identify the correct one.
    5. Call `click_element` using the element's index.
    6. If navigation occurs after clicking, call `wait_for_page` again.

    Parameters
    ----------
    session_id : str
        Active browser session identifier returned by `open_browser`.

    index : int
        Index of the element to click. This index must correspond to an
        element returned by `get_interactive_elements`.

    Returns
    -------
    dict
        {
            "session_id": str
            "index": index of the element that was clicked,
            "status": str
            "message": str
        }

    Error Conditions
    ----------------
    - If `get_interactive_elements` has not been called yet, the element
      cache will be empty and the tool will return an error.
    - If the provided index does not exist in the cached elements list,
      the tool will return an "Invalid element index" error.

    Notes
    -----
    The tool automatically scrolls the element into view before clicking
    to ensure it is visible and interactable. It uses a retry mechanism
    to handle stale element references and implements automatic fallback
    to JavaScript-based clicking if standard Selenium clicks are blocked.
    """

    log_info = f"click_element: session ID = {session_id}, index = {index}"
    logger.info(f"Clicking element - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        elements = element_cache.get(session_id)

        if not elements:
            return {
                "session_id": session_id,
                "index": -1,
                "status": "failure",
                "message": "No elements cached. Call get_interactive_elements first."
            }

        if index >= len(elements):
            return {
                "session_id": session_id,
                "index": -1,
                "status": "failure",
                "message": "Invalid element index"
            }

        element_dict = elements[index]

        # Retry loop (handles stale + timing issues)
        for attempt in range(2):
            try:
                element = resolve_element(driver, element_dict)

                # Scroll to center (better than top)
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    element
                )

                # Try normal click
                try:
                    element.click()
                except ElementClickInterceptedException:
                    # Fallback: JS click (bypasses overlays)
                    driver.execute_script("arguments[0].click();", element)

                status = "success"
                message = "Element clicked successfully"
                break

            except StaleElementReferenceException:
                # Re-resolve on stale element
                if attempt == 1:
                    raise
                continue

            except Exception:
                # Final fallback: force JS click
                try:
                    element = resolve_element(driver, element_dict)
                    driver.execute_script("arguments[0].click();", element)

                    status = "success"
                    message = "Element clicked successfully (JS fallback)"
                    break
                except Exception:
                    if attempt == 1:
                        raise

        if status != "success":
            message = f"Element at index {index} could not be clicked"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = f"Element at index {index} could not be clicked"

    return {
        "session_id": session_id,
        "index": index,
        "status": status,
        "message": message
    }


@mcp.tool()
def type_into_element(session_id: str, index: int, text: str):
    """
    Enter text into an input field or textarea using an element index.

    Purpose
    -------
    This tool allows the agent to type text into editable elements such as
    input fields or textareas. The element must first be discovered using
    `get_interactive_elements`, which returns a list of visible UI elements
    along with their corresponding indexes.

    The index returned by `get_interactive_elements` should be used directly
    with this tool to identify which element to type into.

    Recommended Agent Workflow
    --------------------------
    1. Call `get_interactive_elements` to retrieve all interactive elements.
    2. Identify the correct element by reviewing fields such as:
       - text
       - placeholder
       - aria_label
       - tag
    3. Use the provided `index` to call `type_into_element`.
    4. If the page changes after typing (e.g., search suggestions appear),
       consider calling `get_interactive_elements` again.

    Parameters
    ----------
    session_id : str
        Active browser session identifier returned by `open_browser`.

    index : int
        Index of the element to type into. This must correspond to the index
        returned by `get_interactive_elements`.

    text : str
        The text to be entered into the selected element.

    Returns
    -------
    dict
        {
            "session_id": str,
            "index": index of the element used,
            "text_to_type": the text to enter,
            "status": str,
            "message": str
        }

    Error Conditions
    ----------------
    If `get_interactive_elements` has not been called previously,
    the element cache may be empty and the tool will return an error.

    Notes
    -----
    This tool automatically clears any existing text in the element
    before entering the new text. It scrolls the element into view,
    ensures focus by clicking the element, and includes retry logic
    to handle stale element references and timing issues.
    """

    log_info = f"type_into_element: session ID = {session_id}, index = {index}, text = {text}"
    logger.info(f"Typing into element - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        elements = element_cache.get(session_id)

        if not elements:
            return {
                "session_id": session_id,
                "index": index,
                "text_to_type": text,
                "status": "failure",
                "message": "No elements cached"
            }

        if index >= len(elements):
            return {
                "session_id": session_id,
                "index": index,
                "text_to_type": text,
                "status": "failure",
                "message": "Invalid element index"
            }

        element_dict = elements[index]

        # 🔁 Try twice (handles stale / timing issues)
        for attempt in range(2):
            try:
                element = resolve_element(driver, element_dict)

                # 🔹 Scroll into view (centered)
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    element
                )

                # 🔹 Ensure focus (CRITICAL)
                try:
                    element.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", element)

                # 🔹 Safe clear
                try:
                    element.clear()
                except Exception:
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)

                # 🔹 Type
                element.send_keys(text)

                status = "success"
                message = "Text entered"
                break

            except Exception:
                # Retry once with fresh resolution
                if attempt == 1:
                    raise

        if status != "success":
            message = "Could not type into element"

    except Exception:
        logger.exception(f"Error - {log_info}")
        message = "Could not type into element"

    return {
        "session_id": session_id,
        "index": index,
        "text_to_type": text,
        "status": status,
        "message": message
    }
