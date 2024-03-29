# Selenium Tabs: Enhanced Tab Management for Selenium

Simplify your web automation tasks with **Selenium Tabs**, a Python package that takes Selenium to the next level with streamlined tab management and additional features.

### Installation

Install **Selenium Tabs** from PyPI with ease:

```bash
pip install seleniumtabs
```

### Core Idea

In **Selenium Tabs**, a `browser` contains multiple `tabs`, enabling you to interact with web pages more efficiently. You can perform various actions on both `Tab` and `Browser` objects, making web automation a breeze.

**Actions/Activities on `Tab` Objects:**
- Check tab status (open/closed)
- Switch to a specific tab
- Close a tab
- Access page source, title, and headings
- Select elements and perform actions using Jquery
- Perform actions on a specific tab (e.g., click, scroll, close)
- CSS selection made easy

**Actions/Activities on `Browser` Objects:**
- Open new tabs with URLs
- Retrieve a list of open tabs
- Switch to a specific tab (first, last, or any)
- Close a tab
- Close the entire browser

### Working with Driver Objects

A `driver` object is available on any `Tab` object,
allowing you to access the browser/driver object
and use Selenium methods when needed without making explicit switches to a specific tab.

### Features

**Selenium Tabs** offers a range of features to enhance your web automation tasks:
- Effortless tab management
- Seamless tab switching
- Real-time tab status tracking
- Convenient tab closure
- Built-in functions for scrolling, clicking, waiting for conditions, finding and more
- Access to the underlying Selenium `driver` object for advanced usage
- Access `driver` methods directly on tabs
- Automatic User agent selection based on set browser
- Basic steps to avoid getting flagged as an automation script by websites
- Use the all-powerful `pyquery` object access on each tab
- Execute jquery functions using `.jq` or `.jquery` attributes

### Usage

To get started with **Selenium Tabs**, create a `Browser` object and open tabs using the `open` method:

#### Browser

Create a `Browser` object, specifying the browser name (e.g. "Chrome" or "FireFox").
The project automatically downloads drivers.

```python
from seleniumtabs import Browser, Tab


with Browser(name="Chrome", implicit_wait=10) as browser:
    google = browser.open("https://google.com")
    yahoo = browser.open("https://yahoo.com")
    bing = browser.open("https://bing.com")
    duck_duck = browser.open("https://duckduckgo.com/")

    # Scroll on the page (example)
    yahoo.scroll(times=2)
    yahoo.scroll_to_bottom()

    # Working with tabs
    for tab in browser.tabs:
        print(tab)

    print(browser.tabs)
    print(browser.current_tab)

    # Selecting elements with JQuery (using browserjquery package)
    print(yahoo.jq("a"))

    # Selecting using CSS Selectors (no JQuery needed)
    for item in yahoo.css(".stream-items"):
        for a in item.css("a"):
            print(a, a.text)

    # Some `Tab` attributes/properties
    print(google.title)
    print(google.url)
    print(google.page_source)

    # Closing a tab
    bing.close() # Or browser.close_tab(bing)

    # Switching to a tab
    yahoo.switch()
    google.switch()

    # Accessing the driver object
    print(google.driver.title, google.title) # Should output same value

    # Directly access driver methods and attributes
    print(google.current_window_handle, google.tab_handle)
    google.refresh()

    # PyQuery
    print(google.pyquery.text())
    print(google.pq.size())
```

### TODO

- Complete documentation
