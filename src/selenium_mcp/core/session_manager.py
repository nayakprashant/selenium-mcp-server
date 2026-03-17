from selenium_mcp.utils.logger import logger

sessions = {}
element_cache = {}
tab_registry = {}
current_tab_index = {}


def sync_tabs(session_id):

    log_info = f"sync_tabs: session ID = {session_id}"

    logger.info(f"Syncing tabs - {log_info}")

    try:
        driver = get_driver(session_id)
        current_handles = driver.window_handles
        current_handle = driver.current_window_handle

        if session_id not in tab_registry:
            tab_registry[session_id] = []

        # STEP 1: Remove stale tabs
        existing_tabs = tab_registry.get(session_id, [])
        cleaned_tabs = [
            t for t in existing_tabs if t["handle"] in current_handles
        ]

        if len(cleaned_tabs) != len(existing_tabs):
            logger.info(f"Stale tabs removed - {log_info}")

        tab_registry[session_id] = cleaned_tabs

        # STEP 2: Add new tabs
        existing_handles = {t["handle"] for t in cleaned_tabs}

        for handle in current_handles:
            if handle not in existing_handles:
                tab_registry[session_id].append({
                    "handle": handle,
                    "name": f"tab_{len(tab_registry[session_id])}"
                })

        # STEP 3: Update active tab index
        tabs = tab_registry.get(session_id, [])

        for i, tab in enumerate(tabs):
            if tab["handle"] == current_handle:
                current_tab_index[session_id] = i
                break

    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")


def get_current_tab_index(session_id):

    log_info = f"get_current_tab_index: session ID = {session_id}"

    logger.info(f"Getting current tab index - {log_info}")

    try:
        return current_tab_index.get(session_id)
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")
        return None


def get_tabs_for_session(session_id):

    log_info = f"get_tabs_for_session: session ID = {session_id}"

    logger.info(f"Getting tabs - {log_info}")

    try:
        return tab_registry.get(session_id, [])
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")
        return []


def remove_tab_from_registry(session_id, handle):

    log_info = f"remove_tab_from_registry: session ID = {session_id}, handle = {handle}"

    logger.info(f"Removing tab from registry - {log_info}")

    try:
        tabs = tab_registry.get(session_id, [])
        tab_registry[session_id] = [
            t for t in tabs if t["handle"] != handle
        ]
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")


def get_tabs_for_session(session_id):

    log_info = f"get_tabs_for_session: session ID = {session_id}"

    logger.info(f"Getting tabs - {log_info}")

    try:
        return tab_registry.get(session_id, [])
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")
        return []


def remove_tab_from_registry(session_id, handle):

    log_info = f"remove_tab_from_registry: session ID = {session_id}, handle = {handle}"

    logger.info(f"Removing tab from registry - {log_info}")

    try:
        tabs = tab_registry.get(session_id, [])
        tab_registry[session_id] = [
            t for t in tabs if t["handle"] != handle
        ]
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")


def get_valid_handle(session_id, index):

    log_info = f"get_valid_handle: session ID = {session_id}, index = {index}"

    logger.info(f"Validating tab handle - {log_info}")

    try:
        driver = get_driver(session_id)

        sync_tabs(session_id)
        tabs = tab_registry.get(session_id, [])

        if not tabs or index >= len(tabs):
            return None

        handle = tabs[index]["handle"]

        if handle not in driver.window_handles:
            logger.info(f"Handle missing, re-syncing - {log_info}")

            sync_tabs(session_id)
            tabs = tab_registry.get(session_id, [])

            if not tabs or index >= len(tabs):
                return None

            handle = tabs[index]["handle"]

        # Update active index (important)
        current_tab_index[session_id] = index

        return handle

    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")
        return None


def add_session(session_id, driver):

    log_info = f"add_session: session ID = {session_id}, driver = {driver}"

    logger.info(
        f"Adding session - {log_info}")
    try:
        sessions[session_id] = driver
    except Exception as e:
        logger.error(f"Error - {log_info}. Error: {e}")


def get_driver(session_id):

    log_info = f"get_driver: session ID = {session_id}"

    logger.info(f"Getting driver - {log_info}")
    if session_id not in sessions:
        logger.error(
            f"Error - {log_info}. Details - No active session")
        raise KeyError(f"Error - {log_info}. Details - No active session")

    return sessions[session_id]


def remove_session(session_id):

    log_info = f"emove_session: session ID = {session_id}"

    logger.info(f"Removing session - {log_info}")

    try:
        driver = sessions.get(session_id)
        if driver:
            driver.quit()
            del sessions[session_id]
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")


def cache_elements(session_id, elements):

    log_info = f"cache_elements: session ID = {session_id}, element = {elements}"

    logger.info(
        f"Caching elements - {log_info}")

    try:
        element_cache[session_id] = elements
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")


def get_cached_elements(session_id):

    log_info = f"get_cached_elements: session ID = {session_id}"

    logger.info(f"Getting cached elements - {log_info}")

    try:
        return element_cache.get(session_id)
    except Exception as e:
        logger.error(f"Error - {log_info}. Details - {e}")
