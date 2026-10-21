class UIActions:
    """Reusable, site-agnostic Playwright actions."""

    def __init__(self, page, timeout_ms=30_000):
        self.page = page
        self.timeout_ms = timeout_ms

    def open(self, url):
        return self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)

    def wait_visible(self, locator, timeout_ms=None):
        locator.wait_for(
            state="visible",
            timeout=timeout_ms or self.timeout_ms,
        )
        return locator

    def click(self, locator):
        self.wait_visible(locator)
        locator.click()

    def fill(self, locator, value):
        self.wait_visible(locator)
        locator.fill(value)

    def text(self, locator):
        self.wait_visible(locator)
        return locator.inner_text().strip()
