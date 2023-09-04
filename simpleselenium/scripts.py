PAGE_HEIGHT = "return document.documentElement.scrollHeight"

ELEMENT_ATTRIBUTES = (
    "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) {"
    " items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value };"
    " return items;"
)

SCROLL_TO_HEIGHT = "window.scrollTo(0, {new_height});"

SCROLL_TO_WINDOW_HEIGHT = "window.scrollTo(0, arguments[0]);"

JQUERY_INJECTION = """
var script = document.createElement( 'script' );
script.type = 'text/javascript';
script.src =  'https://code.jquery.com/jquery-3.7.1.min.js';
document.head.appendChild(script);

script.onload = function() {
    var $ = window.jQuery;
}
"""
