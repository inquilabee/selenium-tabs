import importlib
import logging
import sys

import pytest
from selenium.webdriver.common.by import By

from seleniumtabs.utils import core, urls
from seleniumtabs.wait import duration_to_type, humanized_wait, humanized_wait_duration


def test_get_domain_uses_tldextract_for_normal_urls():
    assert urls.get_domain("https://www.example.com/path") == "example"


def test_get_domain_falls_back_to_urlparse_when_tldextract_fails(monkeypatch):
    def raise_value_error(url):
        raise ValueError(url)

    monkeypatch.setattr(urls.tldextract, "extract", raise_value_error)

    assert urls.get_domain("https://subdomain.example.com/path") == "subdomain.example.com"


def test_humanized_wait_duration_uses_random_components(monkeypatch):
    monkeypatch.setattr("seleniumtabs.wait.random.random", lambda: 0.25)
    monkeypatch.setattr("seleniumtabs.wait.random.uniform", lambda min_time, max_time: min_time + max_time)

    assert humanized_wait_duration(1, max_time=2) == 3.25


def test_humanized_wait_validates_inputs():
    with pytest.raises(ValueError, match="min_wait"):
        humanized_wait(-1)

    with pytest.raises(ValueError, match="max_wait"):
        humanized_wait(2, max_wait=1)

    with pytest.raises(ValueError, match="multiply_factor"):
        humanized_wait(1, multiply_factor=0)

    with pytest.raises(ValueError, match="wait_addendum"):
        humanized_wait(1, wait_addendum=-1)


def test_humanized_wait_sleeps_for_calculated_duration(monkeypatch):
    sleeps = []
    monkeypatch.setattr("seleniumtabs.wait.humanized_wait_duration", lambda **kwargs: 1.5)
    monkeypatch.setattr("seleniumtabs.wait.time.sleep", sleeps.append)

    humanized_wait(1)

    assert sleeps == [1.5]


def test_duration_to_type_uses_word_count_and_variation(monkeypatch):
    monkeypatch.setattr("seleniumtabs.wait.random.uniform", lambda min_value, max_value: 1.0)

    assert duration_to_type("hello world", speed=60) == 2.2


def test_find_parent_element_uses_parent_xpath():
    class Element:
        def find_element(self, by, value):
            assert by == By.XPATH
            assert value == ".."
            return "parent"

    assert core.find_parent_element(Element()) == "parent"


def test_importing_settings_does_not_configure_logging_or_create_logs_dir(tmp_path, monkeypatch):
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    previous_settings = sys.modules.pop("seleniumtabs.settings", None)

    for handler in original_handlers:
        root_logger.removeHandler(handler)

    monkeypatch.chdir(tmp_path)

    try:
        importlib.import_module("seleniumtabs.settings")

        assert root_logger.handlers == []
        assert not (tmp_path / "logs").exists()
    finally:
        sys.modules.pop("seleniumtabs.settings", None)
        if previous_settings is not None:
            sys.modules["seleniumtabs.settings"] = previous_settings

        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
            handler.close()
        for handler in original_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(original_level)
