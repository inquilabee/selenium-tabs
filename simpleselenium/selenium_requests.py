import contextlib
import time
from collections import OrderedDict

import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from simpleselenium import scripts


class SeleniumRequestException(Exception):
    pass


class Session:
    """A top level class to manage a browser containing one/more Tabs"""

    BROWSER_DRIVER_FUNCTION = {
        "Chrome": webdriver.Chrome,
        "FireFox": webdriver.Firefox,
    }

    BROWSER_OPTION_FUNCTION = {"Chrome": ChromeOptions, "FireFox": FirefoxOptions}

    def __init__(self, browser_name, driver_path, implicit_wait, user_agent, headless=False):
        self.browser = browser_name

        self.implicit_wait = implicit_wait
        self.user_agent = user_agent
        self.headless = headless

        self.driver_path = driver_path
        self.driver = self._get_driver()

    def _get_driver(self) -> webdriver:
        """returns the driver/browser instance based on set variables and arguments"""

        driver_options = self.BROWSER_OPTION_FUNCTION[self.browser]()

        if self.headless:
            driver_options.headless = self.headless
            driver_options.add_argument("--disable-gpu")
            driver_options.add_argument("--disable-extensions")
            driver_options.add_argument("--no-sandbox")
            driver_options.add_argument("no-default-browser-check")

        driver = self.BROWSER_DRIVER_FUNCTION[self.browser](
            options=driver_options,
        )
        driver.implicitly_wait(self.implicit_wait)
        # driver.set_page_load_timeout(self.implicit_wait)

        return driver

    def close(self):
        """Close Session"""
        self.__del__()

    def __del__(self):
        self.driver.quit()


