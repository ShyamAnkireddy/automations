import logging
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from common.api.api_actions import APIClient

ROOT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
LOGS_DIR = REPORTS_DIR / "logs"
for directory in (REPORTS_DIR, SCREENSHOTS_DIR, LOGS_DIR, REPORTS_DIR / "videos"):
    directory.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT_DIR / ".env")


def _configure_logging():
    log_path = LOGS_DIR / "pytest.log"
    logger = logging.getLogger("automation")
    logger.setLevel(logging.INFO)
    if not any(
        isinstance(handler, logging.FileHandler)
        and getattr(handler, "baseFilename", None) == str(log_path)
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(handler)
    return logger


LOGGER = _configure_logging()


@pytest.fixture(scope="session")
def api_client():
    client = APIClient()
    yield client
    client.close()


@pytest.fixture
def logger():
    return LOGGER


@pytest.fixture
def page(page):
    """Use pytest-playwright's standard page fixture."""
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    if report.failed:
        LOGGER.error(
            "pytest failure | test=%s | phase=%s | message=%s",
            item.nodeid, report.when, str(report.longrepr)[:4000],
        )
        # The call-phase report is produced before fixture teardown, so the page
        # is still available for a failure screenshot here.
        page = item.funcargs.get("page")
        if page is not None and report.when == "call":
            safe_name = "".join(
                char if char.isalnum() or char in "-_" else "_"
                for char in item.nodeid
            )[-140:]
            screenshot_path = SCREENSHOTS_DIR / f"{safe_name}.png"
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                LOGGER.error("Failure screenshot: %s", screenshot_path)
            except Exception as exc:
                LOGGER.exception("Could not save failure screenshot: %s", exc)


def pytest_configure(config):
    LOGGER.info("Starting pytest run. Root=%s", ROOT_DIR)
