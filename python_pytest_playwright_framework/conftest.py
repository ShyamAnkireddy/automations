import logging
import os
import shutil
from datetime import datetime
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

VIDEOS_DIR = REPORTS_DIR / "videos"


def _clear_directory(directory):
    for path in directory.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


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
    if report.when == "call" and item.get_closest_marker("ui"):
        page = item.funcargs.get("page")
        if page is not None:
            index = item.session.items.index(item) + 1
            safe_name = "".join(
                char if char.isalnum() or char in "-_" else "_"
                for char in item.nodeid
            )[-120:]
            screenshot_path = SCREENSHOTS_DIR / f"{index:04d}_{safe_name}.png"
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                LOGGER.info("UI screenshot: %s", screenshot_path)
            except Exception:
                LOGGER.exception(
                    "Could not save UI screenshot for %s", item.nodeid
                )


def pytest_configure(config):
    _clear_directory(SCREENSHOTS_DIR)
    _clear_directory(VIDEOS_DIR)

    if not config.pluginmanager.hasplugin("html"):
        raise pytest.UsageError(
            "pytest-html is required to create a timestamped HTML report. "
            "Install dependencies from requirements.txt."
        )
    if not hasattr(config.option, "video"):
        raise pytest.UsageError(
            "pytest-playwright is required to capture UI videos. "
            "Install dependencies from requirements.txt."
        )

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    config._report_timestamp = timestamp
    config.option.htmlpath = str(REPORTS_DIR / f"test-report-{timestamp}.html")
    config.option.self_contained_html = True
    config.option.video = "on"
    config.option.output = str(VIDEOS_DIR)
    LOGGER.info("Starting pytest run. Root=%s", ROOT_DIR)


def pytest_collection_finish(session):
    markers = {
        marker
        for item in session.items
        for marker in ("ui", "api")
        if item.get_closest_marker(marker)
    }
    if len(markers) == 1:
        report_type = markers.pop()
    else:
        report_type = "test"
    timestamp = session.config._report_timestamp
    report_path = REPORTS_DIR / f"{report_type}-report-{timestamp}.html"
    session.config.option.htmlpath = str(report_path)
    for plugin in session.config.pluginmanager.get_plugins():
        if hasattr(plugin, "_report_path") and hasattr(plugin, "_report"):
            plugin._report_path = report_path
            plugin._report.title = report_path.name
