from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
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
    This tool scans the page for interactive elements using a performance-optimized
    selector that works across modern web applications (React, Angular, dynamic UIs).

    It identifies elements based on interaction signals such as:
        - semantic HTML tags (button, input, link)
        - ARIA roles (button, link, tab, option)
        - click handlers (onclick)
        - focusable elements (tabindex)

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
            "status": str,
            "count": int,
            "elements": [
                {
                    "index": int,
                    "role": str,
                    "label": str,
                    "tag": str,
                    "xpath": str or None,
                    "css": str or None,
                    "typeable": bool,
                    "bbox": {"x": int, "y": int, "width": int, "height": int}
                }
            ]
        }

    Notes
    -----
    - The returned `index` is required for all interaction tools.
    - Only visible and meaningful elements are returned to reduce noise.
    - This tool is optimized for speed and avoids scanning the entire DOM.
    - Elements within iframes are automatically discovered and included.
    - Duplicate elements are automatically filtered out.
    - Each element includes strong locators (xpath and/or css selector) for reliable resolution.
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

            if (el.getAttribute("name")) {
                return `//${el.tagName.toLowerCase()}[@name="${el.getAttribute("name")}"]`;
            }

            if (el.getAttribute("aria-label")) {
                return `//${el.tagName.toLowerCase()}[@aria-label="${el.getAttribute("aria-label")}"]`;
            }

            return null; // avoid brittle absolute xpath
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

            // Avoid weak selectors like "a", "div"
            return null;
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
            rect.width < 20 ||
            rect.height < 20 ||
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

    function isTypeable(el) {
        const tag = el.tagName;
        const type = el.getAttribute("type");

        return (
            tag === "INPUT" ||
            tag === "TEXTAREA" ||
            type === "text" ||
            type === "search"
        );
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

                        const xpath = getXPath(node);
                        const css = getCssSelector(node);

                        // Ensure at least one locator exists
                        if (!xpath && !css) return;

                        results.push({
                            tag: node.tagName.toLowerCase(),
                            label: label,
                            role: inferRole(node),
                            context: getContext(node),

                            xpath: xpath,
                            css: css,

                            typeable: isTypeable(node),

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

    # Deduplicate
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

    # Indexing
    for i, el in enumerate(unique):
        el["index"] = i

    element_cache[session_id] = unique
    logger.info(f"Found {len(unique)} interactive elements")
    logger.info(f"Interactive elements: {unique}")

    return {
        "status": "success",
        "count": len(unique),
        "elements": unique
    }


def compute_score(element, element_dict):
    """
    Compute semantic score between a DOM element and expected metadata.

    This scoring function is used by resolve_element to rank candidate elements
    and select the best match. Higher scores indicate better matches.

    Scoring Strategy
    ----------------
    The function evaluates multiple attributes in order of importance:
    1. Label matching (text content) - strongest signal
    2. HTML tag matching - medium signal
    3. Typeable property - indicates input/textarea
    4. ARIA role matching - helps validate element type

    Score Range: 0-15 points maximum

    Parameters
    ----------
    element : WebElement
        The live Selenium WebElement to evaluate.
    element_dict : dict
        Expected element metadata containing: label, tag, role, typeable.

    Returns
    -------
    int
        Cumulative score (0-15). Higher = better match.
    """

    score = 0

    # Extract expected metadata from the cached element dictionary
    label = (element_dict.get("label") or "").strip().lower()
    tag = element_dict.get("tag")
    role = element_dict.get("role")
    typeable = element_dict.get("typeable")

    # Extract actual text content from the live DOM element
    try:
        text = (element.text or "").strip().lower()
    except Exception:
        text = ""

    # -------------------------
    # Label match (strongest signal) - up to 6 points
    # -------------------------
    # The element's visible text is the most reliable indicator of correctness
    # Exact match (6 points): "Sign In" == "Sign In"
    # Partial match (4 points): "Sign In" in "Click to Sign In"
    if label:
        if text == label:
            score += 6  # Exact match - highest confidence
        elif label in text:
            score += 4  # Partial match - element contains expected text

    # -------------------------
    # Tag match - up to 2 points
    # -------------------------
    # Verifies the HTML tag type matches expectations
    # Useful for distinguishing between <button> vs <div role="button">
    if tag and element.tag_name.lower() == tag:
        score += 2

    # -------------------------
    # Typeable boost - up to 5 points
    # -------------------------
    # Strong signal for input/textarea elements
    # If metadata indicates element is typeable (INPUT or TEXTAREA),
    # and the actual element is also an input field, boost the score
    if typeable and element.tag_name.lower() in ["input", "textarea"]:
        score += 5

    # -------------------------
    # Role hints - up to 2 points each
    # -------------------------
    # Semantic ARIA roles help validate element type
    # Buttons can be <button> or <span role="button">
    if role == "button" and element.tag_name.lower() in ["button", "span"]:
        score += 2

    # Links are typically <a> tags
    if role == "link" and element.tag_name.lower() == "a":
        score += 2

    return score


def compute_spatial_score(element, element_dict):
    """
    Compute spatial proximity score based on element position.

    This scoring function helps resolve elements when multiple candidates match
    semantically. It compares the current element position with the expected
    position (stored in the cached element's bounding box) to determine which
    candidate is most likely the correct one.

    Use Case
    --------
    After page navigation or DOM updates, elements may shift position. This scorer
    helps identify the correct element even if its position has changed slightly.
    It's particularly useful for:
    - Dynamic pages with shifting layouts
    - Reused element metadata across navigation
    - Disambiguating similar elements on the same page

    Distance Calculation
    --------------------
    Uses Manhattan distance (sum of absolute differences in x and y coordinates):
        distance = |actual_x - expected_x| + |actual_y - expected_y|

    Scoring Tiers (0-3 points)
    --------------------------
    - 3 points: distance < 50 pixels (very close match - high confidence)
    - 2 points: distance < 150 pixels (moderate distance - good match)
    - 1 point: distance < 300 pixels (significant distance - weak match)
    - 0 points: distance >= 300 or exception occurs (no credit)

    Parameters
    ----------
    element : WebElement
        The live Selenium WebElement with position information.
    element_dict : dict
        Expected element metadata containing bounding box (bbox) with x, y coords.

    Returns
    -------
    int
        Spatial proximity score (0-3 points). Higher = closer to expected position.
    """

    try:
        # Extract actual element position from the live DOM element
        rect = element.rect
        ex = rect.get("x", 0)  # actual x coordinate
        ey = rect.get("y", 0)  # actual y coordinate

        # Extract expected position from the cached element metadata
        # This bbox was captured when get_interactive_elements was called
        target = element_dict.get("bbox", {})
        tx = target.get("x", 0)  # target/expected x coordinate
        ty = target.get("y", 0)  # target/expected y coordinate

        # Calculate Manhattan distance (sum of absolute x and y differences)
        # This works better than Euclidean distance for UI elements
        distance = abs(ex - tx) + abs(ey - ty)

        # Score based on distance thresholds
        # Closer elements are given higher scores to preference spatial proximity
        if distance < 50:
            return 3  # Very close match - element position nearly identical
        elif distance < 150:
            return 2  # Moderate distance - element likely shifted slightly
        elif distance < 300:
            return 1  # Significant distance - but still plausibly same element

    except Exception:
        # If position data is unavailable, return 0 (no spatial score)
        pass

    return 0  # No spatial match, or error retrieving position data


def resolve_element(driver, element_dict):
    """
    Resolve a cached element to its current DOM reference with multi-strategy fallback.

    Purpose
    -------
    This is the core element resolution engine. Given cached element metadata
    (from a previous get_interactive_elements call), it finds the corresponding
    element in the current DOM. This handles:
    - Elements that persist through page navigation
    - DOM updates and re-renders (React, Angular, etc.)
    - Stale element references after AJAX updates
    - Multiple similar elements on the page

    Multi-Strategy Approach
    -----------------------
    The resolver uses a cascading strategy that tries multiple localization
    methods in order of specificity/reliability:

    1. Primary Locators (strongest):
       - XPath from cached metadata (e.g., //*[@id="submit"])
       - CSS selector from cached metadata (e.g., #submit)
       These are most reliable because they captured specific identifiers

    2. Typeable Shortcut (for inputs):
       - If cached metadata indicates element is typeable (input/textarea),
         prioritize "//input[not(@type='hidden')] | //textarea" selector
       - This avoids false matches on non-input elements

    3. Label-Based Fallback:
       - Exact normalized text match: //{tag}[normalize-space()='{label}']
       - Partial text match: //{tag}[contains(normalize-space(), '{label[:20]}')]
       - Falls back to cached label when identifiers are unavailable

    4. Role-Based Fallback (least specific):
       - For buttons: "//button | //*[@role='button'] | //span"
       - For links: "//a"
       - Very broad, only used after specific strategies fail

    Candidate Selection & Scoring
    ----------------------------
    Once all candidate elements are collected:
    1. Each candidate is scored using compute_score() and compute_spatial_score()
    2. Semantic score (0-15): measures text/tag/role match
    3. Spatial score (0-3): measures position proximity to cached coordinates
    4. Total score (0-18): combined semantic + spatial score
    5. Best element = highest total score

    Error Handling
    --------------
    - Validates input is a dict
    - Gracefully handles strategy failures (continues to next strategy)
    - Raises exception if no candidates found at all
    - Raises exception if best element is None after scoring

    Parameters
    ----------
    driver : WebDriver
        Active Selenium WebDriver instance.
    element_dict : dict
        Cached element metadata from get_interactive_elements containing:
        - label: visible text label
        - tag: HTML tag name
        - role: semantic ARIA role
        - xpath: strong locator (may be None)
        - css: strong locator (may be None)
        - typeable: bool indicating if element accepts text input
        - bbox: {"x": int, "y": int} expected position

    Returns
    -------
    WebElement
        The resolved Selenium WebElement from the current DOM.

    Raises
    ------
    Exception
        If element cannot be found or resolved after all strategies exhausted.

    Confidence Notes
    ----------------
    Internal confidence is calculated but not returned. Scoring > 15 indicates
    high confidence (semantic + spatial match). Scores 5-15 indicate moderate
    confidence. Scores < 5 indicate weak matches (fallback strategy only).
    """

    # Validate input format
    if not isinstance(element_dict, dict):
        raise Exception("Invalid element format")

    strategies = []

    # =========================================================================
    # STRATEGY 1: Primary Locators (strongest - specific identifiers)
    # =========================================================================
    # These locators were generated by get_interactive_elements from stable
    # attributes like id, name, or aria-label. They're the most reliable.
    if element_dict.get("xpath"):
        strategies.append(("xpath", element_dict["xpath"]))

    if element_dict.get("css"):
        strategies.append(("css", element_dict["css"]))

    # =========================================================================
    # STRATEGY 2: Typeable Shortcut (for input/textarea elements)
    # =========================================================================
    # If the cached metadata indicates this is a typeable element (input/textarea),
    # inject a more specific strategy at the beginning to avoid matching
    # non-input elements before we find the actual input.
    if element_dict.get("typeable"):
        strategies.insert(
            0, ("xpath", "//input[not(@type='hidden')] | //textarea"))

    # =========================================================================
    # STRATEGY 3: Label-Based Fallback (moderate specificity)
    # =========================================================================
    # When primary locators fail (e.g., id was removed by JS framework),
    # fall back to matching by visible text label. This works well for
    # buttons, links, and other text-bearing elements.
    label = element_dict.get("label")
    tag = element_dict.get("tag")

    if label:
        # Exact match: element's normalized text equals expected label
        # E.g., <button>Sign In</button> with label="Sign In"
        strategies.append((
            "xpath",
            f"//{tag}[normalize-space()='{label}']"
        ))

        # Partial match: element's normalized text contains first 20 chars of label
        # More forgiving for long labels like "Click here to Sign In"
        strategies.append((
            "xpath",
            f"//{tag}[contains(normalize-space(), '{label[:20]}')]"
        ))

    # =========================================================================
    # STRATEGY 4: Role-Based Fallback (least specific - type matching only)
    # =========================================================================
    # As a last resort, match by semantic role. Very broad (matches many elements),
    # but combined with scoring, we can still identify the correct one.
    role = element_dict.get("role")

    if role == "button":
        # Matches <button>, <div role="button">, even generic <span> with button behavior
        strategies.append(("xpath", "//button | //*[@role='button'] | //span"))

    if role == "link":
        # Matches standard <a> tags
        strategies.append(("xpath", "//a"))

    # =========================================================================
    # STEP 5: Collect All Candidates
    # =========================================================================
    # Try each strategy in order and collect all matching elements.
    # We gather candidates from all strategies so scoring can select the best.
    candidates = []

    for strategy_type, value in strategies:
        try:
            if strategy_type == "xpath":
                found = driver.find_elements(By.XPATH, value)
            else:
                found = driver.find_elements(By.CSS_SELECTOR, value)

            candidates.extend(found)

        except Exception:
            # Strategy failed (invalid XPath, CSS error, etc.)
            # Continue to next strategy instead of raising
            continue

    if not candidates:
        raise Exception("No candidates found for element")

    # =========================================================================
    # STEP 6: Score and Rank Candidates
    # =========================================================================
    # Multiple candidates may match a strategy (e.g., multiple buttons on page).
    # Score each candidate using semantic and spatial metrics to find the best.
    best_element = None
    best_score = -1

    for el in candidates:
        # Semantic score (0-15): text match, tag match, role match
        semantic_score = compute_score(el, element_dict)

        # Spatial score (0-3): position proximity to cached coordinates
        spatial_score = compute_spatial_score(el, element_dict)

        # Total score combines both signals
        total_score = semantic_score + spatial_score

        # Track the candidate with highest combined score
        if total_score > best_score:
            best_score = total_score
            best_element = el

    # =========================================================================
    # STEP 7: Confidence Calculation (internal reference)
    # =========================================================================
    # Score range interpretation:
    # - 15+ = excellent match (exact semantic + spatial match)
    # - 5-14 = good match (primary strategy found element)
    # - 0-4 = fallback match (had to use broad strategies)
    confidence = min(1.0, best_score / 10)

    # Optional: uncomment for debugging resolution quality
    # logger.info(f"Resolver confidence: {confidence}, score: {best_score}")

    if best_element:
        return best_element

    # No element matched or scoring failed entirely
    raise Exception(
        f"Element resolution failed. Label={label}, Tag={tag}"
    )


@mcp.tool()
def get_accessibility_tree(session_id: str):
    """
    Retrieve a simplified accessibility tree of the current page.

    Purpose
    -------
    Returns interactive and semantic elements with standardized accessibility roles
    so AI agents can understand the page structure and meaning. This tool provides
    a semantic view of the page with role inference, helping agents reason about
    the page layout without needing to understand HTML structure directly.

    Compared to get_interactive_elements:
    - get_interactive_elements: Returns indexed, clickable/interactable elements with
      strong locators (xpath/css selectors) for direct interaction
    - get_accessibility_tree: Returns all accessible elements with semantic roles
      for understanding page structure and content organization

    Use Cases
    ---------
    - Understanding the semantic structure of a page
    - Identifying form fields, buttons, and navigation elements by role
    - Creating accessible automation that respects page semantics
    - Debugging accessibility issues (missing ARIA roles, labels)
    - Mapping page hierarchy for complex multi-step workflows

    Element Discovery
    ------------------
    The accessibility tree indexes all DOM elements and returns:
    - Semantic role (button, link, textbox, combobox, generic, etc.)
    - Human-readable name (from text, alt, aria-label, or placeholder)
    - Element identification (id, name, placeholder, aria-label)
    - Element type (HTML tag name)

    Role Inference Rules
    --------------------
    Roles are automatically inferred from element type and attributes:
    - <button> → "button"
    - <a> → "link"
    - <textarea> → "textbox"
    - <input type="text|email|password"> → "textbox"
    - <input type="search"> → "searchbox"
    - <input type="submit"> → "button"
    - <select> → "combobox"
    - Other elements → "generic"

    Visibility Filtering
    --------------------
    Only visible elements are included. Elements are considered visible if:
    - CSS display != "none"
    - CSS visibility != "hidden"
    - Element has offsetParent (rendered in layout)

    Recommended Agent Workflow
    --------------------------
    1. Navigate to a webpage using `open_url`.
    2. Wait for the page to fully load using `wait_for_page`.
    3. Call `get_accessibility_tree` to understand page structure.
    4. Review the returned nodes to identify page sections and available actions.
    5. Use `get_interactive_elements` to find specific interactive elements to click/type.
    6. Use element index from `get_interactive_elements` with interaction tools.

    Parameters
    ----------
    session_id : str
        Active browser session identifier.

    Returns
    -------
    dict
        {
            "session_id": str,
            "count": int (total number of nodes),
            "nodes": [
                {
                    "index": int (position in the tree, starting at 0),
                    "role": str (semantic role: button, link, textbox, etc.),
                    "name": str (human-readable label or text content),
                    "tag": str (HTML tag name in lowercase),
                    "id": str (HTML id attribute, or empty string),
                    "name_attr": str (HTML name attribute, or empty string),
                    "placeholder": str (HTML placeholder attribute, or empty string),
                    "aria_label": str (ARIA label attribute, or empty string)
                }
            ],
            "status": str ("success" or "failure"),
            "message": str (status message describing result or error)
        }

    Error Conditions
    ----------------
    - If the page has not fully loaded, elements may be missing or incomplete.
    - If JavaScript execution is blocked, the tree will be empty.
    - If all elements are hidden/invisible, the tree may have zero or few nodes.
    - Errors during execution return status="failure" with error message.

    Notes
    -----
    - Each node includes an "index" field that serves as a reference number.
    - The "name" field is populated from the first available source:
      text content > alt attribute > aria-label > placeholder > id > generic label
    - Elements without an HTML id attribute will have an empty "id" field.
    - This tool scans the entire page including nested elements (not just top-level).
    - Shadow DOM elements are not included (limitation of current implementation).
    - The accessibility tree is useful for agents to understand structure and plan interactions.
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