class Tab:
    """Single Tab"""

    def __init__(self, session, tab_handle, start_url: str = None):
        self._session = session
        self.tab_handle = tab_handle
        self.start_url = start_url

    def __str__(self):
        return (
            f"Tab(start_url={self.start_url}, active={self.is_active}, alive={self.is_alive}, handle={self.tab_handle})"
        )

    __repr__ = __str__

    @property
    def is_alive(self):
        """Whether the tab is one of the browser tabs"""
        return self.tab_handle in self._session.driver.window_handles

    @property
    def is_active(self):
        """Whether the tab is active tab on the browser"""
        try:
            return self._session.driver.current_window_handle == self.tab_handle
        except Exception:  # noqa
            return False

    @property
    def title(self) -> str:
        """Returns the title of the page at the moment"""
        return self.driver.title

    @property
    def url(self) -> str:
        """Returns the title of the page at the moment"""
        return self.driver.current_url

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    @property
    def driver(self) -> webdriver:
        """Switch to tab (if possible) and return driver"""

        if not self.is_alive:
            raise SeleniumRequestException("Current window is dead.")

        if not self.is_active:
            self._session.driver.switch_to.window(self.tab_handle)
        return self._session.driver

    def switch(self) -> bool:
        """Switch to tab (if possible)"""

        if self.is_active:
            # no need to switch
            return False

        if not self.is_alive:
            raise SeleniumRequestException(
                f"Current window is dead. Window Handle={self.tab_handle} does not exist"
                f" in all currently open window handles: {self._session.driver.window_handles}"
            )

        self._session.driver.switch_to.window(self.tab_handle)
        return True

    def open(self, url):
        """Open a url in the tab"""

        self.driver.get(url)
        return self

    def click(self, element) -> bool:
        """Click a given element on the page represented by the tab"""

        try:
            self.switch()
            element.click()
            return True
        except Exception as e:  # noqa
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:  # noqa
                return False

    @staticmethod
    def element_source(element: webelement):
        return element.get_attribute("outerHTML")

    @staticmethod
    def element_location(element: webelement) -> dict:
        return element.location

    @staticmethod
    def element_size(element: webelement) -> dict:
        return element.size

    @staticmethod
    def element_center(element):
        pass

    def run_js(self, script, *args):
        """Run JavaScript on the page"""
        return self.driver.execute_script(script, *args)

    def get_all_attributes_of_element(self, element) -> dict:
        """Get all attributes of a given element on the tab's page"""

        return self.run_js(scripts.ELEMENT_ATTRIBUTES, element)

    def get_attribute(self, element, attr_name):
        """Get specific attributes of a given element on the tab's page"""

        attr_dict = self.get_all_attributes_of_element(element=element)
        return attr_dict[attr_name]

    def find_element(self, by, value, multiple=False):
        """Try to find element given a criteria and the value"""

        elements = self.driver.find_elements(by, value)

        if multiple:
            return elements
        elif elements:
            if len(elements) > 1:
                raise SeleniumRequestException("Multiple elements found")
            else:
                return elements[0]
        else:
            return None

    @staticmethod
    def _scroll(clicks: int = 10, times: int = 1, direction=1):
        """Usual scroll"""

        # TODO: May not work in all the situations and OS'

        for _ in range(times):
            pyautogui.scroll(direction * clicks)
            time.sleep(0.5)

    def scroll_up(self, times: int = 1, clicks: int = 20):
        self.switch()
        self._scroll(clicks=clicks, times=times, direction=1)

    def scroll_down(self, times: int = 1, clicks: int = 20):
        self.switch()
        self._scroll(clicks=clicks, times=times, direction=-1)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page"""

        html = self.driver.find_element_by_tag_name("html")
        html.send_keys(Keys.END)

    def infinite_scroll(self, retries=5):
        """Infinite (so many times) scroll"""

        for _ in range(max(1, retries)):
            with contextlib.suppress(Exception):  # noqa
                last_height = 0

                while True:
                    self.scroll_to_bottom()
                    new_height = self.run_js(scripts.PAGE_HEIGHT)

                    if new_height == last_height:
                        break

                    last_height = new_height

    def wait_for_presence_of_element(self, element, wait):
        return WebDriverWait(self.driver, wait).until(EC.presence_of_element_located(element))

    def wait_for_visibility_of_element(self, element, wait):
        return WebDriverWait(self.driver, wait).until(EC.visibility_of_element_located(element))

    def wait_for_presence_and_visibility_of_element(self, element, wait):
        self.wait_for_visibility_of_element(element, wait)
        return self.wait_for_presence_of_element(element, wait)

    def wait_for_presence(self, by, key, wait):
        return WebDriverWait(self.driver, wait).until(EC.presence_of_element_located((by, key)))

    def wait_for_visibility(self, by, key, wait):
        return WebDriverWait(self.driver, wait).until(EC.visibility_of_element_located((by, key)))

    def wait_for_presence_and_visibility(self, by, key, wait):
        ele = self.wait_for_presence(by, key, wait)
        self.wait_for_visibility(by, key, wait)
        return ele

    def wait_until_staleness(self, element, wait: int = 5):
        """Wait until the passed element is no longer present on the page"""
        WebDriverWait(self.driver, wait).until(EC.staleness_of(element))


class TabManager:
    """A manager for multiple tabs associated with a browser"""

    def __init__(self, session):
        self._session = session
        self._all_tabs = OrderedDict()

    @property
    def driver(self):
        """driver object for the tab"""
        return self._session.driver

    def __len__(self):
        return len(self._all_tabs)

    def __del__(self):
        self._all_tabs = {}

    def __str__(self):
        return " ".join(self.all())

    def current_tab(self) -> [Tab, None]:
        """Get current active tab"""

        tab_handle = self.driver.current_window_handle
        return self.get(tab_handle)

    def get_blank_tab(self) -> Tab:
        """Get a blank tab to work with. Switches to the newly created tab"""
        windows_before = self.driver.current_window_handle
        self.driver.execute_script("window.open('about:blank');")
        windows_after = self.driver.window_handles
        new_window = [x for x in windows_after if x != windows_before][-1]
        self.driver.switch_to.window(new_window)
        new_tab = self.create(new_window)
        new_tab.switch()
        return new_tab

    def open_new_tab(self, url, wait_for_tag="body", wait_sec=30):
        """Open a new tab with a given URL.

        It also waits for a specified number of seconds for the specified tag to appear on the page"""

        blank_tab = self.get_blank_tab()
        blank_tab.start_url = url

        blank_tab.switch()
        blank_tab.open(url)

        if wait_for_tag:
            blank_tab.wait_for_presence_and_visibility(by=By.TAG_NAME, key=wait_for_tag, wait=wait_sec)

        return blank_tab

    def all(self):
        """All tabs of the browser"""
        curr_tab = self.current_tab()
        all_tabs = list(self._all_tabs.values())
        if curr_tab:
            curr_tab.switch()
        return all_tabs

    def create(self, tab_handle):
        """Create a Tab object"""

        tab = Tab(session=self._session, tab_handle=tab_handle)
        self.add(tab)
        return tab

    def add(self, tab: Tab) -> None:
        """Add a tab to list of tabs"""
        self._all_tabs.update({tab.tab_handle: tab})

    def get(self, tab_handle) -> [Tab, None]:
        """get a Tab object given their handle/id"""
        return self._all_tabs.get(tab_handle, None)

    def exist(self, tab: Tab) -> bool:
        """Check if a tab exist"""

        if isinstance(tab, Tab):
            return tab.tab_handle in self._all_tabs.keys()

        raise SeleniumRequestException("Invalid type for tab.")

    def remove(self, tab: Tab) -> [Tab, None]:
        """Remove a tab from the list of tabs"""

        if isinstance(tab, Tab):
            return self._all_tabs.pop(tab.tab_handle, None)

        raise SeleniumRequestException("Invalid type for tab.")

    @property
    def first_tab(self) -> Tab | None:
        """First tab from the list of tabs of the browser"""
        try:
            _, tab = list(self._all_tabs.items())[0]
            return tab
        except Exception:  # noqa
            return None

    @property
    def last_tab(self) -> Tab | None:
        """Last tab from the list of tabs of the browser"""
        try:
            _, tab = list(self._all_tabs.items())[-1]
            return tab
        except Exception:  # noqa
            return None

    def switch_to_first_tab(self):
        """Attempts to switch to the first tab"""

        if self.first_tab and self.first_tab.is_alive and self.exist(self.first_tab):
            self.first_tab.switch()
            return True

        return False

    def switch_to_last_tab(self):
        """Switch to the last tab"""

        if self.last_tab and self.last_tab.is_alive and self.exist(self.last_tab):
            self.last_tab.switch()
            return True

        return False


class Browser:
    """
    A browser containing session and all the available tabs.
    Most users will just interact with (objects of) this class.
    """

    BROWSER_DRIVER_PATH_ENV = {
        "Chrome": "CHROME_DRIVER_PATH",
        "FireFox": "FIREFOX_DRIVER_PATH",
    }

    def __init__(self, name, driver_path=None, implicit_wait: int = 0, user_agent: str = "", headless=False):
        self.name = name

        self.implicit_wait = implicit_wait
        self.user_agent = user_agent
        self.driver_path = driver_path

        self._session = Session(
            name,
            driver_path,
            headless=headless,
            implicit_wait=self.implicit_wait,
            user_agent=self.user_agent,
        )
        self._tabs = TabManager(self._session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def tabs(self) -> list:
        """Returns all open tabs"""
        return self._tabs.all()

    @property
    def current_tab(self) -> Tab:
        """get current tab from the list of the tabs"""
        return self._tabs.current_tab()

    @property
    def first_tab(self) -> Tab:
        return self._tabs.first_tab

    @property
    def last_tab(self) -> Tab:
        return self._tabs.last_tab

    def open(self, url):
        """Starts a new tab with the given url at end of list of tabs."""

        self._tabs.switch_to_last_tab()
        curr_tab = self._tabs.open_new_tab(url)
        curr_tab.switch()
        return curr_tab

    def _remove_tab(self, tab: Tab):
        """For Internal Use Only: Closes a given tab.

        The order of operation is extremely important here. Practice extreme caution while editing this."""

        assert tab.is_alive is True  # noqa # nosec
        assert self._tabs.exist(tab) is True  # noqa # nosec

        tab.switch()
        self._tabs.remove(tab)
        self._session.driver.close()

        assert tab.is_alive is False  # noqa # nosec
        assert self._tabs.exist(tab) is False  # noqa # nosec

    def close_tab(self, tab: Tab):
        """Close a given tab"""
        if self._tabs.exist(tab):
            tab.switch()
            self._remove_tab(tab=tab)
            self._tabs.switch_to_last_tab()
            return True
        else:
            raise SeleniumRequestException("Tab does not exist.")

    def close(self):
        """Close browser"""
        self._tabs = {}
        self._session.close()


if __name__ == "__main__":
    with Browser(name="Chrome", driver_path=None, implicit_wait=10) as browser:
        google = browser.open("https://google.com")  # a `Tab` object
        yahoo = browser.open("https://yahoo.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")

        yahoo.scroll_up(times=5)
        yahoo.scroll_down(times=10)

        print(browser.tabs)
        print(browser.current_tab)
        print(browser.first_tab)
        print(browser.last_tab)

        print(browser.last_tab.switch())

        print(google.page_source)
        print(google.title)
        print(google.url)
        print(google.is_active)
        print(google.is_alive)

        browser.close_tab(bing)
        print(browser.tabs)

        print(browser.current_tab)

        yahoo.switch()
        print(browser.current_tab)
        google.switch()

        print(browser.current_tab)

        browser.close_tab(yahoo)

        print(yahoo.is_alive)
        print(yahoo.is_active)

        print(google.driver.title, google.title)
        print(google.driver.title == google.title)
