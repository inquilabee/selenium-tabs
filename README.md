### Simple Selenium

The aim of this package is to quickly get started with working with selenium for simple browser automation tasks.

### Usage

The best way to getting started with the package is to use the `Browser` object to start a browser and call `open`
method off it which returns a Tab object.

#### Browser

```python
import time  # just to slow down stuffs and see things for testing
from simpleselenium import Browser

chrome_driver = r"/path/to/chromedriver"

with Browser(name="Chrome", driver_path=chrome_driver, implicit_wait=10) as browser:
    google = browser.open("https://google.com")
    yahoo = browser.open("https://yahoo.com")
    bing = browser.open("https://bing.com")
    duck_duck = browser.open("https://duckduckgo.com/")

    print(yahoo)  # A Tab Object
    print(yahoo.is_alive)
    print(yahoo.is_active)
    print(dir(yahoo))  # All methods and attributes of Tab Objects

    print(browser.get_all_tabs())  # List of tab objects

    print(browser.tabs.all())
    print(browser.tabs)  # TabManager object
    print(dir(browser.tabs))  # All methods and attributes of TabManager Objects

    browser.close_tab(bing)  # close a browser tab
    print(browser.tabs.all())

    print(browser.get_current_tab())  # current tab
    time.sleep(5)

    yahoo.switch()  # switch/focus/tap to/on `yahoo` tab
    print(browser.get_current_tab())
    time.sleep(5)

    google.switch()
    print(browser.get_current_tab())
    time.sleep(5)

    browser.close_tab(yahoo)
    time.sleep(5)

    print(google.driver)  # Usual selenium driver object which can be worked upon

    print(google.driver.title, google.title)

    print(google.scroll_to_bottom())
    print(google.is_active)
    print(google.is_alive)
    print(bing.is_alive)  # False, it has been deleted.

    print(browser.get_all_tabs())
```
