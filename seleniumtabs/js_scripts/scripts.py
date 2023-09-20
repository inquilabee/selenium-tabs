PAGE_HEIGHT = "return document.documentElement.scrollHeight"

ELEMENT_ATTRIBUTES = """
    var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) {
        items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
    };
    return items;
"""

NEW_TAB = """window.open('about:blank');"""

ELEMENT_CLICK = """
    arguments[0].click();
"""

SCROLL_TO_HEIGHT = "window.scrollTo(0, {new_height});"

SCROLL_TO_WINDOW_HEIGHT = "window.scrollTo(0, arguments[0]);"

USER_AGENT = "return window.navigator.userAgent"
