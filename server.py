from mcp.server.fastmcp import FastMCP

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import uuid
import os
import atexit
import tempfile

mcp = FastMCP("selenium-browser")
SCREENSHOT_DIR = os.getenv("MCP_SCREENSHOT_DIR")

# -----------------------------
# Internal Session Store
# -----------------------------

sessions = {}
element_cache = {}

# Shared CSS selector used across all element tools — must be consistent
# so that indices returned by discovery tools match interaction tools.
INTERACTIVE_SELECTOR = "button, a, input, textarea, select"
INPUT_SELECTOR = "input, textarea"

# Directory where screenshots are saved. Defaults to the system temp dir
# so paths are always absolute and accessible.
# SCREENSHOT_DIR = os.environ.get("MCP_SCREENSHOT_DIR", tempfile.gettempdir())


def _cleanup_all_sessions():
    """Quit all open browser sessions on process exit to avoid zombie Chrome processes."""
    for driver in list(sessions.values()):
        try:
            driver.quit()
        except Exception:
            pass
    sessions.clear()


atexit.register(_cleanup_all_sessions)


def create_driver(browser: str = "chrome", headless: bool = False):
    """
    Create and return a Selenium WebDriver instance.

    Parameters
    ----------
    browser : str
        Browser type to launch. Currently only "chrome" is supported.
    headless : bool
        If True, runs Chrome without a visible window. Required on
        headless servers (Docker, CI, cloud VMs).

    Returns
    -------
    WebDriver
    """
    if browser == "chrome":
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )
    else:
        raise ValueError(
            f"Unsupported browser: '{browser}'. Supported: chrome")

    return driver


def get_driver(session_id: str):
    """
    Retrieve the WebDriver associated with a session_id.

    Raises
    ------
    KeyError
        If the session_id is not found.
    """
    if session_id not in sessions:
        raise KeyError(f"No active session with id '{session_id}'")
    return sessions[session_id]


def get_by(by: str):
    """
    Convert a locator strategy string to a Selenium By constant.

    Raises
    ------
    ValueError
        If the strategy is not recognised.
    """
    mapping = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
    }
    result = mapping.get(by.lower())
    if result is None:
        raise ValueError(
            f"Unknown locator strategy '{by}'. Valid options: {list(mapping)}"
        )
    return result


# -----------------------------
# MCP Tools
# -----------------------------


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
        {"session_id": str, "browser": str, "headless": bool}
    """
    driver = create_driver(browser, headless)
    session_id = str(uuid.uuid4())
    sessions[session_id] = driver

    return {"session_id": session_id, "browser": browser, "headless": headless}


@mcp.tool()
def maximize_browser(session_id: str):
    """
    Maximize the browser window.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    driver = get_driver(session_id)
    driver.maximize_window()
    return {"session_id": session_id, "message": "Browser window maximized"}


@mcp.tool()
def fullscreen_browser(session_id: str):
    """
    Switch the browser to fullscreen mode.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    driver = get_driver(session_id)
    driver.fullscreen_window()
    return {"session_id": session_id, "message": "Browser switched to fullscreen mode"}


@mcp.tool()
def navigate_back(session_id: str):
    """
    Navigate back one step in browser history.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
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
    driver = get_driver(session_id)
    driver.refresh()
    return {"session_id": session_id, "message": "Page refreshed"}


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
    driver = get_driver(session_id)
    driver.get(url)
    return {"session_id": session_id, "message": f"Opened {url}"}


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
    driver = get_driver(session_id)
    return driver.title


@mcp.tool()
def close_browser(session_id: str):
    """
    Close the browser session and free its resources.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.
    """
    driver = get_driver(session_id)
    driver.quit()
    del sessions[session_id]
    return {"message": "Browser closed", "session_id": session_id}


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
            "status": "clicked",
            "index": index of the element that was clicked
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
    driver = get_driver(session_id)
    elements = element_cache.get(session_id)

    if not elements:
        return {"status": "error", "message": "No elements cached. Call get_interactive_elements first."}

    if index >= len(elements):
        return {"status": "error", "message": "Invalid element index"}

    element = elements[index]

    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    element.click()

    return {
        "status": "clicked",
        "index": index
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
        {"text": str, "truncated": bool, "total_chars": int}
    """
    driver = get_driver(session_id)
    full_text = driver.find_element(By.TAG_NAME, "body").text
    total = len(full_text)
    truncated = total > max_chars
    return {
        "text": full_text[:max_chars],
        "truncated": truncated,
        "total_chars": total,
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
            "status": "text_entered",
            "index": index of the element used,
            "text": the text that was entered
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
    driver = get_driver(session_id)
    elements = element_cache.get(session_id)

    if not elements:
        return {"status": "error", "message": "No elements cached"}

    element = elements[index]

    element.clear()
    element.send_keys(text)
    return {"status": "text_entered", "index": index, "text": text}


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


@mcp.tool()
def take_screenshot(session_id: str):
    """
    Capture a screenshot of the current browser window.

    Purpose
    -------
    Useful for debugging, failure reporting, or visual analysis.
    Screenshots are saved to the directory set by the
    MCP_SCREENSHOT_DIR environment variable (default: system temp dir).

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {"status": "success", "path": str}  — absolute file path
    """
    driver = get_driver(session_id)
    filename = f"screenshot_{session_id}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(path)
    return {"status": "success", "path": path}


if __name__ == "__main__":
    mcp.run()
