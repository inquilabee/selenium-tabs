import pytest
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import seleniumtabs.browser as browser_module
from seleniumtabs.session import Session


def test_session_destructor_ignores_missing_driver_after_failed_initialization():
    session = Session.__new__(Session)

    assert session.__del__() is None


def test_session_destructor_suppresses_close_errors():
    session = Session.__new__(Session)

    def fail_close():
        raise RuntimeError("close failed")

    session.close = fail_close

    assert session.__del__() is None


def test_session_builds_chrome_and_firefox_options_without_launching_driver():
    for browser_name, expected_type in (("Chrome", ChromeOptions), ("FireFox", FirefoxOptions)):
        session = Session.__new__(Session)
        session.browser = browser_name
        session.headless = True
        session.user_agent = "seleniumtabs-test-agent"
        session._options_factory = None

        assert isinstance(session._get_driver_options(), expected_type)


def test_session_accepts_driver_and_options_factories_without_launching_browser():
    calls = {}

    class FakeDriver:
        capabilities = {"browserName": "fake", "browserVersion": "1", "platformName": "test"}

        def __init__(self):
            self.implicit_wait = None
            self.page_load_timeout = None
            self.closed = False

        def implicitly_wait(self, value):
            self.implicit_wait = value

        def set_page_load_timeout(self, value):
            self.page_load_timeout = value

        def quit(self):
            self.closed = True

    fake_driver = FakeDriver()

    def options_factory(browser_name):
        calls["options_browser"] = browser_name
        return ChromeOptions()

    def driver_factory(options):
        calls["driver_options"] = options
        return fake_driver

    session = Session(
        "Chrome",
        implicit_wait=4,
        user_agent="seleniumtabs-test-agent",
        full_screen=False,
        page_load_timeout=9,
        options_factory=options_factory,
        driver_factory=driver_factory,
    )

    try:
        assert session.driver is fake_driver
        assert calls["options_browser"] == "Chrome"
        assert calls["driver_options"] is not None
        assert fake_driver.implicit_wait == 4
        assert fake_driver.page_load_timeout == 9
    finally:
        session.close()


def test_browser_forwards_driver_and_options_factories_to_session(monkeypatch):
    created_session = {}

    def driver_factory(options):
        return options

    def options_factory(browser_name):
        return browser_name

    class RecordingSession:
        def __init__(
            self,
            browser_name,
            implicit_wait,
            user_agent,
            headless=False,
            full_screen=True,
            page_load_timeout=60,
            driver_factory=None,
            options_factory=None,
        ):
            created_session.update(
                {
                    "driver_factory": driver_factory,
                    "options_factory": options_factory,
                }
            )

        def close(self):
            created_session["closed"] = True

    monkeypatch.setattr(browser_module, "Session", RecordingSession)

    browser = browser_module.Browser(name="Chrome", driver_factory=driver_factory, options_factory=options_factory)
    browser.close()

    assert created_session == {
        "driver_factory": driver_factory,
        "options_factory": options_factory,
        "closed": True,
    }


def test_browser_forwards_page_load_timeout_to_session(monkeypatch):
    created_session = {}

    class RecordingSession:
        def __init__(
            self,
            browser_name,
            implicit_wait,
            user_agent,
            headless=False,
            full_screen=True,
            page_load_timeout=60,
        ):
            created_session.update(
                {
                    "browser_name": browser_name,
                    "implicit_wait": implicit_wait,
                    "user_agent": user_agent,
                    "headless": headless,
                    "full_screen": full_screen,
                    "page_load_timeout": page_load_timeout,
                }
            )

        def close(self):
            created_session["closed"] = True

    monkeypatch.setattr(browser_module, "Session", RecordingSession)

    browser = browser_module.Browser(name="Chrome", implicit_wait=2, page_load_timeout=7)
    browser.close()

    assert created_session == {
        "browser_name": "Chrome",
        "implicit_wait": 2,
        "user_agent": None,
        "headless": False,
        "full_screen": True,
        "page_load_timeout": 7,
        "closed": True,
    }


def test_browser_instances_have_independent_task_schedulers(monkeypatch):
    class RecordingSession:
        def __init__(
            self,
            browser_name,
            implicit_wait,
            user_agent,
            headless=False,
            full_screen=True,
            page_load_timeout=60,
        ):
            self.closed = False

        def close(self):
            self.closed = True

    monkeypatch.setattr(browser_module, "Session", RecordingSession)

    first = browser_module.Browser(name="Chrome")
    second = browser_module.Browser(name="Chrome")
    try:
        assert first.task_scheduler is not second.task_scheduler
    finally:
        first.close()
        second.close()


def test_browser_close_is_idempotent(monkeypatch):
    close_calls = []

    class RecordingSession:
        def __init__(
            self,
            browser_name,
            implicit_wait,
            user_agent,
            headless=False,
            full_screen=True,
            page_load_timeout=60,
        ):
            return None

        def close(self):
            close_calls.append("closed")

    monkeypatch.setattr(browser_module, "Session", RecordingSession)

    browser = browser_module.Browser(name="Chrome")
    browser.close()
    browser.close()

    assert close_calls == ["closed"]


def test_browser_destructor_suppresses_close_errors():
    browser = browser_module.Browser.__new__(browser_module.Browser)

    def fail_close():
        raise RuntimeError("close failed")

    browser.close = fail_close

    assert browser.__del__() is None


def test_browser_close_removes_registry_entry_when_session_close_fails(monkeypatch):
    class FailingSession:
        def __init__(
            self,
            browser_name,
            implicit_wait,
            user_agent,
            headless=False,
            full_screen=True,
            page_load_timeout=60,
        ):
            return None

        def close(self):
            raise RuntimeError("close failed")

    monkeypatch.setattr(browser_module, "Session", FailingSession)

    browser = browser_module.Browser(name="Chrome")
    try:
        assert browser in browser_module.browser_sessions.browser_sessions

        with pytest.raises(RuntimeError, match="close failed"):
            browser.close()

        assert browser not in browser_module.browser_sessions.browser_sessions
    finally:
        browser_module.browser_sessions.remove_browser(browser)
