"""
Storyteller Agent — rewrites math questions with kid-friendly visual themes.
Uses DeepSeek API for generation, caches results in JSON per question_id.
"""
import json
import os
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from backend.agents.llm_agent import LLMAgent
from backend.engine.math_verifier import MathVerifier
from backend.config import DATA_DIR

STORY_CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "story_cache.json"

THEMES = {
    "fruit_shop": {"name": "水果店", "icon": "🍎", "context": "a fruit shop with apples, oranges, and bananas"},
    "animals":    {"name": "动物园", "icon": "🐾", "context": "a zoo or farm with cute animals"},
    "space":      {"name": "太空冒险", "icon": "🚀", "context": "outer space with rockets, planets, and stars"},
    "game_world": {"name": "游戏世界", "icon": "🎮", "context": "a video game with coins, gems, and scores"},
    "baking":     {"name": "烘焙厨房", "icon": "🧁", "context": "a kitchen baking cookies, cakes, and pastries"},
    "sports":     {"name": "运动场", "icon": "🏀", "context": "a sports game with balls, teams, and points"},
    "ocean":      {"name": "海底世界", "icon": "🌊", "context": "the ocean floor with fish, shells, and coral"},
    "carnival":   {"name": "游乐园", "icon": "🎪", "context": "a carnival with prizes, tickets, and rides"},
}

PROMPT_TEMPLATE = """You are a creative math tutor for children aged 8-12. Rewrite the math question below into a story-based version that is engaging and easy to visualize.

Theme: {theme_name} ({theme_context})
Target age: 8-12 years old

IMPORTANT RULES:
1. Keep the mathematical structure EXACTLY the same — same numbers, same operations
2. Use short sentences, simple words
3. Replace abstract numbers with concrete objects from the theme
4. Add a friendly character (小明, 小红, 小动物 etc.)
5. The final question should clearly ask for the mathematical answer
6. Keep under 80 characters of Chinese text
7. Output ONLY the rewritten question, no explanations

Original question: {question}

Rewritten question:"""


@dataclass
class StorytellerAgent:
    cache: dict = field(default_factory=dict)

    def _load_cache(self):
        if not self.cache:
            if STORY_CACHE_PATH.exists():
                try:
                    with open(STORY_CACHE_PATH, "r", encoding="utf-8") as f:
                        self.cache = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    self.cache = {}
        return self.cache

    def _save_cache(self):
        STORY_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STORY_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    async def get_story(self, question_id: str, question_text: str, theme_key: Optional[str] = None) -> dict:
        """Get story version for a question. Uses cache first, calls LLM on miss."""
        cache = self._load_cache()

        # Return cached if exists
        if question_id in cache:
            cached = cache[question_id]
            # Optionally re-theme if different theme requested
            if theme_key and cached.get("theme") != theme_key:
                pass  # Fall through to regenerate
            else:
                return cached

        # Pick random theme
        if not theme_key:
            theme_key = random.choice(list(THEMES.keys()))
        theme = THEMES.get(theme_key, THEMES["fruit_shop"])

        # Generate via LLM
        result = await self._generate(question_text, theme_key, theme)

        # Cache it
        cache[question_id] = result
        self._save_cache()

        return result

    async def _generate(self, question_text: str, theme_key: str, theme: dict) -> dict:
        """Call DeepSeek to rewrite the question."""
        prompt = PROMPT_TEMPLATE.format(
            theme_name=theme["name"],
            theme_context=theme["context"],
            question=question_text,
        )

        if not LLMAgent.is_configured():
            return self._fallback(question_text, theme_key, theme, generated=False)

        try:
            import httpx
            from backend.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                        "max_tokens": 300,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            if content and len(content) > 5:
                return {
                    "question_id": "",
                    "story_question": f"{theme['icon']} {content}",
                    "theme": theme_key,
                    "theme_name": theme["name"],
                    "theme_icon": theme["icon"],
                    "generated": True,
                }
        except Exception as e:
            print(f"Storyteller LLM error: {e}")

        return self._fallback(question_text, theme_key, theme, generated=False)

    def _fallback(self, question_text: str, theme_key: str, theme: dict, generated: bool) -> dict:
        return {
            "question_id": "",
            "story_question": f"{theme['icon']} {question_text}",
            "theme": theme_key,
            "theme_name": theme["name"],
            "theme_icon": theme["icon"],
            "generated": generated,
        }

    async def batch_generate(self, questions: list[dict], theme_key: Optional[str] = None) -> int:
        """Pre-generate stories for a list of questions. Returns count generated."""
        count = 0
        for q in questions:
            qid = q.get("id", "")
            qtext = q.get("question", "")
            if qid and qtext:
                await self.get_story(qid, qtext, theme_key)
                count += 1
                print(f"  {qid}: done")
        return count

    def get_themes(self) -> list[dict]:
        """Return available themes for frontend selection."""
        return [
            {"key": k, "name": v["name"], "icon": v["icon"]}
            for k, v in THEMES.items()
        ]


# Singleton
storyteller = StorytellerAgent()
