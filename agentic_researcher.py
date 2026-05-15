#!/usr/bin/env python3
"""
Agentic Researcher for DailyDex.
Goes beyond aggregation to perform deep-dive synthesis on trending topics.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict

# Internal imports
from data_models import IntelligenceDB, IntelligenceJSON
import llm_summary
import creator_intelligence

class AgenticResearcher:
    def __init__(self):
        self.db = IntelligenceDB()
        self.json_store = IntelligenceJSON()
        
    def perform_daily_research(self, top_n: int = 3):
        """Identify top trends and generate deep-dive content briefs."""
        print(f"[*] Starting Agentic Research session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 1. Identify what's actually trending in the local database
        trends = self.db.get_trending_keywords(limit=10)
        if not trends:
            print("[!] No trends found. Falling back to default focus areas.")
            trends = [{"keyword": k} for k in ["Agentic AI", "Local LLMs", "Coding Agents"]]
            
        research_targets = [t['keyword'] for t in trends[:top_n]]
        print(f"[*] Top research targets: {', '.join(research_targets)}")
        
        # 2. For each target, gather related items and synthesize
        for target in research_targets:
            self._research_topic(target)
            
    def _research_topic(self, topic: str):
        """Synthesize a deep brief for a specific topic cluster."""
        print(f"[*] Deep-diving into: {topic}")
        
        # Gather local context
        items = self.db.get_saved_items() # Simplified: could filter by topic
        related_items = [i for i in items if topic.lower() in (i.get('title') or '').lower() or topic.lower() in (i.get('notes') or '').lower()]
        
        # Build a research context for the LLM
        context = "\n".join([f"- {i.get('title')} ({i.get('url')})" for i in related_items[:5]])
        
        system_prompt = f"""You are a Senior AI Content Strategist. 
You are performing a 'Trend Synthesis' for the topic: '{topic}'.
Your goal is to find the 'Hidden Signal' across multiple news items and repositories.

Return a JSON object:
- strategic_title: A high-click-rate title.
- core_narrative: (2 sentences) The fundamental shift happening in this topic.
- hook: A banger opening hook.
- narrative_beats: 4-5 points for a video/article outline.
- thumbnail_concepts: 3 visual ideas for a thumbnail.
- production_value: Why this is worth making *now*.

Output MUST be valid JSON."""

        prompt = f"Topic: {topic}\nRelated Context:\n{context}\n\nSynthesize a 'Gold' Content Brief:"
        
        response = llm_summary.query_llm(prompt, system_prompt)
        if response:
            try:
                # Extract JSON
                if "{" in response and "}" in response:
                    json_str = response[response.find("{"):response.rfind("}")+1]
                    brief = json.loads(json_str)
                    self._save_brief_to_pipeline(topic, brief)
                    print(f"[+] Successfully synthesized brief for {topic}")
            except Exception as e:
                print(f"[!] Synthesis failed for {topic}: {e}")

    def _save_brief_to_pipeline(self, topic: str, brief: Dict):
        """Inject the synthesized brief into the creator pipeline."""
        item = {
            "title": brief.get("strategic_title", f"Deep Dive: {topic}"),
            "url": f"https://dailydex.internal/research/{topic.lower().replace(' ', '-')}",
            "source": "Agentic Researcher",
            "source_type": "research",
            "category": "Strategic Synthesis",
            "signal_score": 90,
            "creator_score": 95,
            "pipeline_type": "creator",
            "status": "idea",
            "working_title": brief.get("strategic_title"),
            "hook": brief.get("hook"),
            "format": "Video",
            "outline": json.dumps(brief.get("narrative_beats", [])),
            "thumbnail_text": ", ".join(brief.get("thumbnail_concepts", [])),
            "notes": brief.get("core_narrative"),
            "tags": json.dumps(brief.get("tags", [])),
            "created_at": datetime.now().isoformat()
        }
        self.db.save_item(item)

if __name__ == "__main__":
    researcher = AgenticResearcher()
    researcher.perform_daily_research()
