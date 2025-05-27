from playwright.sync_api import sync_playwright
import pytest

class BaseClass:

    def __init__(self):
        self.pw = None
        self.browsers = {}
        self.contexts = {}
        self.pages = {}
        self.counter = 0
        self.enable_automation_url = "https://rtqawww.securly.com/automation/enableAutomation"

    def start(self):
        if self.pw is None:
            self.pw = sync_playwright().start()

    def create_browser(self,):
        self.start()
        # browser_type = config.getoption("--browser")
        # headed_mode = config.getoption("--headed")
        # browser = getattr(self.pw, browser_type).launch(headless=not headed_mode)
        # browser = self.pw..launch(headless=False)
        browser = self.pw.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        handle = f"browser_{self.counter}"
        self.counter += 1
        self.browsers[handle] = browser
        self.contexts[handle] = context
        self.pages[handle] = page
        print(handle)
        return handle

    # def create_browser_remote_desktop_connection(self,ip,port):
    #     self.start()
    #     browser = self.pw.chromium.connect(f"ws://{ip}:{port}/playwright",headless=False)
    #     context = browser.new_context()
    #     page = context.new_page()
    #     handle = f"browser_{self.counter}"
    #     self.counter += 1
    #     self.browsers[handle] = browser
    #     self.contexts[handle] = context
    #     self.pages[handle] = page
    #     print(handle)
    #     return handle

    def operate_on_browsers(self, *handles):
        for handle in handles:
            page = self.pages[handle]
            # This should be implemented in the test or controller as needed
            pass

    def enable_automation(self, handle):
        # page = self.pages[handle]
        handle.goto("https://rtqawww.securly.com/automation/enableAutomation")

    def close_browser(self, handle):
        if handle in self.browsers:
            self.browsers[handle].close()
            del self.browsers[handle]
            del self.contexts[handle]
            del self.pages[handle]

    def close_all(self):
        for browser in list(self.browsers.values()):
            browser.close()
        self.browsers.clear()
        self.contexts.clear()
        self.pages.clear()
        if self.pw:
            self.pw.stop()
            self.pw = None





