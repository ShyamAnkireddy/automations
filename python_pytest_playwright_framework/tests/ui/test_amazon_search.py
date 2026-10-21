import os

import pytest

from pageObjects.amazon_page import AmazonPage
from testData.search_data import AMAZON_SEARCH_QUERY, EXPECTED_PRODUCT_TERMS

pytestmark = [pytest.mark.ui, pytest.mark.smoke]


def test_amazon_search_shows_samsung_s25_ultra_result(page, logger):
    base_url = os.getenv("AMAZON_BASE_URL", "https://www.amazon.com")
    amazon = AmazonPage(page, base_url=base_url)

    amazon.open()
    amazon.search(AMAZON_SEARCH_QUERY)
    first_title = amazon.first_result_title()
    logger.info("Amazon first result title: %s", first_title)

    assert first_title, "The first search result should have a visible product title."
    normalized_title = first_title.casefold()
    assert any(term in normalized_title for term in EXPECTED_PRODUCT_TERMS), (
        "Expected the first result title to mention Samsung or S25/Ultra, "
        f"but got: {first_title!r}"
    )
