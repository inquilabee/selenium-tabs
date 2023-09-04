import contextlib
import time
from collections import OrderedDict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import settings
from simpleselenium import scripts
from simpleselenium.element_selectors import SelectableCSS
from simpleselenium.exceptions import SeleniumRequestException
from simpleselenium.session import Session

logger = settings.getLogger(__name__)


class Tab:
    """Single Tab"""

    SCROLL_DIST = 50

    def __init__(self, session, tab_handle, start_url: str = None, full_screen: bool = True):
        self._session: Session = session
        self.tab_handle = tab_handle
        self.start_url = start_url
        self.full_screen = full_screen

    @property
    def driver(self) -> webdriver:
        """Switch to tab (if possible) and return the driver object."""

        if not self.is_alive:
            raise SeleniumRequestException("Current window is dead.")

        if not self.is_active:
            self._session.switch_to_window_handle(self.tab_handle)

        return self._session.driver

    def __str__(self):
        return (
            f"Tab(start_url={self.start_url}, active={self.is_active}, alive={self.is_alive}, handle={self.tab_handle})"
        )

    __repr__ = __str__

    def __del__(self):
        pass

    def __hash__(self):
        return self.tab_handle

    def __eq__(self, other: "Tab"):
        return self.tab_handle == other.tab_handle

    def maximise(self):
        self._session.maximise_window()

    def css(self, css_selector: str) -> list:
        return SelectableCSS(self.driver).css(css_selector)

    def run_jquery(self, script_code: str, element: webelement.WebElement, *args):
        # TODO: Allow multiple elements as input and check (using regex?) that passed elements are wrapped inside $
        return self.run_js(script_code, element, *args)

    def inject_jquery(self, by: str = "file", wait: int = 2):
        """
        SO: https://stackoverflow.com/a/57947790/8414030
        """
        self._inject_jquery_file(wait=wait) if by == "file" else self._inject_jquery_cdn(wait=wait)

    def _inject_jquery_cdn(self, wait: int = 2):
        self.driver.execute_script(scripts.JQUERY_INJECTION)

        time.sleep(wait)

    def _inject_jquery_file(self, wait: int = 2):
        with open("../data/jquery.js") as f:
            self.driver.execute_script(f.read())

        time.sleep(wait)

    @property
    def is_alive(self):
        """Whether the tab is one of the browser tabs"""
        return self.tab_handle in self._session.window_handles

    @property
    def is_active(self):
        """Whether the tab is active tab on the browser"""
        try:
            return self._session.current_window_handle == self.tab_handle
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
    def page_height(self):
        return self.run_js(scripts.PAGE_HEIGHT)

    def switch(self) -> bool:
        """Switch to tab (if possible)"""

        if self.is_active:
            # no need to switch
            return False

        if not self.is_alive:
            raise SeleniumRequestException(
                f"Current window is dead. Window Handle={self.tab_handle} does not exist"
                f" in all currently open window handles: {self._session.window_handles}"
            )

        self._session.switch_to_window_handle(self.tab_handle)

        return True

    def open(self, url):
        """Open an url in the tab"""

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

    def scroll(self, times=1, clicks: int = None, direction: int = 1, wait: int = 3):
        """Usual scroll"""
        self.switch()

        assert direction in {1, -1}  # noqa  # nosec

        for _ in range(times):
            logger.info(f"Current page height: {self.page_height}")

            new_height = self.page_height + direction * (clicks or self.SCROLL_DIST)
            self.run_js(scripts.SCROLL_TO_WINDOW_HEIGHT, new_height)
            time.sleep(wait)

            logger.info(f"Updated page height: {self.page_height}")

    def scroll_up(self, times: int = 1, clicks: int = None, wait: int = 3):
        self.switch()
        self.scroll(clicks=clicks, times=times, direction=-1, wait=wait)

    def scroll_down(self, times: int = 1, clicks: int = None, wait: int = 3):
        self.switch()
        self.scroll(clicks=clicks, times=times, direction=1, wait=wait)

    def scroll_to_bottom(self, wait: int = None):
        """Scroll to the bottom of the page"""

        html = self.driver.find_element_by_tag_name("html")
        html.send_keys(Keys.END)

        wait and time.sleep(wait)

    def infinite_scroll(self, retries=5):
        """Infinite (so many times) scroll"""

        for _ in range(max(1, retries)):
            with contextlib.suppress(Exception):  # noqa
                last_height = 0

                while True:
                    self.scroll_to_bottom()

                    if self.page_height == last_height:
                        break

                    last_height = self.page_height

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

    def wait_for_body_tag_presence_and_visibility(self, wait: int = 5):
        self.wait_for_presence_and_visibility(by=By.TAG_NAME, key="body", wait=wait)

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
        """driver object for the Tab Manager"""

        return self._session.driver

    def __len__(self):
        return len(self._all_tabs)

    def __bool__(self):
        return bool(self._all_tabs)

    def __del__(self):
        self._all_tabs = {}

    def __getitem__(self, index):
        return list(self._all_tabs.values())[index]

    def __str__(self):
        return " ".join(list(self))  # noqa

    def current_tab(self) -> [Tab, None]:
        """Get current active tab"""

        tab_handle = self.driver.current_window_handle
        return self.get(tab_handle)

    def get_blank_tab(self, full_screen) -> Tab:
        """Get a blank tab to work with. Switches to the newly created tab"""
        windows_before = self.driver.current_window_handle
        self.driver.execute_script("window.open('about:blank');")
        windows_after = self.driver.window_handles
        new_window = [x for x in windows_after if x != windows_before][-1]

        self.driver.switch_to.window(new_window)

        new_tab = self.create(new_window, full_screen)
        new_tab.switch()

        return new_tab

    def open_new_tab(self, url, wait_sec=30, full_screen: bool = True):
        """Open a new tab with a given URL.

        It also waits for a specified number of seconds for the specified tag to appear on the page"""

        blank_tab = self.get_blank_tab(full_screen=full_screen)
        blank_tab.start_url = url

        blank_tab.switch()
        blank_tab.open(url)

        blank_tab.wait_for_body_tag_presence_and_visibility(wait=wait_sec)

        return blank_tab

    def create(self, tab_handle, full_screen):
        """Create a Tab object"""

        tab = Tab(session=self._session, tab_handle=tab_handle, full_screen=full_screen)
        self.add(tab)
        return tab

    def add(self, tab: Tab) -> None:
        """Add a tab to the list of tabs"""
        self._all_tabs.update({tab.tab_handle: tab})

    def get(self, tab_handle) -> Tab | None:
        """get a Tab object given their handle/id"""

        return self._all_tabs.get(tab_handle, None)

    def exist(self, tab: Tab) -> bool:
        """Check if a tab exists"""

        return tab in self

    def remove(self, tab: Tab) -> [Tab, None]:
        """Remove a tab from the list of tabs"""

        if isinstance(tab, Tab):
            return self._all_tabs.pop(tab.tab_handle, None)

        raise SeleniumRequestException("Invalid type for tab.")

    @property
    def first_tab(self) -> Tab | None:
        """First tab from the list of tabs of the browser"""

        return self[0] if self._all_tabs else None

    @property
    def last_tab(self) -> Tab | None:
        """Last tab from the list of tabs of the browser"""

        return self[-1] if self._all_tabs else None

    def switch_to_tab(self, tab: Tab):
        if tab and tab.is_alive and self.exist(tab):
            tab.switch()
            return True

        return False

    def switch_to_first_tab(self):
        """Attempts to switch to the first tab"""

        _tab = self.first_tab

        if _tab and _tab.is_alive and self.exist(_tab):
            _tab.switch()
            return True

        return False

    def switch_to_last_tab(self):
        """Switch to the last tab"""

        _tab = self.last_tab

        if _tab and _tab.is_alive and self.exist(_tab):
            _tab.switch()
            return True

        return False
