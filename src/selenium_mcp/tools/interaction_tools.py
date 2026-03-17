from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import *
from selenium_mcp.utils.logger import logger


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
    to ensure it is visible and interactable.
    """
    log_info = f"click_element: session ID = {session_id}, index = {index}"
    logger.info(f"Clicking element - {log_info}")

    status = "success"
    message = None

    try:

        driver = get_driver(session_id)
        elements = element_cache.get(session_id)

        if not elements:
            status = "failure"
            message = "No elements cached. Call get_interactive_elements first."
            return {
                "session_id": session_id,
                "index": -1,
                "status": status,
                "message": message
            }

        if index >= len(elements):
            status = "failure"
            message = "Invalid element index"
            return {
                "session_id": session_id,
                "index": -1,
                "status": status,
                "message": message
            }

        element = elements[index]
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()

        status = "success"
        message = "Element clicked successfully"

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
    before entering the new text.
    """
    log_info = f"type_into_element: session ID = {session_id}, index = {index}, text = {text}"
    logger.info(f"Typing into element - {log_info}")

    status = "failure"
    message = None

    try:
        driver = get_driver(session_id)
        elements = element_cache.get(session_id)

        if not elements:
            message = "No elements cached"
        else:
            element = elements[index]
            element.clear()
            element.send_keys(text)

            status = "success"
            message = "Text entered"

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
