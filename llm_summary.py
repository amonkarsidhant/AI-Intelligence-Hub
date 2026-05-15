#!/usr/bin/env python3
"""LLM-powered summary and enrichment using Ollama cloud model."""

import json
import requests
import os

# Configuration
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "minimax-m2.5:cloud")

def query_ollama(prompt, system_prompt=None):
    """Generic helper to query Ollama"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"max_tokens": 500, "temperature": 0.3},
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
    except Exception as e:
        print(f"Ollama Error: {e}")
    return None

def get_ollama_summary(data):
    """Generate global summary for the daily brief."""
    github = data.get("github", [])[:3]
    blogs = data.get("blogs", [])[:3]

    repo_info = "\n".join([f"- {r['title']}" for r in github])
    news_info = "\n".join([f"- {b['title']}" for b in blogs])

    prompt = f"""Write 2 sentences about today's AI news:
Trending: {repo_info}
News: {news_info}
Brief summary:"""

    summary = query_ollama(prompt)
    if summary:
        summary = summary.replace("\n", " ").strip()
        if len(summary) > 160:
            summary = summary[:160] + "..."
        return summary

    return f"{len(github)} repos • {len(blogs)} stories"

def get_item_enrichment(item):
    """Generate deep dive insight, hooks, and outline for a specific high-signal item."""
    title = item.get("title", "")
    description = item.get("description", item.get("abstract", ""))
    source = item.get("source", "")
    
    system_prompt = """You are an expert AI Content Researcher. Your goal is to extract the 'Signal' from a news item.
Return a JSON object with:
- insight: A deep dive into the impact and technical value (2 sentences).
- hooks: A list of 3 content hooks (Statistic-based, Problem/Solution, Curiosity).
- outline: 3-5 bullet points for a content outline.
- tags: 3 relevant tags.

Ensure the output is valid JSON."""

    prompt = f"Source: {source}\nTitle: {title}\nDescription: {description}\n\nEnrich this item:"
    
    response_text = query_ollama(prompt, system_prompt)
    if response_text:
        try:
            # Try to extract JSON if LLM added preamble
            if "{" in response_text and "}" in response_text:
                json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
                return json.loads(json_str)
        except:
            pass
    
    return {
        "insight": "High-interest development in AI ecosystem.",
        "hooks": [f"Why {title} matters today.", "The problem this solves.", "Check this out."],
        "outline": [f"Introduction to {title}", "Key features", "Final thoughts"],
        "tags": ["AI", "Tech", source]
    }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.environ.get("DATA_DIR", os.path.join(base_dir, "data"))
    data_path = os.environ.get("DATA_FILE", os.path.join(data_dir, "data.json"))
    
    if os.path.exists(data_path):
        with open(data_path) as f:
            data = json.load(f)

        summary = get_ollama_summary(data)
        print("Global Summary:", summary)
        
        # Test enrichment on first github item
        if data.get("github"):
            print("\nEnriching first GitHub item...")
            enrichment = get_item_enrichment(data["github"][0])
            print(json.dumps(enrichment, indent=2))
