import time

from simpleselenium.exceptions import SeleniumRequestException
from simpleselenium.session import Session
from simpleselenium.tabs import Tab, TabManager


class Browser:
    """
    A browser containing session and all the available tabs.
    Most users will just interact with (objects of) this class.
    """

    def __init__(
        self,
        name,
        implicit_wait: int = 0,
        user_agent: str = None,
        headless: bool = False,
        full_screen: bool = True,
    ):
        self.name = name

        self.implicit_wait = implicit_wait
        self.user_agent = user_agent

        self._session = Session(
            name,
            headless=headless,
            implicit_wait=self.implicit_wait,
            user_agent=self.user_agent,
        )
        self._tabs = TabManager(self._session)
        self.full_screen = full_screen

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def tabs(self) -> list:
        """Returns all open tabs"""
        return list(self._tabs)  # noqa

    @property
    def current_tab(self) -> Tab:
        """get the current tab from the list of the tabs"""
        return self._tabs.current_tab()

    @property
    def first_tab(self) -> Tab:
        return self._tabs.first_tab

    @property
    def last_tab(self) -> Tab:
        return self._tabs.last_tab

    def user_agent(self):
        pass

    def open(self, url) -> Tab:
        """Starts a new tab with the given url at the end of the list of tabs."""

        self._tabs.switch_to_last_tab()
        curr_tab = self._tabs.open_new_tab(url, full_screen=self.full_screen)
        curr_tab.switch()
        return curr_tab

    def close_tab(self, tab: Tab):
        """Close a given tab"""
        if self._tabs.exist(tab):
            tab.switch()
            self._remove_tab(tab=tab)
            time.sleep(1)
            self._tabs.switch_to_last_tab()
            return True
        else:
            raise SeleniumRequestException("Tab does not exist.")

    def close(self):
        """Close browser"""
        self._tabs = {}
        self._session.close()

    def _remove_tab(self, tab: Tab):
        """For Internal Use Only: Closes a given tab.

        The order of operation is extremely important here. Practice extreme caution while editing this."""

        assert tab.is_alive is True  # noqa # nosec
        assert self._tabs.exist(tab) is True  # noqa # nosec

        tab.switch()
        self._tabs.remove(tab)
        self._session.close_driver()

        assert tab.is_alive is False  # noqa # nosec
        assert self._tabs.exist(tab) is False  # noqa # nosec

        self._tabs and self._tabs.last_tab.switch()


if __name__ == "__main__":
    err_msg = "Something went wrong. Report!"

    with Browser(name="Chrome", implicit_wait=10) as browser:
        google: Tab = browser.open("https://google.com")
        yahoo = browser.open("https://yahoo.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")

        yahoo.scroll_down(times=5)
        yahoo.scroll_up(times=5)
        yahoo.scroll(times=5, wait=20)

        assert len(browser.tabs) == 4, err_msg  # noqa
        assert google in browser.tabs, err_msg  # noqa
        assert browser.tabs[0] == google, err_msg  # noqa

        for tab in browser.tabs:
            print(tab)

        print(browser.tabs)
        print(browser.current_tab)

        yahoo.inject_jquery()

        for item in yahoo.run_js("""return $(".stream-items a");"""):
            result = yahoo.run_jquery(
                script_code="""
                        return $(arguments[0]).text();
                    """,
                element=item,
            )

            print(result)

        for item in yahoo.css(".stream-items"):
            for a in item.css("a"):
                print(a, a.text)

        assert yahoo == browser.current_tab, err_msg  # noqa

        print(browser.first_tab)
        assert google == browser.first_tab, err_msg  # noqa

        print(browser.last_tab)
        assert duck_duck == browser.last_tab, err_msg  # noqa

        print(browser.last_tab.switch())
        assert browser.current_tab == duck_duck, err_msg  # noqa

        print(google.page_source)
        print(google.title)
        print(google.url)

        print(google.is_active)
        assert google.is_active is True, err_msg  # noqa
        assert google.is_alive is True, err_msg  # noqa

        print(google.is_alive)
        assert google.is_alive is True, err_msg  # noqa

        browser.close_tab(bing)
        print(browser.tabs)

        assert bing.is_alive is False, err_msg  # noqa
        assert bing.is_active is False, err_msg  # noqa
        assert bing not in browser.tabs, err_msg  # noqa

        print(browser.current_tab)
        assert duck_duck == browser.current_tab, err_msg  # noqa
        assert duck_duck.is_alive, err_msg  # noqa
        assert duck_duck.is_active, err_msg  # noqa

        yahoo.switch()

        print(browser.current_tab)
        assert yahoo == browser.current_tab, err_msg  # noqa
        assert yahoo.is_alive, err_msg  # noqa
        assert yahoo.is_active, err_msg  # noqa
        assert duck_duck.is_active is False, err_msg  # noqa

        google.switch()

        print(browser.current_tab)
        assert google == browser.current_tab, err_msg  # noqa

        browser.close_tab(yahoo)

        print(yahoo.is_alive)
        print(yahoo.is_active)

        assert yahoo.is_active is False, err_msg  # noqa
        assert yahoo.is_alive is False, err_msg  # noqa

        print(google.driver.title, google.title)
        assert google.driver.title == google.title, err_msg  # noqa
