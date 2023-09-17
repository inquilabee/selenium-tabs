JQUERY_INJECTION = """
    var script = document.createElement( 'script' );
    script.type = 'text/javascript';
    script.src =  'https://code.jquery.com/jquery-3.7.1.min.js';
    document.head.appendChild(script);

    script.onload = function() {
        var $ = window.jQuery;
    }
"""

PAGE_HTML = """
    return "<html>" + $("html").html() + "</html>";
"""

JQUERY_INJECTION_CHECK = """
    return $
"""
