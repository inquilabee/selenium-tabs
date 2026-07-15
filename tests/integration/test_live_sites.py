import time

import pytest
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.integration


def test_run_without_exception(browser):
    err_msg = "Something went wrong. Report immediately."

    google = browser.open("https://google.com")
    yahoo = browser.open("https://yahoo.com")
    bing = browser.open("https://bing.com")
    duck_duck = browser.open("https://duckduckgo.com/")

    yahoo.scroll_down(times=5)
    yahoo.scroll_up(times=5)
    yahoo.scroll(times=5)

    assert len(browser.tabs) == 4, err_msg
    assert yahoo == browser.current_tab, err_msg
    assert google == browser.first_tab, err_msg
    assert duck_duck == browser.last_tab, err_msg

    browser.last_tab.switch()
    assert browser.current_tab == duck_duck, err_msg
    assert google.title and google.url
    assert google.is_active is True, err_msg
    assert google.is_alive is True, err_msg

    browser.close_tab(bing)

    assert bing.is_alive is False, err_msg
    assert bing.is_active is False, err_msg
    assert bing not in browser.tabs, err_msg


def test_css_selector_functionality(browser):
    err_msg = "CSS selector test failed"
    yahoo = browser.open("https://yahoo.com")

    search_box = yahoo.css("input#ybar-sbq")
    assert len(search_box) == 1, err_msg
    assert search_box[0].get_attribute("type") == "text", err_msg

    nav_links = yahoo.css("nav a")
    assert len(nav_links) > 0, err_msg
    assert all(link.get_attribute("href") for link in nav_links), err_msg

    logo = yahoo.css("#ybar-logo")
    assert len(logo) == 1, err_msg
    assert "yahoo" in logo[0].get_attribute("href").lower(), err_msg


def test_pyquery_functionality(browser):
    err_msg = "PyQuery test failed"
    yahoo = browser.open("https://yahoo.com")

    nav_links = yahoo.pq("nav")
    assert len(list(nav_links.items("a"))) > 0, err_msg
    assert list(nav_links.items("a")) == list(nav_links("a").items()), err_msg
    assert len(yahoo.pq("nav").find("a")) > 0, err_msg
    assert len(yahoo.pq("body").find("div")) > 0, err_msg

    logo = yahoo.pq("#ybar-logo")
    href = logo.attr("href")
    assert isinstance(href, str) and "yahoo" in href.lower(), err_msg
    assert "Yahoo" in yahoo.pq("title").text(), err_msg


def test_task_scheduling_with_time_website(browser):
    tab = browser.open("https://time.is")
    times_checked = []

    def check_time(tab):
        current_time = tab.find_element(By.ID, "clock").text
        times_checked.append(current_time)

    tab.schedule_task(check_time, period=2)
    browser.execute_task(max_time=6, sleep_time=0.5)

    assert times_checked, "Task should have executed at least once"
    assert len(set(times_checked)) > 1, "Times should be different as website updates"


def test_task_cancellation_with_time_website(browser):
    tab = browser.open("https://time.is")
    times_checked = []

    def check_time(tab):
        current_time = tab.find_element(By.ID, "clock").text
        times_checked.append(current_time)

    tab.schedule_task(check_time, period=1)
    browser.execute_task(max_time=3, sleep_time=0.5)
    time.sleep(2)

    browser.task_scheduler.cancel_task("check_time")
    time.sleep(2)

    assert len(times_checked) <= 4, "Task should have been cancelled and not executed many times"
