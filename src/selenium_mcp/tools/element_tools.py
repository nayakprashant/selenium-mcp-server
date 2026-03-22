from selenium.webdriver.support.ui import WebDriverWait
from selenium_mcp.core.mcp_instance import mcp
from selenium_mcp.core.session_manager import *
from selenium.webdriver.common.by import By

from selenium_mcp.utils.logger import logger

INTERACTIVE_SELECTOR = "*"


@mcp.tool()
def get_interactive_elements(session_id: str):
    """
    Retrieve visible, top-level interactive elements with stable locators.
    Purpose
    -------
    This tool scans the current webpage for interactive elements (buttons, links, inputs, etc.) and returns a list of those that are visible and not obscured by others.
    Each element is assigned a unique index that can be used with `click_element` to interact with it. The tool prioritizes elements that are likely to be meaningful for user interaction, using heuristics based on HTML semantics and accessibility attributes.
    Parameters
    ----------
    session_id : str
        Active browser session identifier returned by `open_browser`.
    Returns
    -------
    dict
        {
            "session_id": str,
            "count": int,
            "elements": [
                {
                    "index": int,
                    "tag": str,
                    "label": str,
                    "role": str,
                    "context": str,
                    "xpath": str,
                    "css": str,
                    "bbox": {"x": int, "y": int, "width": int, "height": int}
                },
                ...
            ],
            "status": str,
            "message": str
        }
    Notes
    -----
    - The tool uses a combination of heuristics to identify interactive elements, including HTML tags, ARIA roles, and visual cues like cursor style and visibility.
    - Elements that are hidden, have zero size, or are obscured by other elements are filtered out to ensure that returned elements are actually interactable.
    - The returned `index` values are stable for the current page state and can be used with `click_element` to perform interactions.
    - The tool also handles elements within iframes by switching context and applying the same heuristics, ensuring a comprehensive capture of interactive elements across the entire page.
    """

    driver = get_driver(session_id)
    driver.switch_to.default_content()

    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    script = """
    function getXPath(el) {
        try {
            if (el.id) return `//*[@id="${el.id}"]`;

            const parts = [];
            while (el && el.nodeType === Node.ELEMENT_NODE) {
                let index = 1;
                let sibling = el.previousElementSibling;

                while (sibling) {
                    if (sibling.tagName === el.tagName) index++;
                    sibling = sibling.previousElementSibling;
                }

                parts.unshift(`${el.tagName.toLowerCase()}[${index}]`);
                el = el.parentElement;
            }

            return "/" + parts.join("/");
        } catch (e) {
            return null;
        }
    }

    function getCssSelector(el) {
        try {
            if (el.id) return `#${el.id}`;

            if (el.getAttribute("name")) {
                return `${el.tagName.toLowerCase()}[name="${el.getAttribute("name")}"]`;
            }

            if (el.getAttribute("aria-label")) {
                return `${el.tagName.toLowerCase()}[aria-label="${el.getAttribute("aria-label")}"]`;
            }

            return el.tagName.toLowerCase();
        } catch (e) {
            return null;
        }
    }

    function isInViewport(rect) {
        return (
            rect.bottom > 0 &&
            rect.right > 0 &&
            rect.top < window.innerHeight &&
            rect.left < window.innerWidth
        );
    }

    function isClickable(el) {
        const tag = el.tagName;
        const role = el.getAttribute('role');
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();

        if (
            rect.width === 0 ||
            rect.height === 0 ||
            !isInViewport(rect)
        ) return false;

        const isSemantic =
            tag === 'BUTTON' ||
            tag === 'A' ||
            tag === 'INPUT' ||
            tag === 'SELECT' ||
            tag === 'TEXTAREA' ||
            role === 'button' ||
            role === 'link' ||
            el.isContentEditable;

        const hasStrongHint =
            el.getAttribute('tabindex') !== null ||
            el.onclick !== null;

        const hasPointer = style.cursor === 'pointer';
        const hasText = (el.innerText || el.getAttribute('aria-label') || "").trim().length > 0;

        return isSemantic || hasStrongHint || (hasPointer && hasText);
    }

    function isTopMostClickable(el) {
        let parent = el.parentElement;

        while (parent) {
            if (isClickable(parent)) return false;
            parent = parent.parentElement;
        }

        return true;
    }

    function getLabel(el) {
        try {
            const tag = el.tagName;

            if (tag === 'INPUT' || tag === 'TEXTAREA') {
                return (
                    el.getAttribute('aria-label') ||
                    el.getAttribute('placeholder') ||
                    el.getAttribute('name') ||
                    el.getAttribute('value') ||
                    ''
                ).trim();
            }

            return (
                el.getAttribute('aria-label') ||
                (el.innerText || "").split("\\n")[0] ||
                el.getAttribute('placeholder') ||
                el.getAttribute('name') ||
                el.getAttribute('value') ||
                ''
            ).trim();
        } catch (e) {
            return "";
        }
    }

    function getContext(el) {
        try {
            let parent = el.parentElement;
            if (!parent) return "";

            return (
                parent.getAttribute('aria-label') ||
                parent.getAttribute('id') ||
                parent.getAttribute('class') ||
                parent.tagName
            ).slice(0, 100);
        } catch (e) {
            return "";
        }
    }

    function inferRole(el) {
        const tag = el.tagName.toLowerCase();
        const role = el.getAttribute('role');
        const type = el.getAttribute('type');

        if (tag === 'button') return 'button';
        if (tag === 'a') return 'link';

        if (tag === 'input') {
            if (type === 'text' || type === 'search') return 'textbox';
            if (type === 'checkbox' || type === 'radio') return 'option';
        }

        if (tag === 'select') return 'select';
        if (role) return role;

        return tag;
    }

    function collect(root) {
        const results = [];

        function traverse(node) {
            if (!node || node.nodeType !== 1) return;

            try {
                if (isClickable(node) && isTopMostClickable(node)) {
                    const label = getLabel(node);

                    if (label && label.length > 0) {
                        const rect = node.getBoundingClientRect();

                        results.push({
                            tag: node.tagName.toLowerCase(),
                            label: label,
                            role: inferRole(node),
                            context: getContext(node),

                            xpath: getXPath(node),
                            css: getCssSelector(node),

                            bbox: {
                                x: rect.x || 0,
                                y: rect.y || 0,
                                width: rect.width || 0,
                                height: rect.height || 0
                            }
                        });
                    }
                }

                if (node.shadowRoot) {
                    traverse(node.shadowRoot);
                }

                for (let child of node.children) {
                    traverse(child);
                }

            } catch (e) {}
        }

        traverse(root);
        return results;
    }

    return collect(document.body);
    """

    raw_elements = []

    try:
        raw_elements.extend(driver.execute_script(script))
    except Exception:
        pass

    # iframe handling
    try:
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe")

        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)

                WebDriverWait(driver, 3).until(
                    lambda d: d.execute_script(
                        "return document.readyState") == "complete"
                )

                raw_elements.extend(driver.execute_script(script))
                driver.switch_to.parent_frame()

            except Exception:
                driver.switch_to.parent_frame()
                continue

    except Exception:
        pass

    # Dedup
    unique = []
    seen = set()

    for el in raw_elements:
        try:
            key = (
                el.get("role"),
                el.get("label"),
                int(el.get("bbox", {}).get("x", 0)),
                int(el.get("bbox", {}).get("y", 0))
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(el)

        except Exception:
            continue

    # Index
    for i, el in enumerate(unique):
        el["index"] = i

    element_cache[session_id] = unique

    logger.info(
        f"""Found {len(unique)} interactive elements - session ID = {session_id}""")
    logger.debug(f"Interactive elements: {unique}")

    return {
        "status": "success",
        "count": len(unique),
        "elements": unique
    }


def resolve_element(driver, element_dict):
    """
    Resolve a cached element dictionary into a Selenium WebElement.

    Priority:
    1. xpath
    2. css
    3. fallback → fail fast
    """

    if not isinstance(element_dict, dict):
        raise Exception("Invalid element format. Expected dict.")

    try:
        if element_dict.get("xpath"):
            return driver.find_element(By.XPATH, element_dict["xpath"])

        if element_dict.get("css"):
            return driver.find_element(By.CSS_SELECTOR, element_dict["css"])

        raise Exception("No valid locator found in element")

    except Exception as e:
        raise Exception(f"Element resolution failed: {str(e)}")


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
