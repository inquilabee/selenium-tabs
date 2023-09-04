from simpleselenium.browser import Browser


def test_run_without_exception():
    err_msg = "Something went wrong. Report immediately."

    with Browser(name="Chrome", implicit_wait=10, headless=True) as browser:
        google = browser.open("https://google.com")
        yahoo = browser.open("https://yahoo.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")

        yahoo.scroll_down(times=5)
        yahoo.scroll_up(times=5)
        yahoo.scroll(times=5)

        assert len(browser.tabs) == 4, err_msg  # noqa

        assert yahoo == browser.current_tab, err_msg  # noqa

        assert google == browser.first_tab, err_msg  # noqa

        assert duck_duck == browser.last_tab, err_msg  # noqa

        browser.last_tab.switch()
        assert browser.current_tab == duck_duck, err_msg  # noqa

        google.title and google.url  # noqa

        assert google.is_active is True, err_msg  # noqa
        assert google.is_alive is True, err_msg  # noqa

        assert google.is_alive is True, err_msg  # noqa

        browser.close_tab(bing)

        assert bing.is_alive is False, err_msg  # noqa
        assert bing.is_active is False, err_msg  # noqa
        assert bing not in browser.tabs, err_msg  # noqa

        assert duck_duck == browser.current_tab, err_msg  # noqa
        assert duck_duck.is_alive, err_msg  # noqa
        assert duck_duck.is_active, err_msg  # noqa

        yahoo.switch()

        assert yahoo == browser.current_tab, err_msg  # noqa
        assert yahoo.is_alive, err_msg  # noqa
        assert yahoo.is_active, err_msg  # noqa
        assert duck_duck.is_active is False, err_msg  # noqa

        google.switch()

        assert google == browser.current_tab, err_msg  # noqa

        browser.close_tab(yahoo)

        assert yahoo.is_active is False, err_msg  # noqa
        assert yahoo.is_alive is False, err_msg  # noqa

        assert google.driver.title == google.title, err_msg  # noqa
