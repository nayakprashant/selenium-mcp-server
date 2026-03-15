from core.mcp_instance import mcp
from core.session_manager import *
from selenium.webdriver.common.by import By

from utils.logger import logger

INTERACTIVE_SELECTOR = "button, a, input, textarea, select"


@mcp.tool()
def get_interactive_elements(session_id: str):
    """
    Retrieve visible interactive elements from the current web page.

    Purpose
    -------
    This tool scans the page for commonly interactive HTML elements such as:
        - buttons
        - links
        - input fields
        - textareas
        - dropdowns

    The discovered elements are returned with an assigned `index`. This index
    must be used when interacting with elements using tools such as:
        - click_element
        - type_into_element

    The function also stores the discovered Selenium elements in an internal
    session cache so that subsequent tools can safely interact with the exact
    same elements without re-querying the DOM.

    Recommended Agent Workflow
    --------------------------
    1. Navigate to a webpage using `open_url`.
    2. Wait for the page to fully load using `wait_for_page`.
    3. Call `get_interactive_elements` to discover UI elements.
    4. Review the returned list of elements and identify the correct element.
    5. Use the provided `index` with tools like:
        - `click_element(index)`
        - `type_into_element(index, text)`

    Parameters
    ----------
    session_id : str
        Active browser session identifier returned by `open_browser`.

    Returns
    -------
    dict
        {
            "count": number_of_interactive_elements_found,
            "elements": [
                {
                    "index": int,
                    "role": str,
                    "label": str
                }
            ]
        }

    Notes
    -----
    - The returned `index` is required for all element interaction tools.
    - Always call this tool before attempting to click, read, or type into elements.
    - The elements are cached internally for the current session so that
      subsequent actions operate on the same DOM elements.
    """
    logger.info(f"get_interactive_elements: session ID = {session_id}")
    driver = get_driver(session_id)

    '''
    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "button, a, input, textarea, select"
    )
    '''
    elements = [
        el for el in driver.find_elements(
            By.CSS_SELECTOR,
            "button, a, input, textarea, select"
        )
        if el.is_displayed()
    ]
    element_cache[session_id] = elements

    result = []

    for i, el in enumerate(elements):
        '''
        text= el.text or el.get_attribute(
            "value") or el.get_attribute("placeholder") or ""
        '''
        role = el.tag_name

        if role == "input":
            role = "textbox"

        if role == "a":
            role = "link"

        label = (
            el.text
            or el.get_attribute("aria-label")
            or el.get_attribute("placeholder")
            or el.get_attribute("name")
            or el.get_attribute("value")
            or ""
        )
        result.append({
            "index": i,
            "role": role,
            "label": label
        })

    return {
        "count": len(result),
        "elements": result
    }


@mcp.tool()
def get_accessibility_tree(session_id: str):
    """
    Retrieve a simplified accessibility tree of the current page.

    Purpose
    -------
    Returns interactive elements with semantic roles so AI agents
    can understand UI meaning (buttons, links, inputs, dropdowns).
    Returned `index` values map directly to `click_element`.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {"count": int, "nodes": [{"index": int, "role": str,
        "name": str, "tag": str, "id": str, "name_attr": str,
        "placeholder": str, "aria_label": str}]}
    """

    logger.info(f"get_accessibility_tree: session ID = {session_id}")
    driver = get_driver(session_id)

    nodes = driver.execute_script(
        f"""
    function getRole(el) {{
        const tag = el.tagName.toLowerCase();
        if (tag === "button") return "button";
        if (tag === "a") return "link";
        if (tag === "textarea") return "textbox";
        if (tag === "input") {{
            if (["text","email","password"].includes(el.type)) return "textbox";
            if (el.type === "search") return "searchbox";
            if (el.type === "submit") return "button";
        }}
        if (tag === "select") return "combobox";
        return "generic";
    }}

    const nodes = [];
    document.querySelectorAll("{INTERACTIVE_SELECTOR}").forEach(el => {{
        const style = window.getComputedStyle(el);
        const visible =
            style.display !== "none" &&
            style.visibility !== "hidden" &&
            el.offsetParent !== null;

        if (!visible) return;

        nodes.push({{
            role: getRole(el),
            name: el.innerText || el.value || el.placeholder || el.getAttribute("aria-label") || "",
            id: el.id || "",
            name_attr: el.name || "",
            placeholder: el.placeholder || "",
            aria_label: el.getAttribute("aria-label") || "",
            tag: el.tagName.toLowerCase()
        }});
    }});

    return nodes;
    """
    )

    for i, node in enumerate(nodes):
        node["index"] = i

    return {"count": len(nodes), "nodes": nodes}
