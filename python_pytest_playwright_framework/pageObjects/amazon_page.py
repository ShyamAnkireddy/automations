from urllib.parse import urlparse

from common.ui.ui_actions import UIActions

class AmazonPage:
    def __init__(self, page, base_url="https://www.amazon.com"):
        self.page = page
        self.actions = UIActions(page)
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or parsed.hostname not in {
            "www.amazon.com", "amazon.com", "www.amazon.in", "amazon.in"
        }:
            raise ValueError("Use a supported HTTPS Amazon storefront URL.")
        self.base_url = base_url.rstrip("/")
        self.search_box = page.locator("input[name='field-keywords']")
        self.result_cards = page.locator("div[data-component-type='s-search-result']")

    def open(self):
        self.actions.open(self.base_url)

    def search(self, query):
        self.actions.wait_visible(self.search_box)
        self.search_box.fill(query)
        self.search_box.press("Enter")
        self.result_cards.first.wait_for(state="visible", timeout=20_000)

    def first_result_title(self):
        first_card = self.result_cards.first
        title = first_card.locator("h2[aria-label]").first
        title.wait_for(state="visible", timeout=10_000)
        return title.get_attribute("aria-label")
