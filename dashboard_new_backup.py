#!/usr/bin/env python3
"""AI Intelligence Command Center - Flask Dashboard"""

import json
import os
import sys
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Paths
DATA_FILE = os.environ.get("DATA_FILE", "/app/data.json")
CONFIG_FILE = os.environ.get("CONFIG_FILE", "/app/config.json")
SCORED_DATA_FILE = os.environ.get("SCORED_DATA_FILE", "/app/data_scored.json")

# Try importing our modules
try:
    from scoring_engine import SignalScorer
    from data_models import IntelligenceDB, IntelligenceJSON
    HAS_SCORE_ENGINE = True
except Exception as e:
    print(f"Warning: Could not load scoring engine: {e}")
    HAS_SCORE_ENGINE = False

# Initialize data stores
if HAS_SCORE_ENGINE:
    try:
        intel_db = IntelligenceDB()
        intel_json = IntelligenceJSON()
    except Exception as e:
        print(f"Warning: Could not initialize data stores: {e}")
        intel_db = None
        intel_json = None
else:
    intel_db = None
    intel_json = None


def load_data():
    """Load data from JSON file"""
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {"github": [], "huggingface": [], "youtube": [], "blogs": [], "papers": []}


def load_scored_data():
    """Load or generate scored data"""
    if not HAS_SCORE_ENGINE:
        return load_data()
    
    try:
        # Try to load existing scored data
        if os.path.exists(SCORED_DATA_FILE):
            with open(SCORED_DATA_FILE) as f:
                scored = json.load(f)
            # Check if scored today
            if scored.get("scored_at", "").startswith(datetime.now().strftime("%Y-%m-%d")):
                return scored
        
        # Generate new scored data
        data = load_data()
        scorer = SignalScorer()
        scored_data = scorer.score_all_items(data)
        
        # Add executive brief
        brief = scorer.generate_executive_brief(scored_data)
        scored_data["executive_brief"] = brief
        
        # Save scored data
        with open(SCORED_DATA_FILE, "w") as f:
            json.dump(scored_data, f, indent=2)
        
        return scored_data
    except Exception as e:
        print(f"Error generating scored data: {e}")
        return load_data()


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1.0, initial-scale=1.0">
    <title>AI Intelligence Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0a0a0a; --surface: #141414; --surface-hover: #1a1a1a; --border: #262626; --text: #f5f5f5; --text-dim: #737373; --accent: #22c55e; --accent-dim: rgba(34, 197, 94, 0.15); 
            --hot: #ef4444; --watch: #f59e0b; --interesting: #3b82f6; --low: #6b7280;
            --github: #7dd3fc; --huggingface: #fcd34d; --youtube: #f87171; --blogs: #34d399; --papers: #a78bfa;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { font-size: 14px; }
        body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; min-height: 100vh; }
        a { color: inherit; text-decoration: none; }
        
        /* Header */
        header { padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); background: var(--surface); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
        .logo { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; }
        .logo span { color: var(--accent); }
        .header-right { display: flex; gap: 0.75rem; align-items: center; }
        .last-updated { font-size: 0.75rem; color: var(--text-dim); font-family: 'JetBrains Mono', monospace; }
        
        /* Stats Bar */
        .stats { display: flex; gap: 0.5rem; padding: 0.75rem 1.5rem; overflow-x: auto; border-bottom: 1px solid var(--border); background: var(--surface); }
        .stat { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.75rem; background: var(--bg); border-radius: 8px; font-size: 0.8rem; }
        .stat-value { font-weight: 600; font-family: 'JetBrains Mono', monospace; color: var(--accent); }
        .stat-label { color: var(--text-dim); }
        
        /* Executive Brief */
        .brief-section { padding: 1.5rem; border-bottom: 1px solid var(--border); background: linear-gradient(135deg, var(--surface) 0%, rgba(34, 197, 94, 0.05) 100%); }
        .brief-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; color: var(--accent); text-transform: uppercase; margin-bottom: 1rem; }
        .brief-grid { display: grid; gap: 0.75rem; }
        .brief-item { display: flex; gap: 1rem; padding: 1rem; background: var(--bg); border: 1px solid var(--border); border-radius: 10px; border-left: 3px solid var(--accent); }
        .brief-rank { font-size: 1.5rem; font-weight: 700; color: var(--text-dim); width: 2rem; text-align: center; }
        .brief-content { flex: 1; }
        .brief-item-title { font-weight: 500; margin-bottom: 0.25rem; }
        .brief-meta { font-size: 0.75rem; color: var(--text-dim); display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .brief-action { font-size: 0.75rem; color: var(--accent); margin-top: 0.5rem; }
        
        /* Navigation */
        nav { display: flex; gap: 0.25rem; padding: 0.75rem 1.5rem; overflow-x: auto; border-bottom: 1px solid var(--border); position: sticky; top: 0; background: var(--bg); z-index: 100; }
        nav::-webkit-scrollbar { display: none; }
        .nav-btn { padding: 0.5rem 1rem; background: transparent; border: none; border-radius: 6px; color: var(--text-dim); font-size: 0.8rem; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.15s; }
        .nav-btn:hover { background: var(--surface); color: var(--text); }
        .nav-btn.active { background: var(--accent); color: var(--bg); }
        
        /* Main Content */
        main { padding: 1.5rem; }
        .section { display: none; }
        .section.active { display: block; }
        
        /* Section Headers */
        .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .section-title { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; color: var(--text-dim); text-transform: uppercase; }
        
        /* Cards Grid */
        .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }
        
        /* Card Styles */
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; position: relative; transition: all 0.2s; cursor: pointer; }
        .card:hover { background: var(--surface-hover); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
        .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
        
        /* Signal Score Badge */
        .signal-badge { display: flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.7rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
        .signal-hot { background: rgba(239, 68, 68, 0.2); color: var(--hot); }
        .signal-watch { background: rgba(245, 158, 11, 0.2); color: var(--watch); }
        .signal-interesting { background: rgba(59, 130, 246, 0.2); color: var(--interesting); }
        .signal-low { background: rgba(107, 114, 128, 0.2); color: var(--low); }
        
        /* Source Badges */
        .source-badge { font-size: 0.65rem; font-weight: 600; padding: 0.2rem 0.4rem; border-radius: 4px; text-transform: uppercase; }
        .source-github { background: rgba(125, 211, 252, 0.15); color: var(--github); }
        .source-huggingface { background: rgba(252, 211, 77, 0.15); color: var(--huggingface); }
        .source-youtube { background: rgba(248, 113, 113, 0.15); color: var(--youtube); }
        .source-blogs { background: rgba(52, 211, 153, 0.15); color: var(--blogs); }
        .source-papers { background: rgba(167, 139, 250, 0.15); color: var(--papers); }
        
        /* Card Content */
        .card-title { font-weight: 500; font-size: 0.9rem; line-height: 1.4; margin-bottom: 0.5rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .card-desc { font-size: 0.8rem; color: var(--text-dim); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.75rem; }
        
        /* Card Tags */
        .card-tags { display: flex; gap: 0.35rem; flex-wrap: wrap; margin-top: 0.75rem; }
        .tag { font-size: 0.65rem; padding: 0.15rem 0.4rem; background: var(--bg); border-radius: 4px; color: var(--text-dim); }
        
        /* Card Footer */
        .card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-dim); }
        
        /* Action Buttons */
        .action-btn { padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; cursor: pointer; border: none; transition: all 0.15s; }
        .action-save { background: var(--accent); color: var(--bg); }
        .action-ignore { background: var(--border); color: var(--text-dim); }
        .action-try { background: var(--hot); color: white; }
        
        /* Pi Suitability */
        .pi-badge { font-size: 0.65rem; padding: 0.15rem 0.35rem; border-radius: 4px; }
        .pi-yes { background: rgba(34, 197, 94, 0.2); color: var(--accent); }
        .pi-partial { background: rgba(245, 158, 11, 0.2); color: var(--watch); }
        .pi-no { background: rgba(107, 114, 128, 0.2); color: var(--low); }
        
        /* Saved Items Section */
        .saved-grid { display: grid; gap: 0.75rem; }
        .saved-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }
        .saved-info { flex: 1; }
        .saved-status { display: inline-block; font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 4px; margin-left: 0.5rem; }
        .status-to_test { background: rgba(245, 158, 11, 0.2); color: var(--watch); }
        .status-to_read { background: rgba(59, 130, 246, 0.2); color: var(--interesting); }
        .status-useful { background: rgba(34, 197, 94, 0.2); color: var(--accent); }
        
        /* Local Lab */
        /* Health Bar */
        .health-bar { display: flex; gap: 1rem; padding: 0.5rem 1.5rem; background: var(--surface); border-bottom: 1px solid var(--border); font-size: 0.7rem; }
        .health-item { display: flex; align-items: center; gap: 0.35rem; color: var(--text-dim); }
        .health-dot { width: 6px; height: 6px; border-radius: 50%; }
        .health-dot.healthy { background: var(--accent); }
        .health-dot.warning { background: var(--watch); }
        .health-dot.error { background: var(--hot); }
        .health-bar .last-update { margin-left: auto; color: var(--text-dim); font-family: 'JetBrains Mono', monospace; }

        /* Trend Radar */
        .radar-bar { display: flex; gap: 0.75rem; padding: 0.5rem 1.5rem; background: var(--bg); border-bottom: 1px solid var(--border); font-size: 0.7rem; align-items: center; overflow-x: auto; }
        .radar-title { font-weight: 600; color: var(--accent); letter-spacing: 0.05em; }
        .radar-item { padding: 0.2rem 0.5rem; border-radius: 4px; background: var(--surface); }
        .radar-item.rising { color: var(--accent); }
        .radar-item.cooling { color: var(--text-dim); }
        .radar-item.new { color: var(--interesting); }

        /* Filter Bar */
        .filter-bar { display: flex; gap: 0.5rem; padding: 0.75rem 1.5rem; border-bottom: 1px solid var(--border); overflow-x: auto; }
        .filter-btn { padding: 0.35rem 0.75rem; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; color: var(--text-dim); font-size: 0.75rem; cursor: pointer; white-space: nowrap; }
        .filter-btn:hover { background: var(--surface-hover); }
        .filter-btn.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }

        /* Lab Grid */
        .lab-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
        .lab-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; }
        .lab-title { font-weight: 600; margin-bottom: 0.5rem; }
        .lab-meta { font-size: 0.8rem; color: var(--text-dim); margin-bottom: 0.75rem; }
        .lab-reqs { display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
        .lab-req { font-size: 0.65rem; padding: 0.2rem 0.4rem; background: var(--bg); border-radius: 4px; color: var(--text-dim); }
        .lab-command { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; padding: 0.5rem; background: var(--bg); border-radius: 6px; color: var(--accent); overflow-x: auto; }
        .lab-risk { font-size: 0.65rem; color: var(--watch); margin-top: 0.5rem; }

        /* Workflows Tab */
        .workflow-section { margin-bottom: 1.5rem; }
        .workflow-title { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; color: var(--text-dim); text-transform: uppercase; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
        .workflow-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .workflow-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; }
        .workflow-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
        .workflow-title-text { font-weight: 600; font-size: 0.95rem; }
        .workflow-meta { font-size: 0.75rem; color: var(--text-dim); display: flex; gap: 0.75rem; flex-wrap: wrap; margin: 0.5rem 0; }
        .workflow-tags { display: flex; gap: 0.35rem; flex-wrap: wrap; }
        .maturity-badge { font-size: 0.6rem; padding: 0.15rem 0.35rem; border-radius: 4px; text-transform: uppercase; }
        .maturity-stable { background: rgba(34, 197, 94, 0.2); color: var(--accent); }
        .maturity-beta { background: rgba(245, 158, 11, 0.2); color: var(--watch); }
        .maturity-alpha { background: rgba(59, 130, 246, 0.2); color: var(--interesting); }
        .security-badge { font-size: 0.6rem; padding: 0.15rem 0.35rem; border-radius: 4px; }
        .security-low { background: rgba(34, 197, 94, 0.2); color: var(--accent); }
        .security-medium { background: rgba(245, 158, 11, 0.2); color: var(--watch); }
        .security-high { background: rgba(239, 68, 68, 0.2); color: var(--hot); }

        /* Watch Queue */
        .watch-queue { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
        .queue-section { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; }
        .queue-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; color: var(--text-dim); text-transform: uppercase; margin-bottom: 0.75rem; }
        .queue-title.must { color: var(--hot); }
        .queue-title.later { color: var(--watch); }
        .queue-title.skip { color: var(--text-dim); }

        /* News Categories */
        .news-categories { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
        .news-cat-btn { padding: 0.35rem 0.75rem; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; color: var(--text-dim); font-size: 0.75rem; cursor: pointer; }
        .news-cat-btn.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }

        /* Research Recommendations */
        .paper-recommendation { font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 4px; margin-left: 0.5rem; }
        .rec-read { background: rgba(34, 197, 94, 0.2); color: var(--accent); }
        .rec-skim { background: rgba(245, 158, 11, 0.2); color: var(--watch); }
        .rec-save { background: rgba(59, 130, 246, 0.2); color: var(--interesting); }
        .rec-ignore { background: rgba(107, 114, 128, 0.2); color: var(--low); }

        /* Model Specs */
        .model-specs { display: flex; gap: 0.75rem; flex-wrap: wrap; font-size: 0.7rem; color: var(--text-dim); margin: 0.5rem 0; }
        .model-spec { display: flex; align-items: center; gap: 0.25rem; }
        .model-filter-bar { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
        .model-filter-btn { padding: 0.35rem 0.75rem; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; color: var(--text-dim); font-size: 0.7rem; cursor: pointer; }
        .model-filter-btn.active { background: var(--accent); color: var(--bg); }

        /* Detailed Card Info */
        .card-detail { font-size: 0.75rem; color: var(--text-dim); margin-top: 0.5rem; display: flex; gap: 1rem; flex-wrap: wrap; }
        .card-detail span { display: flex; align-items: center; gap: 0.25rem; }

        /* Mobile Responsive */
        @media (max-width: 768px) {
            header { flex-direction: column; align-items: flex-start; }
            .stats { overflow-x: auto; }
            .card-grid { grid-template-columns: 1fr; }
            .lab-grid { grid-template-columns: 1fr; }
            .watch-queue { grid-template-columns: 1fr; }
            .brief-grid { gap: 0.5rem; }
            .brief-item { flex-direction: column; }
            .brief-rank { text-align: left; }
            nav { overflow-x: auto; }
            .filter-bar { overflow-x: auto; }
            .health-bar { flex-wrap: wrap; }
        }

        /* Empty State */
        .empty-state { text-align: center; padding: 3rem 1rem; color: var(--text-dim); }
        .empty-icon { font-size: 2rem; margin-bottom: 1rem; opacity: 0.5; }
        .empty-message { font-size: 0.9rem; }
        .lab-meta { font-size: 0.75rem; color: var(--text-dim); margin-bottom: 0.75rem; }
        .lab-reqs { display: flex; gap: 1rem; font-size: 0.7rem; color: var(--text-dim); }
        .lab-req { display: flex; align-items: center; gap: 0.25rem; }
        .lab-command { background: var(--bg); padding: 0.75rem; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--accent); margin-top: 0.75rem; overflow-x: auto; }
        
        /* Search */
        .search-bar { width: 100%; padding: 0.75rem 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; color: var(--text); font-size: 0.9rem; margin-bottom: 1rem; }
        .search-bar:focus { outline: none; border-color: var(--accent); }
        
        /* Empty State */
        .empty-state { text-align: center; padding: 3rem; color: var(--text-dim); }
        .empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
        
        /* Responsive */
        @media (max-width: 640px) {
            header { padding: 1rem; }
            .stats, nav, main { padding: 0.75rem 1rem; }
            .card-grid { grid-template-columns: 1fr; }
            .brief-item { flex-direction: column; gap: 0.5rem; }
            .brief-rank { width: auto; text-align: left; }
        }
        
        /* Loading skeleton */
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
        .skeleton { background: linear-gradient(90deg, var(--surface) 25%, var(--surface-hover) 50%, var(--surface) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
    </style>
</head>
<body>
    <header>
        <div class="logo">AI <span>Intelligence</span> Command Center</div>
        <div class="header-right">
            <span class="last-updated">{{ last_updated }}</span>
        </div>
    </header>
    
    <div class="stats">
        <div class="stat"><span class="stat-value">{{ github|length }}</span><span class="stat-label">GitHub</span></div>
        <div class="stat"><span class="stat-value">{{ huggingface|length }}</span><span class="stat-label">Models</span></div>
        <div class="stat"><span class="stat-value">{{ youtube|length }}</span><span class="stat-label">Videos</span></div>
        <div class="stat"><span class="stat-value">{{ blogs|length }}</span><span class="stat-label">News</span></div>
        <div class="stat"><span class="stat-value">{{ papers|length }}</span><span class="stat-label">Papers</span></div>
    </div>

    <!-- Executive Brief Section -->
    {% if executive_brief and executive_brief['items'] %}
    <div class="brief-section">
        <div class="brief-title">Today's Brief - Top Developments</div>
        <div class="brief-grid">
            {% for item in executive_brief['items'][:5] %}
            <div class="brief-item">
                <div class="brief-rank">{{ loop.index }}</div>
                <div class="brief-content">
                    <div class="brief-item-title">{{ item.title }}</div>
                    <div class="brief-meta">
                        <span class="signal-badge {% if item.signal_score >= 80 %}signal-hot{% elif item.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ item.signal_score }}</span>
                        {% for cat in item.categories[:2] %}<span class="tag">{{ cat }}</span>{% endfor %}
                        <span class="source-badge source-{{ item.source }}">{{ item.source }}</span>
                    </div>
                    <div class="brief-action">{{ item.recommendation }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    
    <!-- Source Health -->
    <div class="health-bar">
        <span class="health-item"><span class="health-dot healthy"></span>GitHub</span>
        <span class="health-item"><span class="health-dot healthy"></span>Models</span>
        <span class="health-item"><span class="health-dot healthy"></span>Videos</span>
        <span class="health-item"><span class="health-dot healthy"></span>News</span>
        <span class="health-item"><span class="health-dot healthy"></span>Papers</span>
        <span class="health-item last-update">Updated: {{ last_updated }}</span>
    </div>

    <!-- Trend Radar -->
    <div class="radar-bar">
        <span class="radar-title">TREND RADAR</span>
        <span class="radar-item rising">+ Agents</span>
        <span class="radar-item rising">+ Local LLMs</span>
        <span class="radar-item cooling">- CV Models</span>
    </div>

    <nav>
        <button class="nav-btn active" onclick="showTab('feed',this)">Feed</button>
        <button class="nav-btn" onclick="showTab('github',this)">GitHub</button>
        <button class="nav-btn" onclick="showTab('models',this)">Models</button>
        <button class="nav-btn" onclick="showTab('videos',this)">Videos</button>
        <button class="nav-btn" onclick="showTab('news',this)">News</button>
        <button class="nav-btn" onclick="showTab('research',this)">Research</button>
        <button class="nav-btn" onclick="showTab('workflows',this)">Workflows</button>
        <button class="nav-btn" onclick="showTab('local',this)">Local Lab</button>
        <button class="nav-btn" onclick="showTab('saved',this)">Saved</button>
    </nav>

    <!-- Filter Bar -->
    <div class="filter-bar">
        <button class="filter-btn active" onclick="filterByScore(0, this)">All</button>
        <button class="filter-btn" onclick="filterByScore(80, this)">Hot (80+)</button>
        <button class="filter-btn" onclick="filterByScore(60, this)">Watch (60+)</button>
        <button class="filter-btn" onclick="filterByScore(40, this)">Interesting (40+)</button>
        <button class="filter-btn" onclick="filterByLocal(this)">Pi Compatible</button>
    </div>
    
    <main>
        <!-- Feed Tab -->
        <div id="feed" class="section active">
            <div class="section-header">
                <span class="section-title">High Signal Items</span>
            </div>
            <input type="text" class="search-bar" placeholder="Search all intelligence..." onkeyup="filterCards(this.value)">
            <div class="card-grid" id="feed-grid">
                {% for item in feed_items %}
                <div class="card" data-title="{{ item.title|lower }}" data-categories="{{ item.categories|join(' ') }}">
                    <div class="card-header">
                        <span class="signal-badge {% if item.signal_score >= 80 %}signal-hot{% elif item.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ item.signal_score }}</span>
                        <span class="source-badge source-{{ item.source_type }}">{{ item.source_type }}</span>
                    </div>
                    <div class="card-title">{{ item.title }}</div>
                    {% if item.description %}<div class="card-desc">{{ item.description }}</div>{% endif %}
                    <div class="card-tags">
                        {% for cat in item.categories[:3] %}<span class="tag">{{ cat }}</span>{% endfor %}
                    </div>
                    <div class="card-footer">
                        <span>{{ item.action|upper }}</span>
                        <button class="action-btn action-save" onclick="saveItem('{{ item.url }}', '{{ item.title }}', '{{ item.source_type }}')">Save</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- GitHub Tab -->
        <div id="github" class="section">
            <div class="section-header">
                <span class="section-title">GitHub Trending</span>
                <span style="font-size:0.75rem;color:var(--text-dim)">{{ github|length }} repos</span>
            </div>

            <!-- Try This Weekend -->
            <div class="brief-section" style="padding:1rem;margin-bottom:1rem">
                <div class="brief-title" style="margin-bottom:0.75rem">Try This Weekend</div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:0.75rem">
                    {% for repo in github[:3] %}
                    {% if repo.action == 'try' %}
                    <div class="brief-item" style="padding:0.75rem">
                        <div class="brief-content">
                            <div class="brief-item-title">{{ repo.title }}</div>
                            <div class="brief-meta">
                                <span>{{ repo.stars }} stars</span>
                                <span>{{ repo.language }}</span>
                                <span class="pi-badge pi-{{ repo.pi_suitability|default('partial') }}">Pi: {{ repo.pi_suitability|default('partial') }}</span>
                            </div>
                            <div class="brief-action">{{ repo.installation_complexity|default('medium') }} setup</div>
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>

            <div class="card-grid">
                {% for repo in github[:15] %}
                <div class="card">
                    <div class="card-header">
                        <span class="signal-badge {% if repo.signal_score >= 80 %}signal-hot{% elif repo.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ repo.signal_score }}</span>
                        <span class="source-badge source-github">GitHub</span>
                    </div>
                    <div class="card-title">{{ repo.title }}</div>
                    <div class="card-desc">{{ repo.description }}</div>
                    <div class="card-tags">
                        {% for cat in repo.categories[:4] %}<span class="tag">{{ cat }}</span>{% endfor %}
                    </div>
                    <div class="card-detail">
                        <span>{{ repo.stars }} stars</span>
                        <span>{{ repo.language }}</span>
                        {% if repo.license %}<span>{{ repo.license }}</span>{% endif %}
                        <span class="pi-badge pi-{{ repo.pi_suitability|default('partial') }}">Pi: {{ repo.pi_suitability|default('partial') }}</span>
                    </div>
                    <div class="card-footer">
                        <span style="font-size:0.7rem;color:var(--text-dim)">Setup: {{ repo.installation_complexity|default('medium') }}</span>
                        <button class="action-btn {% if repo.action == 'try' %}action-try{% else %}action-save{% endif %}" onclick="saveItem('{{ repo.url }}', '{{ repo.title }}', 'github')">{{ repo.action|upper }}</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Models Tab -->
        <div id="models" class="section">
            <div class="section-header">
                <span class="section-title">Model Intelligence</span>
            </div>
            <div class="model-filter-bar">
                <button class="model-filter-btn active" onclick="filterModels('all',this)">All</button>
                <button class="model-filter-btn" onclick="filterModels('local',this)">Local/Ollama</button>
                <button class="model-filter-btn" onclick="filterModels('coding',this)">Coding</button>
                <button class="model-filter-btn" onclick="filterModels('small',this)">Small (<3B)</button>
                <button class="model-filter-btn" onclick="filterModels('agent',this)">Agent-Ready</button>
                <button class="model-filter-btn" onclick="filterModels('open',this)">Open Weight</button>
            </div>
            <div class="card-grid">
                {% for model in huggingface[:20] %}
                <div class="card" data-tags="{% if model.is_local_compatible %}local{% endif %} {% if model.is_coding_model %}coding{% endif %} {% if model.is_small %}small{% endif %} {% if model.is_agent_ready %}agent{% endif %} {% if model.is_open_weight %}open{% endif %}">
                    <div class="card-header">
                        <span class="signal-badge {% if model.signal_score >= 80 %}signal-hot{% elif model.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ model.signal_score }}</span>
                        <span class="source-badge source-huggingface">Model</span>
                    </div>
                    <div class="card-title">{{ model.id }}</div>
                    <div class="model-specs">
                        {% if model.language %}<span class="model-spec">{{ model.language }}</span>{% endif %}
                        {% if model.downloads %}<span class="model-spec">{{ "{:,}".format(model.downloads) }} downloads</span>{% endif %}
                    </div>
                    <div class="card-tags">
                        {% if model.is_local_compatible %}<span class="tag" style="background:var(--accent-dim)">Local</span>{% endif %}
                        {% if model.is_coding_model %}<span class="tag">Coding</span>{% endif %}
                        {% if model.is_small %}<span class="tag">Small</span>{% endif %}
                        {% if model.is_agent_ready %}<span class="tag">Agent</span>{% endif %}
                        {% if model.is_multimodal %}<span class="tag">Multimodal</span>{% endif %}
                        {% if model.tool_calling %}<span class="tag">Tools</span>{% endif %}
                    </div>
                    {% if model.ollama_available %}
                    <div class="lab-command" style="margin-top:0.5rem">ollama run {{ model.id.split('/')[-1] }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Videos Tab -->
        <div id="videos" class="section">
            <div class="section-header">
                <span class="section-title">Watch Queue</span>
            </div>
            <div class="watch-queue">
                <div class="queue-section">
                    <div class="queue-title must">Must Watch Today</div>
                    {% for video in youtube %}
                    {% if video.watch_priority == 'high' %}
                    <div class="saved-item" style="margin-bottom:0.5rem">
                        <div class="saved-info">
                            <div class="card-title" style="font-size:0.85rem">{{ video.title }}</div>
                            <div class="card-tags">
                                <span class="signal-badge signal-hot">{{ video.signal_score }}</span>
                                <span class="tag">{{ video.source }}</span>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
                <div class="queue-section">
                    <div class="queue-title later">Watch Later</div>
                    {% for video in youtube %}
                    {% if video.watch_priority == 'medium' %}
                    <div class="saved-item" style="margin-bottom:0.5rem">
                        <div class="saved-info">
                            <div class="card-title" style="font-size:0.85rem">{{ video.title }}</div>
                            <div class="card-tags">
                                <span class="signal-badge signal-watch">{{ video.signal_score }}</span>
                                <span class="tag">{{ video.source }}</span>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
                <div class="queue-section">
                    <div class="queue-title skip">Skip</div>
                    {% for video in youtube %}
                    {% if video.watch_priority == 'low' %}
                    <div class="saved-item" style="margin-bottom:0.5rem;opacity:0.6">
                        <div class="saved-info">
                            <div class="card-title" style="font-size:0.85rem">{{ video.title }}</div>
                            <div class="card-tags">
                                <span class="signal-badge signal-low">{{ video.signal_score }}</span>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>

            <div class="section-header" style="margin-top:1.5rem">
                <span class="section-title">All Videos</span>
            </div>
            <div class="card-grid">
                {% for video in youtube[:15] %}
                <div class="card">
                    <div class="card-header">
                        <span class="signal-badge {% if video.signal_score >= 80 %}signal-hot{% elif video.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ video.signal_score }}</span>
                        <span class="source-badge source-youtube">Video</span>
                    </div>
                    <div class="card-title">{{ video.title }}</div>
                    {% if video.description %}<div class="card-desc">{{ video.description[:100] }}...</div>{% endif %}
                    <div class="card-tags">
                        <span class="tag">{{ video.source }}</span>
                        <span class="tag">{{ video.watch_priority|default('medium') }}</span>
                        {% if video.duration %}<span class="tag">{{ video.duration }}</span>{% endif %}
                    </div>
                    <div class="card-detail">
                        <span>Views: {{ video.views }}</span>
                        <span>{{ video.published }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- News Tab -->
        <div id="news" class="section">
            <div class="section-header">
                <span class="section-title">AI News</span>
            </div>
            <div class="news-categories">
                <button class="news-cat-btn active" onclick="filterNews('all',this)">All</button>
                <button class="news-cat-btn" onclick="filterNews('big-tech',this)">Big Tech</button>
                <button class="news-cat-btn" onclick="filterNews('open-source',this)">Open Source</button>
                <button class="news-cat-btn" onclick="filterNews('agents',this)">Agents</button>
                <button class="news-cat-btn" onclick="filterNews('regulation',this)">Regulation</button>
                <button class="news-cat-btn" onclick="filterNews('infrastructure',this)">Infrastructure</button>
                <button class="news-cat-btn" onclick="filterNews('safety',this)">Safety</button>
                <button class="news-cat-btn" onclick="filterNews('products',this)">Products</button>
                <button class="news-cat-btn" onclick="filterNews('tools',this)">Developer Tools</button>
            </div>
            <div class="card-grid">
                {% for news in blogs[:20] %}
                <div class="card" data-categories="{{ news.categories|join(' ') if news.categories else '' }}">
                    <div class="card-header">
                        <span class="signal-badge {% if news.signal_score >= 70 %}signal-hot{% elif news.signal_score >= 40 %}signal-watch{% else %}signal-interesting{% endif %}">{{ news.signal_score }}</span>
                        <span class="source-badge source-blogs">News</span>
                    </div>
                    <div class="card-title">{{ news.title }}</div>
                    {% if news.description %}<div class="card-desc">{{ news.description[:120] }}...</div>{% endif %}
                    <div class="card-tags">
                        {% for cat in news.categories[:3] %}<span class="tag">{{ cat }}</span>{% endfor %}
                        <span class="tag" style="{% if news.impact == 'high' %}color:var(--hot){% elif news.impact == 'medium' %}color:var(--watch){% endif %}">{{ news.impact|default('medium') }} impact</span>
                    </div>
                    <div class="card-detail">
                        <span>{{ news.source }}</span>
                        <span>{{ news.published }}</span>
                    </div>
                    {% if news.related_repos %}
                    <div class="card-detail" style="margin-top:0.5rem">
                        <span>Related: {% for repo in news.related_repos %}{{ repo }}{% if not loop.last %}, {% endif %}{% endfor %}</span>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Research Tab -->
        <div id="research" class="section">
            <div class="section-header">
                <span class="section-title">Research Papers</span>
            </div>
            <div class="paper-filters" style="display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap;">
                <button class="model-filter-btn active">All</button>
                <button class="model-filter-btn">LLM Reasoning</button>
                <button class="model-filter-btn">Agents</button>
                <button class="model-filter-btn">RAG</button>
                <button class="model-filter-btn">Evaluation</button>
                <button class="model-filter-btn">Small Models</button>
                <button class="model-filter-btn">Multimodal</button>
            </div>
            <div class="card-grid">
                {% for paper in papers[:15] %}
                <div class="card" data-categories="{{ paper.categories|join(' ') if paper.categories else '' }}">
                    <div class="card-header">
                        <span class="signal-badge {% if paper.signal_score >= 80 %}signal-hot{% elif paper.signal_score >= 50 %}signal-watch{% else %}signal-interesting{% endif %}">{{ paper.signal_score }}</span>
                        <span class="source-badge source-papers">Paper</span>
                    </div>
                    <div class="card-title">{{ paper.title }}</div>
                    {% if paper.description %}<div class="card-desc">{{ paper.description }}</div>{% endif %}
                    <div class="card-tags">
                        {% if paper.recommendation %}<span class="paper-recommendation rec-{{ paper.recommendation }}">{{ paper.recommendation }}</span>{% endif %}
                        {% if paper.has_code %}<span class="tag">Has Code</span>{% endif %}
                        {% if paper.has_model %}<span class="tag">Has Model</span>{% endif %}
                    </div>
                    {% if paper.abstract %}
                    <div class="card-detail"><span>{{ paper.abstract[:100] }}...</span></div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Agentic Workflows Tab -->
        <div id="workflows" class="section">
            <div class="workflow-section">
                <div class="workflow-title">Coding Agents</div>
                <div class="workflow-grid">
                    {% for repo in github %}
                    {% if 'agent' in repo.categories|lower or 'coding' in repo.categories|lower or 'cli' in repo.categories|lower %}
                    <div class="workflow-card">
                        <div class="workflow-card-header">
                            <span class="workflow-title-text">{{ repo.title }}</span>
                            <span class="signal-badge {% if repo.signal_score >= 80 %}signal-hot{% elif repo.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ repo.signal_score }}</span>
                        </div>
                        <div class="card-desc">{{ repo.description }}</div>
                        <div class="workflow-meta">
                            <span>{{ repo.stars }} stars</span>
                            <span>{{ repo.language }}</span>
                            <span class="maturity-badge {% if repo.maturity == 'stable' %}maturity-stable{% elif repo.maturity == 'beta' %}maturity-beta{% else %}maturity-alpha{% endif %}">{{ repo.maturity|default('alpha') }}</span>
                            <span class="security-badge {% if repo.security_risk == 'low' %}security-low{% elif repo.security_risk == 'medium' %}security-medium{% else %}security-high{% endif %}">Security: {{ repo.security_risk|default('medium') }}</span>
                        </div>
                        <div class="workflow-tags">
                            {% for cat in repo.categories[:4] %}<span class="tag">{{ cat }}</span>{% endfor %}
                            {% if repo.local_deploy %}<span class="tag" style="background:var(--accent-dim)">Local</span>{% endif %}
                        </div>
                        <div class="card-footer" style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid var(--border)">
                            <span class="action-btn {% if repo.action == 'try' %}action-try{% else %}action-save{% endif %}">{{ repo.action|upper }}</span>
                            <a href="{{ repo.url }}" target="_blank" class="action-btn" style="background:var(--border)">Open</a>
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>

            <div class="workflow-section">
                <div class="workflow-title">Browser Agents</div>
                <div class="workflow-grid">
                    {% for repo in github %}
                    {% if 'browser' in repo.categories|lower or 'automation' in repo.categories|lower %}
                    <div class="workflow-card">
                        <div class="workflow-card-header">
                            <span class="workflow-title-text">{{ repo.title }}</span>
                            <span class="signal-badge {% if repo.signal_score >= 80 %}signal-hot{% elif repo.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ repo.signal_score }}</span>
                        </div>
                        <div class="card-desc">{{ repo.description }}</div>
                        <div class="workflow-meta">
                            <span>{{ repo.stars }} stars</span>
                        </div>
                        <div class="workflow-tags">
                            {% for cat in repo.categories[:4] %}<span class="tag">{{ cat }}</span>{% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="workflow-section">
                <div class="workflow-title">Multi-Agent Frameworks</div>
                <div class="workflow-grid">
                    {% for repo in github %}
                    {% if 'multi-agent' in repo.categories|lower or 'collaboration' in repo.categories|lower %}
                    <div class="workflow-card">
                        <div class="workflow-card-header">
                            <span class="workflow-title-text">{{ repo.title }}</span>
                            <span class="signal-badge {% if repo.signal_score >= 80 %}signal-hot{% elif repo.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ repo.signal_score }}</span>
                        </div>
                        <div class="card-desc">{{ repo.description }}</div>
                        <div class="workflow-meta">
                            <span>{{ repo.stars }} stars</span>
                        </div>
                        <div class="workflow-tags">
                            {% for cat in repo.categories[:4] %}<span class="tag">{{ cat }}</span>{% endfor %}
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>

            <div class="workflow-section">
                <div class="workflow-title">Evaluation & Testing</div>
                <div class="workflow-grid">
                    {% for repo in github %}
                    {% if 'eval' in repo.categories|lower or 'benchmark' in repo.categories|lower or 'testing' in repo.categories|lower %}
                    <div class="workflow-card">
                        <div class="workflow-card-header">
                            <span class="workflow-title-text">{{ repo.title }}</span>
                            <span class="signal-badge {% if repo.signal_score >= 80 %}signal-hot{% elif repo.signal_score >= 60 %}signal-watch{% else %}signal-interesting{% endif %}">{{ repo.signal_score }}</span>
                        </div>
                        <div class="card-desc">{{ repo.description }}</div>
                        <div class="workflow-meta">
                            <span>{{ repo.stars }} stars</span>
                        </div>
                        <div class="workflow-tags">
                            {% for cat in repo.categories[:4] %}<span class="tag">{{ cat }}</span>{% endfor %}
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>

            {% if not github %}
            <div class="empty-state">
                <div class="empty-icon">🤖</div>
                <div>No agentic workflows detected yet</div>
            </div>
            {% endif %}
        </div>
        <div id="local" class="section">
            <div class="section-header">
                <span class="section-title">Local Lab - Run on Pi/Local</span>
            </div>

            <!-- Weekend Experiments -->
            <div class="brief-section" style="padding:1rem;margin-bottom:1rem">
                <div class="brief-title" style="margin-bottom:0.75rem">Weekend Experiments</div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:0.75rem">
                    {% for repo in local_items[:3] %}
                    <div class="lab-card">
                        <div class="lab-title">{{ repo.title }}</div>
                        <div class="lab-meta">{{ repo.description }}</div>
                        <div class="lab-reqs">
                            <span class="lab-req">Pi: {{ repo.pi_suitability }}</span>
                            <span class="lab-req">Setup: {{ repo.installation_complexity|default('medium') }}</span>
                            {% if repo.ram_requirement %}<span class="lab-req">RAM: {{ repo.ram_requirement }}</span>{% endif %}
                        </div>
                        {% if repo.risk %}
                        <div class="lab-risk">Risk: {{ repo.risk }}</div>
                        {% endif %}
                        <div class="lab-command" style="margin-top:0.5rem">git clone {{ repo.url }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Lightweight Models -->
            <div class="workflow-section">
                <div class="workflow-title">Lightweight Models to Try</div>
                <div class="lab-grid">
                    {% for model in huggingface %}
                    {% if model.is_small or model.is_local_compatible %}
                    <div class="lab-card">
                        <div class="lab-title">{{ model.id }}</div>
                        <div class="lab-meta">{{ model.downloads|default(0) }} downloads</div>
                        <div class="lab-reqs">
                            {% if model.is_small %}<span class="lab-req">Small</span>{% endif %}
                            {% if model.is_local_compatible %}<span class="lab-req">Local</span>{% endif %}
                        </div>
                        {% if model.ollama_available %}
                        <div class="lab-command">ollama run {{ model.id.split('/')[-1] }}</div>
                        {% endif %}
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>

            <!-- All Pi Compatible -->
            <div class="workflow-section">
                <div class="workflow-title">Pi Compatible Projects</div>
                <div class="lab-grid">
                    {% for repo in local_items %}
                    <div class="lab-card">
                        <div class="lab-title">{{ repo.title }}</div>
                        <div class="lab-meta">{{ repo.description }}</div>
                        <div class="lab-reqs">
                            <span class="lab-req">Pi: {{ repo.pi_suitability }}</span>
                            <span class="lab-req">Setup: {{ repo.installation_complexity|default('medium') }}</span>
                            <span class="lab-req">{{ repo.language }}</span>
                        </div>
                        <div class="lab-command" style="margin-top:0.5rem">git clone {{ repo.url }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            {% if not local_items %}
            <div class="empty-state">
                <div class="empty-icon">🔧</div>
                <div>No Pi-compatible items found yet</div>
                <div class="empty-message">Add projects with Pi suitability to see them here</div>
            </div>
            {% endif %}
        </div>

        <!-- Saved Tab -->
        <div id="saved" class="section">
            <div class="section-header">
                <span class="section-title">Saved Intelligence</span>
            </div>
            <div class="saved-grid" id="saved-items">
                {% for item in saved_items %}
                <div class="saved-item">
                    <div class="saved-info">
                        <div class="card-title">{{ item.title }}</div>
                        <div class="card-tags">
                            <span class="saved-status status-{{ item.status }}">{{ item.status }}</span>
                            {% for tag in item.tags %}<span class="tag">{{ tag }}</span>{% endfor %}
                        </div>
                    </div>
                    <button class="action-btn action-ignore" onclick="deleteItem({{ item.id }})">Remove</button>
                </div>
                {% endfor %}
                {% if not saved_items %}
                <div class="empty-state">
                    <div class="empty-icon">💾</div>
                    <div>No saved items yet. Click Save on any item to add it here.</div>
                </div>
                {% endif %}
            </div>
        </div>
    </main>

    <script>
        function showTab(tabId, btn) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }

        function filterCards(query) {
            const cards = document.querySelectorAll('#feed-grid .card');
            const q = query.toLowerCase();
            cards.forEach(card => {
                const title = card.dataset.title || '';
                const cats = card.dataset.categories || '';
                card.style.display = (title.includes(q) || cats.includes(q)) ? 'block' : 'none';
            });
        }

        function saveItem(url, title, source) {
            fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url, title, source_type: source})
            }).then(r => r.json()).then(d => {
                if(d.success) alert('Saved!');
            });
        }

        function deleteItem(id) {
            fetch('/api/saved/' + id, {method: 'DELETE'}).then(r => r.json()).then(d => {
                if(d.success) location.reload();
            });
        }

        function filterByScore(threshold, btn) {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const activeTab = document.querySelector('.section.active');
            const cards = activeTab.querySelectorAll('.card, .lab-card, .workflow-card');
            cards.forEach(card => {
                const scoreEl = card.querySelector('.signal-badge');
                if (scoreEl) {
                    const score = parseInt(scoreEl.textContent);
                    card.style.display = threshold === 0 || score >= threshold ? 'block' : 'none';
                }
            });
        }

        function filterByLocal(btn) {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const activeTab = document.querySelector('.section.active');
            const cards = activeTab.querySelectorAll('.card, .lab-card');
            cards.forEach(card => {
                const piBadge = card.querySelector('.pi-badge');
                card.style.display = !piBadge || piBadge.textContent.includes('yes') || piBadge.textContent.includes('partial') ? 'block' : 'none';
            });
        }

        function filterModels(filter, btn) {
            document.querySelectorAll('.model-filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const cards = document.querySelectorAll('#models .card');
            cards.forEach(card => {
                const tags = card.dataset.tags || '';
                card.style.display = filter === 'all' || tags.includes(filter) ? 'block' : 'none';
            });
        }

        function filterNews(category, btn) {
            document.querySelectorAll('.news-cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const cards = document.querySelectorAll('#news .card');
            cards.forEach(card => {
                const cats = card.dataset.categories || '';
                card.style.display = category === 'all' || cats.includes(category) ? 'block' : 'none';
            });
        }

        function updateStatus(id, status) {
            fetch('/api/saved/' + id + '/status', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({status})
            }).then(r => r.json()).then(d => {
                if(d.success) location.reload();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', e => {
            if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            if(e.key === '/') { e.preventDefault(); document.querySelector('.search-bar').focus(); }
            if(e.key === 's' && !e.ctrlKey) { e.preventDefault(); showTab('saved', document.querySelectorAll('.nav-btn')[9]); }
            if(e.key === 'f') { e.preventDefault(); showTab('feed', document.querySelectorAll('.nav-btn')[0]); }
            if(e.key === 'g') { e.preventDefault(); showTab('github', document.querySelectorAll('.nav-btn')[1]); }
            if(e.key === 'm') { e.preventDefault(); showTab('models', document.querySelectorAll('.nav-btn')[2]); }
            if(e.key === 'v') { e.preventDefault(); showTab('videos', document.querySelectorAll('.nav-btn')[3]); }
            if(e.key === 'n') { e.preventDefault(); showTab('news', document.querySelectorAll('.nav-btn')[4]); }
            if(e.key === 'r') { e.preventDefault(); showTab('research', document.querySelectorAll('.nav-btn')[5]); }
            if(e.key === 'w') { e.preventDefault(); showTab('workflows', document.querySelectorAll('.nav-btn')[6]); }
            if(e.key === 'l') { e.preventDefault(); showTab('local', document.querySelectorAll('.nav-btn')[8]); }
            if(e.key === 'd') { e.preventDefault(); generateDigest(); }
            if(e.key === 'Escape') { document.querySelector('.search-bar').blur(); }
        });

        function generateDigest() {
            fetch('/api/digest').then(r => r.json()).then(d => {
                if(d.digest) {
                    const blob = new Blob([d.digest], {type: 'text/markdown'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'digest-' + new Date().toISOString().split('T')[0] + '.md';
                    a.click();
                }
            });
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
    """Main dashboard page"""
    scored_data = load_scored_data()
    
    # Prepare feed items (all high-signal items combined)
    feed_items = []
    for source_type, items in scored_data.items():
        if source_type in ["github", "huggingface", "youtube", "blogs", "papers"]:
            for item in items:
                if item.get("signal_score", 0) >= 40:
                    feed_items.append({**item, "source_type": source_type})
    
    feed_items.sort(key=lambda x: x.get("signal_score", 0), reverse=True)
    
    # Get local/pi-suitable items
    local_items = [r for r in scored_data.get("github", []) if r.get("pi_suitability") in ["yes", "partial"]]
    local_items.sort(key=lambda x: x.get("signal_score", 0), reverse=True)
    
    # Get saved items
    saved_items = []
    if intel_db:
        try:
            saved_items = intel_db.get_saved_items()
        except:
            pass
    
    # Format last updated
    last_updated = scored_data.get("last_updated", "Unknown")
    if last_updated != "Unknown":
        try:
            dt = datetime.fromisoformat(last_updated)
            last_updated = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass
    
    # Get top 5 brief items in Python
    brief_items = scored_data.get("executive_brief", {}).get("items", [])[:5] if scored_data.get("executive_brief") else []
    
    return render_template_string(HTML,
        github=scored_data.get("github", []),
        huggingface=scored_data.get("huggingface", []),
        youtube=scored_data.get("youtube", []),
        blogs=scored_data.get("blogs", []),
        papers=scored_data.get("papers", []),
        feed_items=feed_items[:30],
        local_items=local_items[:6],
        saved_items=saved_items,
        executive_brief=scored_data.get("executive_brief"),
        last_updated=last_updated
    )


@app.route("/api/data")
def api_data():
    """API endpoint for raw data"""
    return jsonify(load_data())


@app.route("/api/scored")
def api_scored():
    """API endpoint for scored data"""
    return jsonify(load_scored_data())


@app.route("/api/save", methods=["POST"])
def api_save():
    """Save an item"""
    if not intel_db:
        return jsonify({"success": False, "error": "Database not available"})
    
    data = request.json
    item_id = intel_db.save_item({
        "title": data.get("title", ""),
        "url": data.get("url", ""),
        "source": data.get("source", ""),
        "source_type": data.get("source_type", ""),
        "category": data.get("category", ""),
        "signal_score": data.get("signal_score", 0)
    })
    return jsonify({"success": True, "id": item_id})


@app.route("/api/saved/<int:item_id>", methods=["DELETE"])
def api_delete_saved(item_id):
    """Delete a saved item"""
    if not intel_db:
        return jsonify({"success": False, "error": "Database not available"})
    
    intel_db.delete_item(item_id)
    return jsonify({"success": True})


@app.route("/api/saved/<int:item_id>/status", methods=["PUT"])
def api_update_status(item_id):
    """Update saved item status"""
    if not intel_db:
        return jsonify({"success": False, "error": "Database not available"})
    
    data = request.json
    status = data.get("status", "to_read")
    intel_db.update_status(item_id, status)
    return jsonify({"success": True})


@app.route("/api/saved")
def api_get_saved():
    """Get all saved items"""
    if not intel_db:
        return jsonify({"items": []})
    
    return jsonify({"items": intel_db.get_saved_items()})


@app.route("/api/llm-summarize", methods=["POST"])
def api_llm_summarize():
    """Summarize an item using Ollama"""
    data = request.json
    text = data.get("text", "")
    item_type = data.get("type", "general")
    
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "minimax-m2.5:cloud")
    
    prompt = f"""Analyze this AI {item_type} and return JSON:
{{
  "summary": "2-3 sentence summary",
  "why_matters": "why this is important",
  "category": "one word category",
  "signal_score": 0-100,
  "action": "read|try|save|ignore",
  "pi_suitable": "yes|partial|no"
}}
Content: {text[:500]}
"""
    
    try:
        import requests as req
        resp = req.post(f"{ollama_url}/api/generate", json={"model": model, "prompt": prompt, "format": "json"}, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            return jsonify({"success": True, "summary": json.loads(result.get("response", "{}"))})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False, "error": "Ollama not available"})


@app.route("/api/digest")
def api_digest():
    """Generate and return daily digest"""
    if not HAS_SCORE_ENGINE:
        return jsonify({"error": "Scoring engine not available"})
    
    from digest_generator import DailyDigestGenerator
    generator = DailyDigestGenerator()
    data = load_data()
    digest = generator.generate_digest(data)
    return jsonify({"digest": digest})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)