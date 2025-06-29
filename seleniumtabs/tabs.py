import contextlib
import logging
import random
import time
from collections import OrderedDict
from collections.abc import Iterator
from threading import Lock
from typing import Any

from browserjquery import BrowserJQuery
from pyquery import PyQuery
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from seleniumtabs.browser_management import browser_sessions
from seleniumtabs.css_selectors import SelectableCSS
from seleniumtabs.exceptions import SeleniumOpenTabException, SeleniumRequestException
from seleniumtabs.js_scripts import scripts
from seleniumtabs.schedule_tasks import task_scheduler
from seleniumtabs.session import Session
from seleniumtabs.utils.urls import get_domain
from seleniumtabs.wait import humanized_wait

logger = logging.getLogger(__name__)

lock = Lock()


class Tab:
    """Single Tab"""

    SCROLL_DIST = 50

    def __init__(self, session: Session, tab_handle, start_url: str | None = None, full_screen: bool = True):
        self._session = session
        self.tab_handle = tab_handle
        self.start_url = start_url
        self.full_screen = full_screen

    @property
    def driver(self) -> webdriver.Chrome | webdriver.Firefox:
        """Switch to tab (if possible) and return the driver object."""

        if not self.is_alive:
            raise SeleniumRequestException("Current window is dead.")

        if not self.is_active:
            self._session.switch_to_window_handle(self.tab_handle)

        return self._session.driver

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f"("
            f"start_url={self.start_url}, "
            f"active={self.is_active}, "
            f"alive={self.is_alive}, "
            f"handle={self.tab_handle}"
            f")"
        )

    __repr__ = __str__

    def __getattribute__(self, item):
        with contextlib.suppress(Exception):
            return super().__getattribute__(item)

        return getattr(self.driver, item)

    def __del__(self):
        self.close()

    def __hash__(self):
        return hash(self.tab_handle)

    def __eq__(self, other: "Tab"):  # type: ignore
        return self.tab_handle == other.tab_handle

    def maximise(self):
        self._session.maximise_window()

    @property
    def jquery(self) -> BrowserJQuery:
        """Access jquery methods via this property"""
        return BrowserJQuery(driver=self.driver)

    @property
    def jq(self) -> BrowserJQuery:
        """Alias for jquery"""
        return self.jquery

    def css(self, css_selector: str) -> list:
        return SelectableCSS(self.driver).css(css_selector)  # type: ignore # noqa

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
        """Returns the url of the page at the moment"""
        return self.driver.current_url

    @property
    def domain(self) -> str:
        """Returns the domain of the page url at the moment"""
        return get_domain(self.driver.current_url)

    def has_page_loaded(self) -> bool:
        """Check if the page has finished loading.

        Reference: https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
        """
        page_state = self.driver.execute_script(scripts.PAGE_LOAD_CHECK)
        return page_state == "complete"

    def wait_for_loading(self, max_wait: int | float = 5, check_duration: int | float = 0.5) -> bool:
        """Wait until the page has finished loading.

        Reference: https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
        """
        start = time.perf_counter()

        ready = "nope"

        while ready != "complete" and time.perf_counter() - start < max_wait:
            ready = self.driver.execute_script(scripts.PAGE_LOAD_CHECK)
            time.sleep(check_duration)

        return ready == "complete"

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    @property
    def page_html(self) -> str:
        return self.jquery.page_html

    @property
    def page_height(self):
        return self.run_js(scripts.PAGE_HEIGHT)

    @property
    def user_agent(self):
        return self.run_js(scripts.USER_AGENT)

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

    def open(
        self, url, partial_load: bool = True, wait: int = 1, wait_for_redirect: int | float = 1, timeout: int = 30
    ) -> "Tab":
        """Open an url in the tab with optional partial loading.

        Args:
            url: The URL to open
            partial_load: Whether to allow partial loading if full load times out
            wait: Minimum wait time after loading (seconds)
            wait_for_redirect: Maximum time to wait for redirects (seconds)
            timeout: Maximum time to wait for initial page load (seconds)

        Returns:
            self: The tab instance for method chaining

        Raises:
            SeleniumOpenTabException: If the page cannot be loaded even partially
        """
        start_time = time.perf_counter()

        try:
            # Attempt full page load with timeout
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)

            # Wait for minimum time and check loading
            humanized_wait(wait or 0)
            if self.wait_for_loading(wait_for_redirect):
                logger.info(f"Page fully loaded: {self.url}")
                return self

        except Exception as e:
            logger.warning(f"Full page load failed after {time.perf_counter() - start_time:.1f}s: {str(e)}")

            if not partial_load:
                raise SeleniumOpenTabException(f"Could not open {url} - full load required but failed") from e

        # If we get here, either full load failed or partial load is allowed
        if partial_load:
            try:
                # Stop loading and check if we got something useful
                self.driver.execute_script(scripts.STOP_PAGE_LOADING)
                humanized_wait(1)  # Give a moment for any pending operations

                # Check if we got at least the domain loaded
                if url in self.domain or self.domain in url:
                    logger.info(f"Page partially loaded after {time.perf_counter() - start_time:.1f}s: {self.url}")
                    return self

            except Exception as e:
                logger.error(f"Partial load failed: {str(e)}")

        raise SeleniumOpenTabException(f"Could not open {url} - neither full nor partial load succeeded")

    def close(self):
        browser_sessions.close_tab(self)

    def click(self, element: webelement.WebElement) -> bool:
        """Click a given element on the page represented by the tab"""

        with contextlib.suppress(Exception):
            return self._click_on_random_position(element)

        with contextlib.suppress(Exception):
            self.driver.execute_script(scripts.ELEMENT_CLICK, element)
            return True

        with contextlib.suppress(Exception):
            self.switch()
            element.click()
            return True

        return False

    def _click_on_random_position(self, element):
        """Given an element, click at the random position of the element instead of the
        exact centre of the element.

        Code Adapted from: https://pylessons.com/Selenium-with-python-click-as-human
        """

        self.switch()

        height = random.randint(1, element.size["height"] // 2)
        width = random.randint(1, element.size["width"] // 2)

        action = ActionChains(self.driver)

        # offsets are measured from the centre of the element
        action.move_to_element_with_offset(element, width, height)
        action.click()
        action.perform()

        return True

    def empty_click(self) -> bool:
        """Simulates empty click on the webpage.

        SO: https://stackoverflow.com/questions/27966080/how-to-simulate-mouse-click-on-blank-area
        """

        with contextlib.suppress(Exception):
            self.driver.find_element(by=By.XPATH, value=r"//body").click()
            return True

        with contextlib.suppress(Exception):
            action = ActionChains(self.driver)

            action.move_by_offset(0, 0)
            action.click()
            action.perform()
            return True

        with contextlib.suppress(Exception):
            self.driver.find_element(by=By.XPATH, value=r"//html").click()
            return True

        return False

    @staticmethod
    def element_source(element: webelement.WebElement):
        return element.get_attribute("outerHTML")

    @staticmethod
    def element_location(element: webelement.WebElement) -> dict:
        return element.location

    @staticmethod
    def element_size(element: webelement.WebElement) -> dict:
        return element.size

    @staticmethod
    def element_center(element):
        pass

    def run_js(self, script: str, *args) -> Any:
        """Run JavaScript on the page"""
        return self.driver.execute_script(script, *args)

    def get_all_attributes_of_element(self, element: webelement.WebElement) -> dict:
        """Get all attributes of a given element on the tab's page"""

        return self.run_js(scripts.ELEMENT_ATTRIBUTES, element)

    def get_attribute(self, element: webelement.WebElement, attr_name: str) -> Any:
        """Get specific attributes of a given element on the tab's page"""

        attr_dict = self.get_all_attributes_of_element(element=element)
        return attr_dict[attr_name]

    def find_element(
        self, by: str, value: str, multiple: bool = False
    ) -> webelement.WebElement | None | list[webelement.WebElement]:
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

    def scroll(self, times: int = 1, clicks: int | None = None, direction: int = 1, wait: int = 3):
        """Usual scroll"""
        self.switch()

        assert direction in {1, -1}  # noqa  # nosec

        for _ in range(times):
            logger.info(f"Current page height: {self.page_height}")

            new_height = self.page_height + direction * (clicks or self.SCROLL_DIST)
            self.run_js(scripts.SCROLL_TO_WINDOW_HEIGHT, new_height)
            time.sleep(wait)

            logger.info(f"Updated page height: {self.page_height}")

    def scroll_up(self, times: int = 1, clicks: int | None = None, wait: int = 3):
        self.switch()
        self.scroll(clicks=clicks, times=times, direction=-1, wait=wait)

    def scroll_down(self, times: int = 1, clicks: int | None = None, wait: int = 3):
        self.switch()
        self.scroll(clicks=clicks, times=times, direction=1, wait=wait)

    def scroll_to_bottom(self, wait: int | None = None):
        """Scroll to the bottom of the page"""

        self.wait_for_presence_and_visibility(by=By.TAG_NAME, key="html", wait=wait or 5)
        html = self.driver.find_elements(by=By.TAG_NAME, value="html")

        if html and html[0]:
            html[0].send_keys(Keys.END)

        self.run_js(scripts.SCROLL_TO_WINDOW_HEIGHT, self.page_height)

        time.sleep(wait or 0)

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

    # Visibility and Presence

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

    # Staleness and invisibility

    def wait_for_staleness_of_element(self, element, wait: int = 5):
        """Wait until the passed element is no longer attached to the DOM.

        Args:
            element: The element to wait for staleness
            wait: Maximum time to wait in seconds

        Returns:
            bool: True if element became stale within wait time, False otherwise
        """
        return WebDriverWait(self.driver, wait).until(EC.staleness_of(element))

    def wait_for_staleness(self, by, key, wait: int = 5):
        """Wait until the element matching the locator is no longer attached to the DOM.

        Args:
            by: The locator strategy (e.g., By.ID, By.CLASS_NAME)
            key: The locator value
            wait: Maximum time to wait in seconds

        Returns:
            bool: True if element became stale within wait time, False otherwise
        """
        try:
            element = self.driver.find_element(by, key)
            return self.wait_for_staleness_of_element(element, wait)
        except Exception:
            return False

    def wait_for_invisibility_of_element(self, element, wait: int = 5):
        """Wait until the passed element is no longer visible.

        Args:
            element: The element to wait for invisibility
            wait: Maximum time to wait in seconds

        Returns:
            bool: True if element became invisible within wait time, False otherwise
        """
        return WebDriverWait(self.driver, wait).until(EC.invisibility_of_element_located(element))

    def wait_for_invisibility(self, by, key, wait: int = 5):
        """Wait until the element matching the locator is no longer visible.

        Args:
            by: The locator strategy (e.g., By.ID, By.CLASS_NAME)
            key: The locator value
            wait: Maximum time to wait in seconds

        Returns:
            bool: True if element became invisible within wait time, False otherwise
        """
        return WebDriverWait(self.driver, wait).until(EC.invisibility_of_element_located((by, key)))

    def wait_for_disappearance(self, by, key, wait: int = 5):
        """Wait until the element matching the locator is no longer present in the DOM.

        Args:
            by: The locator strategy (e.g., By.ID, By.CLASS_NAME)
            key: The locator value
            wait: Maximum time to wait in seconds

        Returns:
            bool: True if element disappeared within wait time, False otherwise
        """
        try:
            WebDriverWait(self.driver, wait).until_not(EC.presence_of_element_located((by, key)))
            return True
        except Exception:
            return False

    def wait_for_url(self, url: str, wait: int = 10) -> bool:
        """Wait until the url is available.

        Note: it does not wait indefinitely for the url to appear,
        rather waits for the specified maximum time and returns
        if the url appeared or not.
        """

        with contextlib.suppress(Exception):
            WebDriverWait(self.driver, wait).until(EC.url_to_be(url))
            return True

        return False

    @property
    def pyquery(self) -> PyQuery:
        """Use the powerful pyquery on a Tab object.

        http://pyquery.rtfd.org
        """

        return PyQuery(self.page_html)

    @property
    def pq(self) -> PyQuery:
        """Use the powerful pyquery on a Tab object.

        http://pyquery.rtfd.org
        """

        return self.pyquery

    def schedule_task(self, task, period: int, *args, **kwargs):
        task_scheduler.schedule_task(self, task, period, *args, **kwargs)


class TabManager:
    """A manager for multiple tabs associated with a browser.

    This class manages the lifecycle and operations of browser tabs, including:
    - Creating and tracking tabs
    - Switching between tabs
    - Managing tab state
    - Handling tab operations (open, close, switch)
    """

    def __init__(self, session: Session):
        self._session = session
        self._all_tabs = OrderedDict()

    def __iter__(self) -> Iterator[Tab]:
        """Make TabManager iterable by yielding tab values"""
        return iter(self._all_tabs.values())

    @property
    def driver(self) -> webdriver.Chrome | webdriver.Firefox:
        """driver object for the Tab Manager"""
        return self._session.driver

    def clear(self) -> None:
        """Clear all tabs from the manager"""

        self._all_tabs = OrderedDict()

    def __len__(self) -> int:
        """Return the number of managed tabs"""
        return len(self._all_tabs)

    def __bool__(self) -> bool:
        """Return True if there are any managed tabs"""
        return bool(self._all_tabs)

    def __del__(self) -> None:
        """Clean up all tabs when the manager is deleted"""
        self._all_tabs = {}

    def __getitem__(self, index: int) -> Tab:
        """Get a tab by index"""
        return list(self._all_tabs.values())[index]

    def __str__(self) -> str:
        """Return a string representation of all tab handles"""
        return " ".join(list(self._all_tabs))

    def current_tab(self) -> Tab | None:
        """Get current active tab"""
        tab_handle = self.driver.current_window_handle
        return self.get(tab_handle)

    def get_blank_tab(self, full_screen: bool) -> Tab:
        """Get a blank tab to work with. Switches to the newly created tab"""

        windows_before = set(self.driver.window_handles)

        self.driver.execute_script(scripts.NEW_TAB)

        if not (new_window := set(self.driver.window_handles) - windows_before):
            raise SeleniumOpenTabException("Could not open new tab. Error in getting a blank tab.")

        new_window = list(new_window)[0]

        self.driver.switch_to.window(new_window)

        new_tab = self.create(new_window, full_screen)
        new_tab.switch()

        return new_tab

    def open_new_tab(self, url, wait_sec=30, full_screen: bool = True, **open_kw) -> Tab:
        """Open a new tab with a given URL.

        It also waits for a specified number of seconds for the specified tag to appear on the page"""

        blank_tab = self.get_blank_tab(full_screen=full_screen)
        blank_tab.start_url = url

        blank_tab.switch()
        blank_tab.open(url, **open_kw)

        blank_tab.wait_for_body_tag_presence_and_visibility(wait=wait_sec)

        return blank_tab

    def create(self, tab_handle, full_screen: bool = True) -> Tab:
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

    def remove(self, tab: Tab) -> Tab | None:
        """Remove a tab from the list of tabs"""

        if isinstance(tab, Tab):
            return self._all_tabs.pop(tab.tab_handle, None)
        return None

    @property
    def first_tab(self) -> Tab | None:
        """First tab from the list of tabs of the browser"""
        return self[0] if self._all_tabs else None

    @property
    def last_tab(self) -> Tab | None:
        """Last tab from the list of tabs of the browser"""
        return self[-1] if self._all_tabs else None

    def switch_to_tab(self, tab: Tab) -> bool:
        """Switch to the specified tab if it exists and is alive"""
        if tab and tab.is_alive and self.exist(tab):
            tab.switch()
            return True
        return False

    def switch_to_first_tab(self) -> bool:
        """Attempts to switch to the first tab"""
        _tab = self.first_tab
        if _tab and _tab.is_alive and self.exist(_tab):
            _tab.switch()
            return True
        return False

    def switch_to_last_tab(self) -> bool:
        """Switch to the last tab"""
        _tab = self.last_tab
        if _tab and _tab.is_alive and self.exist(_tab):
            _tab.switch()
            return True
        return False

    def unmanaged_tabs(self) -> list[Tab]:
        """Get tabs that are not managed by this manager"""

        curr_tab = self.current_tab()
        curr_tabs = set(self._all_tabs)
        tabs = [
            Tab(session=self._session, tab_handle=handle)
            for handle in self._session.window_handles
            if handle not in curr_tabs
        ]

        for tab in tabs:
            tab.start_url = tab.url

        if curr_tab:
            curr_tab.switch()

        return tabs
