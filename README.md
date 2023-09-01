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
- work on a specific tab (click elements, scroll and so on.)
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
- Can't find a way to use usual selenium methods? Use `tab.driver` object to access the browser/driver object and use
  accordingly

### Usage

The best way to getting started with the package is to use the `Browser` object to start a browser and call `open`
method off it which returns a Tab object.

#### Browser

```python

from simpleselenium import Browser, Tab

# name is one of "Chrome" or "FireFox"
# driver path is not required in most cases

with Browser(name="Chrome", driver_path=None, implicit_wait=10) as browser:
        google: Tab = browser.open("https://google.com") # a `Tab` object
        yahoo = browser.open("https://yahoo.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")

        yahoo.scroll_up(times=5)
        yahoo.scroll_down(times=10)

        print(browser.tabs)
        print(browser.current_tab)
        print(browser.first_tab)
        print(browser.last_tab)

        print(browser.last_tab.switch())

        print(google.page_source)
        print(google.title)
        print(google.url)
        print(google.is_active)
        print(google.is_alive)

        browser.close_tab(bing)
        print(browser.tabs)

        print(browser.current_tab)

        yahoo.switch()
        print(browser.current_tab)
        google.switch()

        print(browser.current_tab)

        browser.close_tab(yahoo)

        print(yahoo.is_alive)
        print(yahoo.is_active)

        print(google.driver.title, google.title)
        print(google.driver.title == google.title)
```

### TODO

- Complete documentation
