import pytest

from seleniumtabs.exceptions import SeleniumRequestException
from seleniumtabs.tabs import Tab


class ClosedSession:
    window_handles = []


def test_dead_tab_driver_access_raises_request_exception_without_recursing():
    tab = Tab(ClosedSession(), "missing")

    with pytest.raises(SeleniumRequestException, match="Current window is dead"):
        _driver = tab.driver


def test_element_center_returns_midpoint_from_location_and_size():
    class Element:
        location = {"x": 10, "y": 20}
        size = {"width": 30, "height": 40}

    assert Tab.element_center(Element()) == {"x": 25.0, "y": 40.0}


def test_tab_close_uses_explicit_owner_callback(monkeypatch):
    closed_tabs = []
    tab = Tab(ClosedSession(), "missing", close_tab=closed_tabs.append)

    def fail_global_close(tab):
        raise AssertionError("Tab.close() should not use the global browser registry")

    monkeypatch.setattr("seleniumtabs.tabs.browser_sessions.close_tab", fail_global_close)

    assert tab.close() is None
    assert closed_tabs == [tab]


def test_unowned_tab_close_raises_request_exception(monkeypatch):
    tab = Tab(ClosedSession(), "missing")
    monkeypatch.setattr("seleniumtabs.tabs.browser_sessions.get_browser_for_tab", lambda tab: None)

    with pytest.raises(SeleniumRequestException, match="Tab is not owned"):
        tab.close()
