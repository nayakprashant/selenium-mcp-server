from selenium_mcp.utils.logger import logger

sessions = {}
element_cache = {}


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
