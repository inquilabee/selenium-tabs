# Selenium Tabs

Selenium Tabs is a Python package for developers who want Selenium automation without constantly juggling window handles. It gives you a `Browser` object, `Tab` objects, and a small set of helpers for page inspection, interaction, scrolling, waiting, JavaScript, and recurring tab tasks.

Use it when you want to script real browser work in Python: open a few tabs, collect data, click through pages, monitor changing content, or keep a browser session running while tasks execute on a schedule.

## Why Use It

- Tabs are first-class: `browser.open(...)` returns a `Tab`, and you can switch, close, list, and inspect tabs directly.
- Selenium is still there: use `tab.driver` whenever you need the raw WebDriver API.
- Page querying is convenient: use CSS selectors, jQuery-style access, or PyQuery snapshots.
- Common browser actions are built in: click, scroll, wait, run JavaScript, and read element attributes.
- Slow pages are easier to handle: navigation supports page load timeouts and partial-load fallback.
- Long-running automation is supported: schedule recurring work against specific tabs.
- Driver setup is simple: Chrome and Firefox drivers are managed through `webdriver-manager`.

## Installation

```bash
pip install seleniumtabs
```

## Requirements

- Python 3.13+
- Chrome or Firefox installed locally

Use `"Chrome"` or `"FireFox"` as the browser name when creating a `Browser`.

## Quick Start

```python
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True, implicit_wait=5) as browser:
    search = browser.open("https://example.com")
    docs = browser.open("https://example.org")

    print(search.title)
    print(docs.url)

    search.switch()
    print(search.is_active)

    docs.close()
```

## Common Tasks

### Manage Tabs

```python
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    first = browser.open("https://example.com")
    second = browser.open("https://example.org")

    print(browser.first_tab)   # first opened tab
    print(browser.last_tab)    # latest opened tab
    print(browser.current_tab) # active tab

    first.switch()
    second.close()
```

### Find Elements

```python
from selenium.webdriver.common.by import By
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    links = tab.css("a")
    print([link.text for link in links])

    button = tab.find_element(By.CSS_SELECTOR, "button[type='submit']")
    if button:
        print(button.text)
```

### Parse HTML With PyQuery

```python
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    page = tab.pyquery
    print(page("title").text())

    for link in page("a").items():
        print(link.text(), link.attr("href"))
```

### Query the Live DOM With jQuery Syntax

```python
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    for element in tab.jq("a"):
        print(element.text)
```

### Click, Scroll, and Run JavaScript

```python
from selenium.webdriver.common.by import By
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    button = tab.find_element(By.CSS_SELECTOR, "button")
    if button:
        tab.click(button)

    tab.scroll_down(times=2, clicks=100, wait=1)
    tab.scroll_to_bottom(wait=1)

    title = tab.run_js("return document.title")
    print(title)
```

### Wait for Elements and URLs

```python
from selenium.webdriver.common.by import By
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    tab.wait_for_presence(By.TAG_NAME, "body", wait=10)
    tab.wait_for_visibility(By.CSS_SELECTOR, "main", wait=10)

    if tab.wait_for_url("https://example.com/", wait=5):
        print("Reached expected URL")
```

### Schedule Recurring Work

```python
from seleniumtabs import Browser


def collect_title(tab):
    print(tab.title)


with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    tab.schedule_task(collect_title, period=60)
    browser.execute_task(max_time=300, sleep_time=1)
```

### Drop Down to Selenium

```python
from seleniumtabs import Browser

with Browser(name="Chrome", headless=True) as browser:
    tab = browser.open("https://example.com")

    print(tab.driver.current_url)
    print(tab.driver.execute_script("return navigator.userAgent"))
```

## Browser Configuration

```python
from seleniumtabs import Browser

with Browser(
    name="Chrome",
    implicit_wait=10,
    user_agent="my-custom-user-agent",
    headless=True,
    full_screen=False,
    page_load_timeout=60,
) as browser:
    tab = browser.open("https://example.com")
```

Available constructor options:

- `name`: browser name, currently `"Chrome"` or `"FireFox"`.
- `implicit_wait`: Selenium implicit wait in seconds.
- `user_agent`: optional browser user agent. If omitted, Selenium Tabs generates one.
- `headless`: run without a visible browser window.
- `full_screen`: maximize the browser window after launch.
- `page_load_timeout`: Selenium page load timeout in seconds.
- `driver_factory`: optional advanced hook for creating a custom Selenium driver.
- `options_factory`: optional advanced hook for creating custom Selenium browser options.

## When to Use Selenium Tabs

Choose Selenium Tabs when your job looks like a browser automation script:

- open several sites in separate tabs
- scrape or inspect browser-rendered HTML
- periodically refresh or monitor pages
- mix wrapper helpers with raw Selenium calls
- keep the code small and Pythonic

If you are building a full end-to-end test suite with network mocking, browser contexts, mobile emulation, trace viewing, and generated tests, Playwright may be a better fit.

## Development

For contributors:

```bash
git clone https://github.com/inquilabee/selenium-tabs.git
cd selenium-tabs
make sync
```

Useful commands:

```bash
make test          # run the default deterministic test suite
make integration   # run live browser/network tests
make check-commit  # run formatting, lint, tests, and security scan
make lint          # run all pre-commit hooks
make build         # build wheel and sdist
```

The default tests use local fixtures. Live browser or external-site checks are marked as integration tests.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
