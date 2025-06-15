import logging

from seleniumtabs.browser_management import browser_sessions
from seleniumtabs.exceptions import SeleniumRequestException
from seleniumtabs.schedule_tasks import task_scheduler
from seleniumtabs.session import Session
from seleniumtabs.tabs import Tab, TabManager
from seleniumtabs.wait import humanized_wait

logger = logging.getLogger(__name__)


class Browser:
    """
    A browser containing session and all the available tabs.

    Most users will just interact with (objects of) this class.
    """

    def __init__(
        self,
        name: str,
        implicit_wait: int = 0,
        user_agent: str | None = None,
        headless: bool = False,
        full_screen: bool = True,
    ):
        logger.info(f"Initializing Browser with name: {name}")
        self.name = name

        logger.info("Creating new Session")
        self._session = Session(
            name,
            headless=headless,
            implicit_wait=implicit_wait,
            user_agent=user_agent,
            full_screen=full_screen,
        )
        logger.info("Session created successfully")

        self._manager: TabManager = TabManager(self._session)
        self.full_screen = full_screen

        browser_sessions.add_browser(self)
        logger.info("Browser initialization complete")

    def __enter__(self) -> "Browser":
        """Context manager entry point"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit point - ensures browser is closed"""
        self.close()

    def __del__(self) -> None:
        """Destructor to ensure browser cleanup when object is garbage collected"""
        self.close()

    @property
    def tabs(self) -> list[Tab]:
        """Returns all open tabs in the browser"""
        return list(self._manager)

    @property
    def current_tab(self) -> Tab | None:
        """Get the currently active tab from the list of tabs"""
        return self._manager.current_tab()

    @property
    def first_tab(self) -> Tab | None:
        """Get the first tab from the list of tabs"""
        return self._manager.first_tab

    @property
    def last_tab(self) -> Tab | None:
        """Get the last tab from the list of tabs"""
        return self._manager.last_tab

    def unmanaged_tabs(self) -> list[Tab]:
        """Get tabs which have not been created using `Browser.open()` method.

        Returns:
            list[Tab]: List of tabs that are not managed by this browser instance
        """
        return self._manager.unmanaged_tabs()

    def open(self, url: str = "data:,", **kwargs) -> Tab:
        """Start a new tab with the given url at the end of the list of tabs.

        Args:
            url: The URL to open in the new tab. Defaults to "data:,"
            **kwargs: Additional arguments to pass to the tab creation

        Returns:
            Tab: The newly created tab object
        """
        self._manager.switch_to_last_tab()
        curr_tab = self._manager.open_new_tab(url, full_screen=self.full_screen, **kwargs)
        curr_tab.switch()
        return curr_tab

    def close_tab(self, tab: Tab) -> bool:
        """Close a given tab.

        Args:
            tab: The tab to close

        Returns:
            bool: True if the tab was closed successfully

        Raises:
            SeleniumRequestException: If the tab does not exist
        """
        if self._manager.exist(tab):
            tab.switch()
            self._remove_tab(tab=tab)
            humanized_wait(1)
            self._manager.switch_to_last_tab()
            return True

        raise SeleniumRequestException("Tab does not exist.")

    def close(self) -> None:
        """Close the browser and clean up all resources"""
        try:
            # Cancel any scheduled tasks first
            task_scheduler.cancel_all_tasks()

            # Close all tabs and clear the manager
            if hasattr(self, "_manager"):
                self._manager.clear()

            # Close the session
            if hasattr(self, "_session"):
                self._session.close()

            # Remove from browser sessions
            if hasattr(self, "name"):
                browser_sessions.browser_sessions = [b for b in browser_sessions.browser_sessions if b != self]

        except Exception:
            raise

    def __contains__(self, item: Tab) -> bool:
        """Check if a tab exists in the browser"""
        return item in self.tabs

    def _remove_tab(self, tab: Tab) -> None:
        """For Internal Use Only: Closes a given tab.

        The order of operation is extremely important here. Practice extreme caution while editing this.

        Args:
            tab: The tab to remove

        Note:
            This method performs several assertions to ensure the tab state is correct
            before and after removal.
        """
        assert tab.is_alive is True  # noqa # nosec
        assert self._manager.exist(tab) is True  # noqa # nosec

        tab.switch()
        self._manager.remove(tab)
        self._session.close_driver()

        assert tab.is_alive is False  # noqa # nosec
        assert self._manager.exist(tab) is False  # noqa # nosec

        if self._manager and self._manager.last_tab:
            self._manager.last_tab.switch()

    def execute_task(self, max_time: int | None = None, sleep_time: float = 1.0) -> None:
        """Execute scheduled tasks.

        Args:
            max_time: Maximum time in seconds to execute tasks. If None, no time limit is applied.
            sleep_time: Time in seconds to sleep between task checks. Defaults to 1.0 second.
                      Lower values will check for tasks more frequently but use more CPU.
                      Higher values will use less CPU but may delay task execution.
        """
        task_scheduler.execute_tasks(max_time=max_time, sleep_time=sleep_time)
