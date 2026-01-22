from queue import Queue
from playwright.sync_api import sync_playwright

class BrowserManager:
    def __init__(self, size=3, headless=True):
        self.size = size
        self._headless = headless
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return
        self._initialized = True
        self._queue = Queue()
        self._sync_playwright = sync_playwright().start()
        for _ in range(self.size):
            browser = self._sync_playwright.chromium.launch(headless=self._headless)
            self._queue.put(browser)

    def get_browser(self):
        self._initialize()
        return self._queue.get()
    def return_browser(self, browser):
        return self._queue.put(browser)
    def close_all_browsers(self):
        while not self._queue.empty():
            browser = self._queue.get()
            browser.close()
        self._sync_playwright.stop()


