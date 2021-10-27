from simpleselenium import Browser


def test_run_without_exception():
    chrome_driver = r"/Users/dayhatt/workspace/drivers/chromedriver"

    with Browser(name="Chrome", driver_path=chrome_driver, implicit_wait=10) as browser:
        google = browser.open("https://google.com")
        yahoo = browser.open("https://yahoo.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")  # noqa

        assert len(browser.get_all_tabs()) == 4

        browser.close_tab(bing)

        assert len(browser.get_all_tabs()) == 3

        yahoo.switch()

        assert browser.get_current_tab().tab_handle == yahoo.tab_handle
        assert yahoo.is_alive
        assert yahoo.is_active
        assert bing.is_alive is False
        assert bing.is_active is False

        assert google.driver.title == google.title
