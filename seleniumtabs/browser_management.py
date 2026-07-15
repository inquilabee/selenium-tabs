class BrowserSessions:
    def __init__(self):
        self.browser_sessions = []

    def get_browser_for_tab(self, tab):
        if browser := [browser for browser in self.browser_sessions if tab in browser]:
            return browser[0]

        return None

    def close_tab(self, tab):
        if browser := self.get_browser_for_tab(tab):
            return browser.close_tab(tab)

        return None

    def add_browser(self, br):
        self.browser_sessions.append(br)

    def remove_browser(self, br):
        self.browser_sessions = [browser for browser in self.browser_sessions if browser != br]


browser_sessions = BrowserSessions()
