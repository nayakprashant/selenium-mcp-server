from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import *
from selenium.webdriver.common.by import By

from selenium_mcp.utils.logger import logger

INTERACTIVE_SELECTOR = "*"


@mcp.tool()
def get_interactive_elements(session_id: str):
    """
    Retrieve visible interactive elements from the current web page.

    Purpose
    -------
    This tool scans the page for interactive elements across modern web applications,
    including React, Angular, and dynamic UI frameworks. It detects elements based on
    behavior (clickability, roles, attributes) rather than only HTML tags.

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
        Active browser session identifier.

    Returns
    -------
    dict
        {
            "session_id": str,
            "count": int,
            "elements": [
                {
                    "index": int,
                    "role": str,
                    "label": str
                }
            ],
            "status": str,
            "message": str
        }
    """

    log_info = f"get_interactive_elements: session ID = {session_id}"
    logger.info(f"Getting interactive elements - {log_info}")

    status = "failure"
    message = None
    result = []

    try:
        driver = get_driver(session_id)

        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")

        filtered_elements = []

        for el in all_elements:
            try:
                if not el.is_displayed():
                    continue

                tag = el.tag_name

                text = (
                    el.text
                    or el.get_attribute("aria-label")
                    or el.get_attribute("placeholder")
                    or el.get_attribute("value")
                    or ""
                ).strip()

                role_attr = el.get_attribute("role")
                onclick = el.get_attribute("onclick")
                tabindex = el.get_attribute("tabindex")
                input_type = el.get_attribute("type")

                # Interaction heuristic (modern UI safe)
                is_interactive = (
                    tag in ["button", "a", "input", "select", "textarea"]
                    or role_attr in ["button", "link", "tab", "option"]
                    or onclick is not None
                    or tabindex is not None
                )

                if not is_interactive:
                    continue

                if not text:
                    continue

                filtered_elements.append(el)

            except Exception:
                continue

        # Deduplicate elements (avoid noisy UI)
        unique_elements = []
        seen = set()

        for el in filtered_elements:
            try:
                key = (
                    el.text.strip(),
                    el.tag_name
                )

                if key in seen:
                    continue

                seen.add(key)
                unique_elements.append(el)

            except Exception:
                continue

        # Cache elements
        element_cache[session_id] = unique_elements

        for i, el in enumerate(unique_elements):
            try:
                tag = el.tag_name
                role_attr = el.get_attribute("role")
                input_type = el.get_attribute("type")

                role = tag

                # Role normalization
                if tag == "input":
                    if input_type in ["text", "search"]:
                        role = "textbox"
                    elif input_type in ["radio", "checkbox"]:
                        role = "option"
                    else:
                        role = "input"

                elif tag == "a":
                    role = "link"

                elif role_attr == "button":
                    role = "button"

                elif role_attr == "link":
                    role = "link"

                elif role_attr == "option":
                    role = "option"

                label = (
                    el.text
                    or el.get_attribute("aria-label")
                    or el.get_attribute("placeholder")
                    or el.get_attribute("name")
                    or el.get_attribute("value")
                    or ""
                ).strip()

                result.append({
                    "index": i,
                    "role": role,
                    "label": label
                })

            except Exception:
                continue

        status = "success"
        message = "Interactive elements captured successfully"

    except Exception:
        logger.exception(f"Error - {log_info}")
        result = []
        message = "Could not capture interactive elements"

    return {
        "session_id": session_id,
        "count": len(result),
        "elements": result,
        "status": status,
        "message": message
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
        {
        "session_id": str,
        "count": int, 
        "nodes": [{"index": int, "role": str,
        "name": str, "tag": str, "id": str, "name_attr": str,
        "placeholder": str, "aria_label": str}],
        "status": str,
        "message": str
        }
    """
    log_info = f"get_accessibility_tree: session ID = {session_id}"
    logger.info(f"Getting accessibility tree -  {log_info}")

    status = "failure"
    message = None

    try:
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

        status = "success"
        message = "Accessibility tree captured successfully"

    except Exception:

        logger.exception(f"Error - {log_info}")
        message = "Could not capture accessibility tree"

    return {
        "session_id": session_id,
        "count": len(nodes),
        "nodes": nodes,
        "status": status,
        "message": message
    }
