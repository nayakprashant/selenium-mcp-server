from selenium_mcp.utils.logger import logger

sessions = {}
element_cache = {}


def add_session(session_id, driver):
    logger.info(
        f"add_session: session ID = {session_id}, driver = {driver}")
    sessions[session_id] = driver


def get_driver(session_id):

    logger.info(f"get_driver: session ID = {session_id}")

    if session_id not in sessions:
        logger.error(
            f"get_driver: session ID = {session_id}")
        raise KeyError(f"No active session with id '{session_id}'")

    return sessions[session_id]


def remove_session(session_id):

    logger.info(f"remove_session: session ID = {session_id}")

    driver = sessions.get(session_id)
    if driver:
        driver.quit()
        del sessions[session_id]


def cache_elements(session_id, elements):
    logger.info(
        f"cache_elements: session ID = {session_id}, element = {elements}")
    element_cache[session_id] = elements


def get_cached_elements(session_id):

    logger.info(
        f"get_cached_elements: session ID = {session_id}")
    return element_cache.get(session_id)
