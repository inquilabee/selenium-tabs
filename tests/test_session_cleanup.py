from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import seleniumtabs.browser as browser_module
from seleniumtabs.session import Session


def test_session_destructor_ignores_missing_driver_after_failed_initialization():
    session = Session.__new__(Session)

    assert session.__del__() is None


def test_session_builds_chrome_and_firefox_options_without_launching_driver():
    for browser_name, expected_type in (("Chrome", ChromeOptions), ("FireFox", FirefoxOptions)):
        session = Session.__new__(Session)
        session.browser = browser_name
        session.headless = True
        session.user_agent = "seleniumtabs-test-agent"

        assert isinstance(session._get_driver_options(), expected_type)


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
