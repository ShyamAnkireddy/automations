# Python + pytest + Playwright Automation Framework

A starter framework with shared API/UI utilities, Page Objects, test data, pytest fixtures,
timestamped HTML reports, per-test UI screenshots and videos, and logs.

## Folder structure

```text
python_pytest_playwright_framework/
├── common/
│   ├── api/
│   │   ├── api_actions.py
│   │   └── api_constants.py
│   └── ui/
│       └── ui_actions.py
├── pageObjects/
│   └── amazon_page.py
├── testData/
│   └── search_data.py
├── tmp/
├── tests/
│   ├── api/
│   │   └── test_jsonplaceholder_api.py
│   └── ui/
│       └── test_amazon_search.py
├── reports/
│   ├── logs/
│   ├── screenshots/
│   ├── videos/
│   └── .gitkeep
├── conftest.py
├── pytest.ini
├── requirements.txt
├── .env.example
└── .gitignore
```

## 1. Setup

Python 3.10+ recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
```

If PowerShell blocks activation, you can run the venv Python directly:
`\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

## 2. Run tests

From the project root:

```bash
# API demo tests only (no browser required)
pytest tests/api

# Amazon UI test (opens Amazon, searches, checks the first result)
pytest tests/ui --headed
```

Every pytest run creates a self-contained HTML report under `reports/`, named
`ui-report-<timestamp>.html` or `api-report-<timestamp>.html` for UI-only or API-only
runs. Mixed runs use `test-report-<timestamp>.html`.
UI tests save a screenshot and video for each test under `reports/screenshots/` and
`reports/videos/`. Those two artifact folders are cleared at the start of each run;
timestamped reports are retained so runs do not overwrite one another. Logs are written
under `reports/logs/`.

## 3. Example tests

### Amazon UI test
- Opens `AMAZON_BASE_URL` (defaults to `https://www.amazon.com`).
- Waits for the search field to become visible.
- Searches for **Samsung S25 Ultra**.
- Waits for product result cards and asserts the first result has a non-empty title and
  a Samsung/S25 Ultra-related title.

Amazon can vary results by location, cookies, inventory, ads, and experiments. It may show
a CAPTCHA or block automation. If the test fails because of a challenge or a changed page,
inspect the screenshot/log in `reports/`; do not try to bypass anti-bot controls. Use a
permitted test environment or a site you own for stable UI tests.

### API demo tests
Uses JSONPlaceholder (`https://jsonplaceholder.typicode.com`), a public fake REST API.
GET `/posts/1` is checked for expected fields. POST `/posts` demonstrates a safe sample
request; JSONPlaceholder returns a simulated created record and does not persist it.

## 4. Framework design notes

- `conftest.py` at the repository root is the single shared pytest fixture entry point.
- `common/api/api_actions.py` centralizes GET, POST, PUT, PATCH, and DELETE signatures.
- API requests use HTTPS, a finite timeout, JSON serialization, and a configurable host allowlist.
  To target another API, explicitly set `API_BASE_URL` and `API_ALLOWED_HOSTS` for that host.
- API methods do not log authorization headers or request bodies. Never commit tokens, passwords,
  cookies, or real customer data. Keep `.env` local and out of Git.
- `pageObjects/` owns page-specific selectors and workflows; `common/ui/` holds generic browser actions.
- `testData/` contains reusable test inputs, separate from test logic.
- `reports/` and `tmp/` are generated-output areas and are ignored by Git.
- Tests do not make purchases, sign in, submit payment details, or perform destructive API calls.

## 5. Extend safely

1. Add a Page Object under `pageObjects/`.
2. Put generic browser actions in `common/ui/ui_actions.py`; keep site-specific selectors in Page Objects.
3. Add API endpoints/methods in `common/api/`; keep API-specific constants in `api_constants.py`.
4. Add test data in `testData/`.
5. Add tests under `tests/api/` or `tests/ui/`.
6. Keep real credentials in environment variables or a secret manager; do not add them to source control.
