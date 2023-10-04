class BrowserSessions:
    def __init__(self):
        self.sessions = []

    def close_tab(self, tab):
        if browser := [browser for browser in self.sessions if tab in browser]:
            br = browser[0]
            br.close_tab(tab)

    def add_browser(self, br):
        self.sessions.append(br)


browser_sessions = BrowserSessions()
