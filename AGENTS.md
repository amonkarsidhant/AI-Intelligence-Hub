# AI Intelligence Command Center

Personal AI news aggregator with daily email newsletter and intelligent signal scoring.

## Architecture

```
ai-dashboard/
├── dashboard_new.py      # New Flask dashboard with signal scoring (port 8888)
├── scoring_engine.py     # Signal scoring algorithm (0-100)
├── data_models.py        # SQLite storage for saved items
├── digest_generator.py   # Daily markdown digest generator
├── fetch_news.py         # Data fetcher (YouTube, GitHub, HF, blogs, ArXiv)
├── send_email.py         # Newsletter email sender
├── config/
│   ├── topics.json       # Focus areas, scoring weights
│   ├── sources.json      # Data source configuration
│   └── runtime.json      # Runtime settings
├── data/
│   ├── intelligence.db   # SQLite database
│   └── digests/         # Daily markdown digests
├── data_scored.json     # Pre-scored data with executive brief
└── Dockerfile           # Container definition
```

## Features (Phase 1 Complete)

### Signal Scoring Engine
- Scores every item from 0-100 based on:
  - Recency, popularity/stars, relevance to focus areas
  - Agentic workflow relevance, local/PI suitability
- Action recommendations: Try, Save, Read, Ignore
- Categories: Model, Agent, Open Source, Research, etc.

### Executive Brief
- Top 5 AI developments with signal scores
- Why each matters and action recommendations
- Generated daily from high-signal items

### New Dashboard UI
- Signal score badges (Hot/Watch/Interesting/Low)
- Source badges (GitHub/Model/Video/News/Paper)
- Category tags, Pi suitability badges
- Dark theme, responsive design

### New Tabs
- **Feed**: Unified high-signal stream
- **GitHub**: Trending repos with scores and Pi compatibility
- **Models**: HuggingFace models with local/coding filters
- **Videos**: YouTube with watch priority
- **News**: AI news grouped by category
- **Research**: Papers with recommendations
- **Local Lab**: Pi-compatible projects to try
- **Saved**: Your saved intelligence with status tracking

### Saved Intelligence
- Save items from any card
- SQLite storage with status: to_test, to_read, useful
- Notes and tags support

### Daily Digest
- Markdown format saved to `data/digests/YYYY-MM-DD.md`
- Includes: Brief, High Signal, GitHub, Models, Videos, Papers
- Things to try this weekend

## Commands

```bash
# Run new dashboard (standalone, for testing)
python3 /home/sidhant/ai-dashboard/dashboard_new.py

# Build Docker image
docker build -t ai-dashboard /home/sidhant/ai-dashboard

# Run container
docker run -d --name ai-dashboard -p 8888:8888 --restart unless-stopped -v /home/sidhant/ai-dashboard:/app ai-dashboard

# Manually fetch and score data
python3 /home/sidhant/ai-dashboard/fetch_news.py

# Generate digest
python3 /home/sidhant/ai-dashboard/digest_generator.py

# Send test email
python3 /home/sidhant/ai-dashboard/send_email.py
```

## Cron Jobs

```bash
# Data refresh every 12 hours
0 */12 * * * CONFIG_FILE=/home/sidhant/ai-dashboard/config.json DATA_FILE=/home/sidhant/ai-dashboard/data.json /usr/bin/python3 /home/sidhant/ai-dashboard/fetch_news.py >> /home/sidhant/ai-dashboard/dashboard.log 2>&1

# Daily email at 8AM CEST
0 6 * * * CONFIG_FILE=/home/sidhant/ai-dashboard/config.json DATA_FILE=/home/sidhant/ai-dashboard/data.json /usr/bin/python3 /home/sidhant/ai-dashboard/send_email.py >> /home/sidhant/ai-dashboard/email.log 2>&1
```

## API Endpoints

- `GET /` - Dashboard with signal-scored content
- `GET /api/data` - Raw data
- `GET /api/scored` - Scored data with executive brief
- `POST /api/save` - Save an item
- `GET /api/saved` - Get saved items
- `DELETE /api/saved/<id>` - Delete saved item
- `GET /api/digest` - Generate daily digest

## Configuration

Edit `config/topics.json` to customize:
- Focus areas (keywords to prioritize)
- Blocked keywords
- Scoring weights
- Category thresholds

## Keyboard Shortcuts
- `/` - Search
- `s` - Go to Saved
- `f` - Go to Feed

## Common Issues

- Emoji in Python strings cause syntax errors - use ASCII only
- Docker paths must be `/app/` inside container, `/home/sidhant/ai-dashboard/` on host
- Ollama API timeout: if LLM fails, falls back to simple count

## Testing

```bash
# Test dashboard
curl http://localhost:8888

# Test API
curl http://localhost:8888/api/scored

# Test scoring
python3 -c "
import sys; sys.path.insert(0, '/home/sidhant/ai-dashboard')
from scoring_engine import SignalScorer
scorer = SignalScorer()
print(scorer.score_github_repo({'title': 'test', 'description': 'AI agent', 'stars': '5000', 'url': ''}))
"
```

## Future (Phase 2-3)
- Local Lab tab improvements
- Agentic Workflows tab
- Trend radar with historical tracking
- Search and advanced filters
- Intelligence clustering (deduplication)
- Ollama-powered summarization