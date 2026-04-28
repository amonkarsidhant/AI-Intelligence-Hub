# AI Intelligence Hub

A modern AI news and signal dashboard with a polished SaaS-style interface.

## Status

`v0.6.0 Modern Dashboard Release Candidate`

A fully redesigned dashboard with Light/Dark/System theme support, a modern app-shell layout, and improved usability.

## What Works

- **Modern UI**: Soft grey background, white cards, and consistent design system.
- **Theme Support**: Light, Dark, and System theme (persisted in localStorage).
- **App-Shell Layout**: Left sidebar navigation with all tabs, top header with search and actions.
- **Overview Page**: Daily Trust State, New Items, High Signal count, Saved items summary.
- **Today's Top 5**: High-signal briefing cards with "Why it matters" and "For me" context.
- **Try This Weekend**: Practical experiments with setup difficulty and install commands.
- **Source Health**: Detailed status cards showing freshness, cache age, and failure reasons.
- **Card & Table Views**: Toggle between Cards and Table views on GitHub, Models, and Research tabs.
- **Kanban Saved Board**: Saved items organized as columns (To Read, To Test, Testing, Useful).
- **Global Search**: Search across all items with real-time filtering.
- **Digest Modal**: Generate, view, copy, and download daily digests.
- **Trends Page**: Rising and cooling topics visualization.
- **Settings Page**: Theme toggle and refresh controls.
- **Responsive**: Works on Desktop, Tablet, and Phone.

## Quick Start

```bash
# Build
docker build -t ai-dashboard .

# Run with persistent data
docker run -d --name ai-dashboard \
  -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -e DATA_DIR=/app/data \
  -e DB_PATH=/app/data/intelligence.db \
  -e CACHE_DIR=/app/data/cache \
  -e DIGEST_DIR=/app/data/digests \
  -e DATA_FILE=/app/data/data.json \
  -e SCORED_DATA_FILE=/app/data/data_scored.json \
  --restart unless-stopped \
  ai-dashboard
```

Open `http://localhost:8888`.

## Daily Workflow

### Daily Status

At the top of the dashboard you will see:

- last dashboard update time
- per-source health cards
- cached / stale / failed indicators
- new items collected today

Use this section first to decide whether today’s dashboard is trustworthy.

### Refresh Now

Click **Refresh Now** in the header or Daily Status section.

What it does:

- calls `POST /api/refresh`
- runs the fetch pipeline safely
- preserves existing data if refresh fails
- updates source health
- shows success / partial / failed feedback

### Today’s Digest

Click **Open Today’s Digest**.

What it does:

- calls `GET /api/digest`
- generates markdown digest content
- saves it to `data/digests/YYYY-MM-DD.md`
- opens the digest in a modal
- lets you copy it

### Saved Intelligence Workflow

Typical flow:

1. Save interesting items from the Feed or briefing cards.
2. Move them to `to_test` when you want hands-on time.
3. Add notes and tags.
4. Move them to `testing` or `useful` as they mature.
5. Remove or discard items that are no longer relevant.

## Manual Refresh Outside the UI

```bash
python3 fetch_news.py
```

This will:

- fetch all sources
- use cache fallback where needed
- deduplicate results
- update source health
- write `data.json`

## Testing

```bash
python3 -m pytest -q

# Optional legacy/manual checks
python3 test_smoke.py
```

## API Endpoints

- `GET /` - dashboard UI
- `GET /health` - container health check
- `GET /api/data` - raw data
- `GET /api/scored` - scored data
- `POST /api/refresh` - run manual refresh safely
- `POST /api/save` - save item
- `GET /api/saved` - list saved items
- `DELETE /api/saved/<int:item_id>` - remove saved item
- `PUT /api/saved/<int:item_id>/status` - update saved status
- `PUT /api/saved/<int:item_id>/notes` - update saved notes/tags
- `POST /api/ignore` - ignore item
- `GET /api/ignored` - list ignored items
- `POST /api/track` - track topic
- `GET /api/track` - list tracked topics
- `DELETE /api/track/<int:topic_id>` - remove tracked topic
- `GET /api/source-health` - normalized source health summary
- `GET /api/digest` - generate and save today’s digest

## Data Paths

Default local paths:

- `./data/intelligence.db`
- `./data/cache/`
- `./data/digests/`
- `./data/data.json`
- `./data/data_scored.json`

Docker paths:

- `/app/data/intelligence.db`
- `/app/data/cache/`
- `/app/data/digests/`
- `/app/data/data.json`
- `/app/data/data_scored.json`

## Environment Variables

- `DATA_DIR`
- `DB_PATH`
- `CACHE_DIR`
- `DIGEST_DIR`
- `DATA_FILE`
- `SCORED_DATA_FILE`
- `CONFIG_FILE`
- `CONFIG_PATH`

## Troubleshooting

### No data showing

- Click **Refresh Now**.
- Or run `python3 fetch_news.py`.
- Check whether `data/data.json` exists.

### Source shows stale or using cache

- The dashboard is still usable, but that source is not fresh.
- Check network access from the Pi or container.
- Look at the Daily Status card for the failure reason.

### Refresh failed

- Existing data is preserved.
- Check `docker logs ai-dashboard`.
- Verify DNS / outbound network access.

### Digest could not be generated

- Open `docker logs ai-dashboard`.
- Check that `data/data.json` exists and is valid.
- Confirm `data/digests/` is writable.

## Cron Example

Outside Docker:

```bash
0 */6 * * * cd /home/pi/AI-Intelligence-Hub && DATA_DIR=./data python3 fetch_news.py
```

Inside Docker:

```bash
0 */6 * * * cd /home/pi/AI-Intelligence-Hub && docker exec ai-dashboard python3 fetch_news.py
```

## Manual User Validation Checklist

After starting the dashboard:

1. Open `http://localhost:8888`
2. Click **Refresh Now**
3. Confirm Daily Status updates
4. Save one item
5. Open the **Saved** tab
6. Change its status to `to_test`
7. Add notes and tags
8. Remove the item
9. Ignore one feed item
10. Track one topic
11. Open Today’s Digest
12. Confirm a file exists in `data/digests/`

## Notes

- The dashboard is optimized for a lightweight Flask + SQLite + JSON + vanilla JS deployment.
- No extra frontend framework is required.
- The focus is daily usefulness, not feed quantity.
