from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager as FireFoxDriverManager


class Session:
    """A top level class to manage a browser containing one/more Tabs"""

    BROWSER_DRIVER_FUNCTION = {
        "Chrome": webdriver.Chrome,
        "FireFox": webdriver.Firefox,
    }

    BROWSER_DRIVER_SERVICE_FUNCTION = {
        "Chrome": ChromeService,
        "FireFox": FirefoxService,
    }

    BROWSER_DRIVER_MANAGER_FUNCTION = {
        "Chrome": ChromeDriverManager,
        "FireFox": FireFoxDriverManager,
    }

    BROWSER_OPTION_FUNCTION = {"Chrome": ChromeOptions, "FireFox": FirefoxOptions}

    def __init__(
        self,
        browser_name,
        implicit_wait,
        user_agent,
        headless: bool = False,
        full_screen: bool = True,
        page_load_timeout: int = 60,
    ):
        self.browser = browser_name

        self.implicit_wait = implicit_wait
        self.page_load_timeout = page_load_timeout

        self.user_agent = user_agent
        self.headless = headless

        self.full_screen = full_screen
        self._driver: webdriver = self._get_driver()

        # self.full_screen and self.fullscreen_window()
        self.full_screen and self.maximise_window()

    @property
    def driver(self):
        return self._driver

    def _get_driver(self) -> webdriver:
        """returns the driver/browser instance based on set variables and arguments"""

        driver_options = self._get_driver_options()
        driver_func = self.BROWSER_DRIVER_FUNCTION[self.browser]
        driver_service = self.BROWSER_DRIVER_SERVICE_FUNCTION[self.browser]
        driver_manager = self.BROWSER_DRIVER_MANAGER_FUNCTION[self.browser]

        driver: webdriver = driver_func(
            options=driver_options, service=driver_service(executable_path=driver_manager().install())
        )

        driver.implicitly_wait(self.implicit_wait)

        self.page_load_timeout and driver.set_page_load_timeout(self.page_load_timeout)

        return driver

    def _get_driver_options(self):
        driver_options = self.BROWSER_OPTION_FUNCTION[self.browser]()

        self.headless and driver_options.add_argument("--headless")

        driver_options.add_argument("--disable-gpu")
        driver_options.add_argument("--disable-extensions")
        driver_options.add_argument("--no-sandbox")
        driver_options.add_argument("no-default-browser-check")
        driver_options.add_argument("start-maximized")

        return driver_options

    @property
    def current_window_handle(self):
        return self.driver.current_window_handle

    @property
    def window_handles(self) -> list:
        return self.driver.window_handles

    def switch_to_window_handle(self, handle):
        self.driver.switch_to.window(handle)

    def fullscreen_window(self):
        self.driver.fullscreen_window()

    def maximise_window(self):
        self.driver.maximize_window()

    def minimise_window(self):
        self.driver.minimize_window()

    def close_driver(self):
        self.driver.close()

    def close(self):
        """Close Session"""
        self.__del__()

    def __del__(self):
        self.driver.quit()
