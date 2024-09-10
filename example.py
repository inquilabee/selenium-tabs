from seleniumtabs import Browser

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
    bing.close()  # Or browser.close_tab(bing)

    # Switching to a tab
    yahoo.switch()
    google.switch()

    # Accessing the driver object
    print(google.driver.title, google.title)  # Should output same value

    # Directly access driver methods and attributes
    print(google.current_window_handle, google.tab_handle)
    google.refresh()

    # PyQuery
    print(google.pyquery.text())
    print(google.pq.size())
