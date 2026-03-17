from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium_mcp.utils.logger import logger


def create_driver(browser="chrome", headless=False):

    log_info = f"create_driver: browser={browser}, headless={headless}"

    logger.info(
        f"Creating driver - {log_info}")

    try:
        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")

            return webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )

        if browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("-headless")

            return webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )

        if browser == "edge":
            options = EdgeOptions()
            if headless:
                options.add_argument("--headless=new")

            return webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=options
            )

        if browser == "safari":
            return webdriver.Safari()

    except Exception as e:

        logger.error(
            f"Error - {log_info}. Details - {e}")

    logger.error(
        f"Error - {log_info}. Details - {e}")

    raise ValueError(f"Unsupported browser: {browser}")
