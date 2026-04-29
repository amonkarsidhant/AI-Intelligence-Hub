# Contributing

Thanks for contributing to DailyDex.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 dashboard_new.py
```

Open `http://localhost:8888`.

## Docker Setup

```bash
docker build -t ai-dashboard .
docker run -d --name ai-dashboard \
  -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -e DATA_DIR=/app/data \
  -e DB_PATH=/app/data/intelligence.db \
  -e CACHE_DIR=/app/data/cache \
  -e DIGEST_DIR=/app/data/digests \
  -e DATA_FILE=/app/data/data.json \
  -e SCORED_DATA_FILE=/app/data/data_scored.json \
  ai-dashboard
```

## Development Workflow

1. Create a branch from `main`.
2. Make focused changes.
3. Run the test suite.
4. Verify the UI manually if you touched templates, CSS, or JS.
5. Open a pull request with screenshots for UI changes.

## Required Checks

```bash
python3 -m pytest -q
python3 -m py_compile dashboard_new.py data_models.py fetch_news.py
node --check static/app.js
```

## Project Conventions

- Keep the stack lightweight: Flask + vanilla JS + SQLite + JSON.
- Prefer small, direct changes over new abstractions.
- Keep runtime artifacts out of commits.
- Preserve accessibility and reduced-motion behavior.
- For frontend work, test desktop and mobile layouts.

## Manual UI Review

Use `docs/ui_review_checklist.md` before merging a UI-heavy PR.

## Good Contributions

- Source quality improvements
- Better ranking and signal explanations
- UI clarity and accessibility improvements
- Test coverage for routes and dashboard behavior
- Deployment hardening and observability
