class BrowserSessions:
    def __init__(self):
        self.browser_sessions = []

    def get_browser_for_tab(self, tab):
        if browser := [browser for browser in self.browser_sessions if tab in browser]:
            return browser[0]

        return None

    def close_tab(self, tab):
        if browser := self.get_browser_for_tab(tab):
            browser.close_tab(tab)

    def add_browser(self, br):
        self.browser_sessions.append(br)


browser_sessions = BrowserSessions()
