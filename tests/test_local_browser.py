from selenium.webdriver.common.by import By


def local_url(base_url: str, page: str = "basic.html") -> str:
    return f"{base_url}/{page}"


def test_browser_manages_local_tabs(browser, fixture_server):
    first = browser.open(local_url(fixture_server), wait=0, wait_for_redirect=0, timeout=5)
    second = browser.open(f"{local_url(fixture_server)}#second", wait=0, wait_for_redirect=0, timeout=5)

    assert len(browser.tabs) == 2
    assert browser.first_tab == first
    assert browser.last_tab == second
    assert browser.current_tab == second

    first.switch()
    assert browser.current_tab == first
    assert first.is_active is True
    assert second.is_active is False
    assert "Selenium Tabs Fixture" in first.title
    assert "/basic.html" in first.url

    browser.close_tab(second)

    assert second.is_alive is False
    assert second not in browser.tabs
    assert browser.current_tab == first


def test_selectors_pyquery_and_javascript_use_local_fixture(browser, fixture_server):
    tab = browser.open(local_url(fixture_server), wait=0, wait_for_redirect=0, timeout=5)

    search_box = tab.css("input#search-input")
    assert len(search_box) == 1
    assert search_box[0].get_attribute("value") == "tabs"

    main_content = tab.css("main")
    assert len(main_content) == 1
    card_links = main_content[0].css(".card a")
    assert [link.text for link in card_links] == ["Read first", "Read second"]

    submit_button = tab.find_element(By.ID, "submit-button")
    assert submit_button is not None
    assert tab.get_attribute(submit_button, "type") == "submit"

    nav_links = list(tab.pq("nav a").items())
    assert [link.text() for link in nav_links] == ["Home", "Docs", "Contact"]
    assert tab.run_js("return document.querySelectorAll('.card').length") == 2


def test_scroll_helpers_run_against_local_fixture(browser, fixture_server):
    tab = browser.open(local_url(fixture_server), wait=0, wait_for_redirect=0, timeout=5)

    assert tab.page_height > 1000

    tab.scroll_down(times=1, clicks=100, wait=0)
    tab.scroll_up(times=1, clicks=100, wait=0)
    tab.scroll_to_bottom(wait=0)

    assert tab.is_alive is True


def test_task_scheduler_executes_and_cancels_local_tab_task(browser, fixture_server):
    tab = browser.open(local_url(fixture_server), wait=0, wait_for_redirect=0, timeout=5)
    titles_seen = []

    def collect_title(tab):
        titles_seen.append(tab.title)

    tab.schedule_task(collect_title, period=1)
    browser.execute_task(max_time=1.4, sleep_time=0.1)

    assert titles_seen == ["Selenium Tabs Fixture"]
    assert browser.task_scheduler.is_task_running("collect_title") is True

    assert browser.task_scheduler.cancel_task("collect_title") is True
    assert browser.task_scheduler.is_task_running("collect_title") is False
