from seleniumtabs import Browser, settings

logger = settings.getLogger(__name__)

logger.info("Test Starts")


def test_run_without_exception():
    err_msg = "Something went wrong. Report immediately."

    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        logger.info("Test Starts")
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

        browser.last_tab.switch()  # type: ignore
        assert browser.current_tab == duck_duck, err_msg

        assert google.title and google.url

        assert google.is_active is True, err_msg
        assert google.is_alive is True, err_msg

        assert google.is_alive is True, err_msg

        browser.close_tab(bing)

        assert bing.is_alive is False, err_msg
        assert bing.is_active is False, err_msg
        assert bing not in browser.tabs, err_msg

        assert duck_duck == browser.current_tab, err_msg
        assert duck_duck.is_alive, err_msg
        assert duck_duck.is_active, err_msg

        yahoo.switch()

        assert yahoo == browser.current_tab, err_msg
        assert yahoo.is_alive, err_msg
        assert yahoo.is_active, err_msg
        assert duck_duck.is_active is False, err_msg

        google.switch()

        assert google == browser.current_tab, err_msg

        browser.close_tab(yahoo)

        assert yahoo.is_active is False, err_msg
        assert yahoo.is_alive is False, err_msg

        assert google.driver.title == google.title, err_msg


def test_css_selector_functionality():
    """Test CSS selector functionality on Yahoo homepage"""
    err_msg = "CSS selector test failed"

    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        yahoo = browser.open("https://yahoo.com")

        # Test basic element selection
        search_box = yahoo.css("input#ybar-sbq")
        assert len(search_box) == 1, err_msg
        assert search_box[0].get_attribute("type") == "text", err_msg

        # Test multiple elements selection
        nav_links = yahoo.css("nav a")
        assert len(nav_links) > 0, err_msg
        assert all(link.get_attribute("href") for link in nav_links), err_msg

        # Test class-based selection
        logo = yahoo.css("#ybar-logo")
        assert len(logo) == 1, err_msg
        assert "yahoo" in logo[0].get_attribute("href").lower(), err_msg

        # Test attribute-based selection
        search_buttons = yahoo.css("button[type='submit']")
        assert len(search_buttons) > 0, err_msg
        assert search_buttons[0].get_attribute("type") == "submit", err_msg

        # Test non-existent selector
        non_existent = yahoo.css(".this-class-does-not-exist")
        assert len(non_existent) == 0, err_msg


def test_css_selector_chaining():
    """Test the chaining capability of CSS selectors"""
    err_msg = "CSS selector chaining test failed"

    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        yahoo = browser.open("https://yahoo.com")

        # Test main content chaining
        main_content = yahoo.css("main")
        assert len(main_content) == 1, err_msg
        story_links = main_content[0].css("a")
        assert len(story_links) > 0, err_msg
        assert all(link.get_attribute("href") for link in story_links), err_msg


def test_pyquery_functionality():
    """Test PyQuery functionality"""
    err_msg = "PyQuery test failed"

    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        yahoo = browser.open("https://yahoo.com")

        # Test items() functionality
        nav_links = yahoo.pq("nav")
        assert len([i for i in nav_links.items("a")]) > 0, err_msg

        links = yahoo.pq("nav a")
        assert len([i for i in links.items()]) > 0, err_msg

        assert list(nav_links.items("a")) == list(nav_links("a").items()), err_msg

        # Test find() functionality
        assert len(yahoo.pq("nav").find("a")) > 0, err_msg
        assert len(yahoo.pq("body").find("div")) > 0, err_msg

        # Test parent/children functionality
        nav = yahoo.pq("nav")
        assert len(nav.children()) > 0, err_msg
        parent = nav.parent()
        assert parent.is_("div"), err_msg  # nav's parent is a div in Yahoo's current structure

        # Test attr() functionality
        logo = yahoo.pq("#ybar-logo")
        href = logo.attr("href")
        assert isinstance(href, str) and "yahoo" in href.lower(), err_msg

        # Test text() functionality
        title = yahoo.pq("title")
        title_text = title.text()
        assert isinstance(title_text, str) and len(title_text) > 0, err_msg
        assert "Yahoo" in title_text, err_msg

        # Test html() functionality
        body = yahoo.pq("body")
        body_html = body.html()
        assert isinstance(body_html, str) and len(body_html) > 0, err_msg
        assert "<div" in body_html, err_msg

        # Test basic integration - can we get page content?
        assert len(yahoo.pq("body")) > 0, err_msg
        assert len(yahoo.pq("title")) > 0, err_msg
