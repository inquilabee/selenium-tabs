### Simple Selenium

Selenium with Tab Management

<small> With all the already available flexibility and features of Selenium </small>

### Installation

Install from PyPI

```bash
pip install simpleselenium
```

### Core Idea

A `browser` has many `tabs`.

Action/activity on `Tab` object
- Check if the tab is alive (i.e. it has not been closed)
- Switch to a tab
- See/obtain page source, title and headings
- inject JQuery and select elements
- work on a specific tab
- click elements
- scroll (up or down)
- infinite scroll
- CSS selection made easy
- ... many more

Action/activity on `Browser` object
- Open a new tab with url
- Get a list of open tabs
- Get active tab
- Switch to a tab of the browser (first, last or any one).
- close a tab
- Close the browser

### Working with driver objects

`driver` object available on any `Tab` object.

### Features

Some basic features are being listed below (also see the `Usage` section below):

- easy management of different tabs
- switching to a tab is super easy
- know if a tab is active (current tab) or alive
- closing a tab is easy as `browser.close_tab(tab_object)`
- Several (built-in) functions
    - `tab.infinite_scroll()`
    - `tab.scroll()`
    - `tab.scroll_to_bottom()`
    - `tab.click(element_on_page)`
    - `tab.switch()` to focus on tab i.e. make it the active tab
- Can't find a way to use usual selenium methods? Use `Tab.driver` object to access the browser/driver object and use
  accordingly

### Usage

The best way to getting started with the package is to use the `Browser` object to start a browser and call `open`
method off it which returns a Tab object.

#### Browser

```python

from simpleselenium import Browser, Tab

# The `name` argument is one of "Chrome" or "FireFox".
# The project has been configured to auto-download drivers.


    with Browser(name="Chrome", implicit_wait=10) as browser:
        google: Tab = browser.open("https://google.com")
        yahoo = browser.open("https://yahoo.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")

        # Scroll on the page

        # yahoo.scroll_to_bottom()
        # yahoo.scroll_down(times=2)
        # yahoo.scroll_up(times=2)
        # yahoo.scroll(times=2, wait=5)

        # Working with tabs -- loop through it, access using index and so on

        assert len(browser.tabs) == 4, err_msg  # noqa
        assert google in browser.tabs, err_msg  # noqa
        assert browser.tabs[0] == google, err_msg  # noqa

        for tab in browser.tabs:
            print(tab)

        print(browser.tabs)
        print(browser.current_tab)

        # Selecting elements with JQuery

        print(yahoo.jq("a"))
        print(yahoo.jquery("a"))  # same as above

        print(yahoo.jquery.find(".streams"))

        for item in yahoo.jquery.execute("""return $(".stream-items a");"""):
            result = yahoo.jquery.query(
                script="""
                        return $(arguments[0]).text();
                    """,
                element=item,
            )

            print(result)

        # Selecting using CSS Selectors (no JQuery needed)

        for item in yahoo.css(".stream-items"):
            for a in item.css("a"):
                print(a, a.text)

        assert yahoo == browser.current_tab, err_msg  # noqa

        print(browser.first_tab)
        assert google == browser.first_tab, err_msg  # noqa

        print(browser.last_tab)
        assert duck_duck == browser.last_tab, err_msg  # noqa

        print(browser.last_tab.switch())
        assert browser.current_tab == duck_duck, err_msg  # noqa

        # Some `Tab` attributes/properties

        print(google.title)
        print(google.url)

        print(google.page_source)
        print(google.page_html)

        print(google.page_height)
        print(google.user_agent)
        print(google.is_active)
        print(google.is_alive)

        # Closing a tab

        browser.close_tab(bing)
        print(browser.tabs)

        print(browser.current_tab)

        # Switching to a tab

        yahoo.switch()

        print(browser.current_tab)

        google.switch()

        print(browser.current_tab)

        browser.close_tab(yahoo)

        print(yahoo.is_alive)
        print(yahoo.is_active)

        # Accessing the driver object

        print(google.driver.title, google.title)
        assert google.driver.title == google.title, err_msg  # noqa

        # Query using the powerful pyquery library

        d = yahoo.pyquery  # noqa
```

### TODO

- Complete documentation
