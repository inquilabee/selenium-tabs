# Simple Selenium: Enhanced Tab Management for Selenium

Simplify your web automation tasks with **Simple Selenium**, a Python package that takes Selenium to the next level with streamlined tab management and additional features.

### Installation

Install **Simple Selenium** from PyPI with ease:

```bash
pip install simpleselenium
```

### Core Idea

In **Simple Selenium**, a `browser` contains multiple `tabs`, enabling you to interact with web pages more efficiently. You can perform various actions on both `Tab` and `Browser` objects, making web automation a breeze.

**Actions/Activities on `Tab` Objects:**
- Check tab status (open/closed)
- Switch to a specific tab
- Access page source, title, and headings
- Inject jQuery and select elements
- Perform actions on a specific tab (e.g., click, scroll)
- CSS selection made easy

**Actions/Activities on `Browser` Objects:**
- Open new tabs with URLs
- Retrieve a list of open tabs
- Switch to a specific tab (first, last, or any)
- Close a tab
- Close the entire browser

### Working with Driver Objects

A `driver` object is available on any `Tab` object, allowing you to access the browser/driver object and use Selenium methods when needed.

### Features

**Simple Selenium** offers a range of features to enhance your web automation tasks:
- Effortless tab management
- Seamless tab switching
- Real-time tab status tracking
- Convenient tab closure
- Built-in functions for scrolling, clicking, and more
- Access to the underlying Selenium `driver` object for advanced usage

### Usage

To get started with **Simple Selenium**, create a `Browser` object and open tabs using the `open` method:

#### Browser

```python
from simpleselenium import Browser, Tab

# Create a `Browser` object, specifying the browser name (e.g., "Chrome").
# The project automatically downloads drivers.

with Browser(name="Chrome", implicit_wait=10) as browser:
    google: Tab = browser.open("https://google.com")
    yahoo = browser.open("https://yahoo.com")
    bing = browser.open("https://bing.com")
    duck_duck = browser.open("https://duckduckgo.com/")

    # Scroll on the page (example)
    yahoo.scroll_to_bottom()

    # Working with tabs
    assert len(browser.tabs) == 4
    assert google in browser.tabs
    assert browser.tabs[0] == google

    for tab in browser.tabs:
        print(tab)

    print(browser.tabs)
    print(browser.current_tab)

    # Selecting elements with JQuery (using Browserjquery package)
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
    browser.close_tab(bing)

    # Switching to a tab
    yahoo.switch()
    google.switch()

    # Accessing the driver object
    print(google.driver.title, google.title)
```

### TODO

- Complete documentation
