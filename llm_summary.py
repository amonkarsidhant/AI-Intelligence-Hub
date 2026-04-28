#!/usr/bin/env python3
"""LLM-powered summary using Ollama cloud model."""

import json
import requests


def get_ollama_summary(data):
    """Generate summary using Ollama cloud API (faster)."""
    github = data.get("github", [])[:3]
    youtube = data.get("youtube", [])[:2]
    blogs = data.get("blogs", [])[:3]

    repo_info = "\n".join([f"- {r['title']}" for r in github])
    news_info = "\n".join([f"- {b['title']}" for b in blogs])

    prompt = f"""Write 2 sentences about today's AI news:

Trending: {repo_info}
News: {news_info}

Brief summary:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "minimax-m2.5:cloud",
                "prompt": prompt,
                "stream": False,
                "options": {"max_tokens": 120, "temperature": 0.3},
            },
            timeout=20,
        )
        if response.status_code == 200:
            result = response.json()
            summary = result.get("response", "").strip()
            summary = summary.replace("\n", " ").strip()
            if len(summary) > 140:
                summary = summary[:140] + "..."
            return summary
    except Exception as e:
        print(f"Error: {e}")

    return f"{len(github)} repos • {len(blogs)} stories"


if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.environ.get("DATA_DIR", os.path.join(base_dir, "data"))
    data_path = os.environ.get("DATA_FILE", os.path.join(data_dir, "data.json"))
    with open(data_path) as f:
        data = json.load(f)

    summary = get_ollama_summary(data)
    print("Summary:", summary)
