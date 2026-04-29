#!/bin/bash
set -e

echo "Running DailyDex v0.7.0-rc1 release checks..."

echo ""
echo "=== Python Syntax Validation ==="
python3 -m py_compile dashboard_new.py data_models.py fetch_news.py scoring_engine.py digest_generator.py
echo "Python syntax validation passed."

echo ""
echo "=== JavaScript Syntax Check ==="
if command -v node >/dev/null 2>&1; then
    node --check static/app.js
    echo "JavaScript syntax validation passed."
else
    echo "Warning: node not installed; skipping static/app.js syntax check"
fi

echo ""
echo "=== Docker Build ==="
docker build -t dailydex .
echo "Docker build succeeded."

echo ""
echo "=== Pytest ==="
python3 -m pytest -q

echo ""
echo "All release checks passed."
