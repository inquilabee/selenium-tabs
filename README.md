# Selenium Tabs

A Python library that makes browser automation with Selenium more intuitive by providing a tab-centric interface. Manage multiple browser tabs with ease, perform common operations, and interact with web elements using a clean, Pythonic API.

---

And guess what! You don't need to manually download drivers for the browser—it's all taken care of by the library. Install and start right away.

**Note:** All testing has been done on Chrome.

## 🚀 Top Features

- **Tab Management**: Open, close, switch, and query tab state with ease.
- **Element Selection**: Use CSS selectors, jQuery, and PyQuery for powerful element querying.
- **Page Interaction**: Scroll, click, and wait for elements with robust error handling.
- **Advanced Features**: Direct driver access, task scheduling, and more.
- **Automatic Driver Management**: No need to manually download or manage browser drivers.

## 🔧 Installation

```bash
pip install seleniumtabs
```

Or with Poetry:
```bash
poetry add seleniumtabs
```

## 📋 Requirements

- Python 3.13+
- Chrome or Firefox browser

## 🚀 Quick Start

```python
from seleniumtabs import Browser

# Create a browser instance and open multiple tabs
with Browser(name="Chrome", implicit_wait=10) as browser:
    # Open multiple websites in different tabs
    google = browser.open("https://google.com")
    yahoo = browser.open("https://yahoo.com")

    # Work with tabs
    print(f"Current tab: {browser.current_tab}")
    print(f"First tab: {browser.first_tab}")
    print(f"Last tab: {browser.last_tab}")

    # Switch between tabs
    yahoo.switch()
    google.switch()

    # Close a tab
    yahoo.close()
```

## ✨ Key Features

### 1. Tab Management
```python
with Browser(name="Chrome") as browser:
    # Open tabs
    tab1 = browser.open("https://example.com")
    tab2 = browser.open("https://example.org")

    # Access tab properties
    print(tab1.title)  # Page title
    print(tab1.url)    # Current URL
    print(tab1.domain) # Domain name

    # Check tab state
    print(tab1.is_active)  # Is this the active tab?
    print(tab1.is_alive)   # Is the tab still open?
```

### 2. Element Selection
```python
with Browser(name="Chrome") as browser:
    tab = browser.open("https://example.com")

    # CSS Selectors
    elements = tab.css("div.class-name")
    for element in elements:
        print(element.text)

    # Chaining selectors
    main_content = tab.css("main")[0]
    links = main_content.css("a")

    # Get element attributes
    for link in links:
        print(link.get_attribute("href"))
```

### 3. Page Interaction
```python
with Browser(name="Chrome") as browser:
    tab = browser.open("https://example.com")

    # Scrolling
    tab.scroll_down(times=3)  # Scroll down 3 times
    tab.scroll_up(times=2)    # Scroll up 2 times
    tab.scroll_to_bottom()    # Scroll to page bottom

    # Clicking elements
    element = tab.css("button")[0]
    tab.click(element)

    # Wait for elements
    tab.wait_for_presence("div", "class-name", wait=10)
    tab.wait_for_visibility("button", "submit", wait=5)
```

### 4. Advanced Features
```python
with Browser(name="Chrome") as browser:
    tab = browser.open("https://example.com")

    # jQuery-like operations
    jq_elements = tab.jq("div.class-name")

    # PyQuery for HTML parsing
    pq = tab.pyquery
    text_content = pq.text()

    # Run JavaScript
    result = tab.run_js("return document.title")

    # Schedule tasks
    def refresh_page(tab):
        tab.refresh()

    tab.schedule_task(refresh_page, period=60)  # Refresh every 60 seconds
```

### Direct Driver Access

- If a feature is not directly available in the `Tab` object, you can access the underlying Selenium WebDriver directly via `tab.driver`.
- **Example:**
  ```python
  # Access driver methods directly
  tab.driver.execute_script("return document.title")
  ```

- **Fallback Behavior**: If you call a non-existent method on the `Tab` object, an attempt is made to query `tab.driver.method_name` via `__getattribute__`.

### jQuery Integration

- You can use the `tab.jq` or `tab.jquery` property to run jQuery-like selectors and operations directly on the live browser DOM.
- Tested features:
  - Selecting elements with jQuery syntax.
  - Chaining jQuery selectors.
  - Accessing and manipulating attributes and text.
  - Interacting with elements (e.g., click, scroll).

**Example:**
```python
jq_elements = tab.jq("div.class-name")
for el in jq_elements:
    print(el.text)
```

---

### PyQuery Integration

- You can use the `tab.pyquery` or `tab.pq` property to parse and query the current page's HTML snapshot using PyQuery (lxml-based).
- Tested features:
  - `.items()` for iterating over selections and sub-selections.
  - `.find()`, `.parent()`, `.children()` for DOM navigation.
  - `.attr()`, `.text()`, `.html()` for attribute and content access.
  - Consistency between `tab.pyquery` and `tab.pq`.
  - Integration with real-world pages (e.g., Yahoo).

**Example:**
```python
pq = tab.pyquery
for link in pq("nav a").items():
    print(link.attr("href"))
print(pq("title").text())
```

---

## 🔍 Browser Options

```python
with Browser(
    name="Chrome",           # Browser name ("Chrome" or "FireFox")
    implicit_wait=10,        # Default wait time for elements
    headless=False,          # Run browser in headless mode
    full_screen=True,        # Start browser in full screen
    page_load_timeout=60     # Page load timeout in seconds
) as browser:
    # Your code here
```


## ✅ Tested Features

This library is thoroughly tested for:

- **Tab Management**: Opening, closing, switching, and querying tab state.
- **Element Selection**: CSS selector queries, chaining, and attribute access.
- **Page Interaction**: Scrolling, clicking, and waiting for elements.
- **Page Loading**: Full and partial page load handling, including timeouts.
- **Tab Refresh**: Full and partial refresh with robust error handling.
- **Task Scheduling**: Periodic tab actions (e.g., auto-refresh).
- **Integration with jQuery and PyQuery** (see below).

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
