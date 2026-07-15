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
