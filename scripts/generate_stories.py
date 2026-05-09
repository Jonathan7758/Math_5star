"""
Pre-generate storytelling versions for all quiz bank questions.
Run: set LLM_API_KEY=sk-... && python scripts/generate_stories.py
"""
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

if not os.getenv("LLM_API_KEY"):
    print("ERROR: Set LLM_API_KEY first")
    sys.exit(1)

from backend.agents.storyteller_agent import storyteller
from backend.config import QUIZ_BANK_PATH


async def main():
    with open(QUIZ_BANK_PATH, "r", encoding="utf-8") as f:
        bank = json.load(f)

    questions = bank.get("questions", [])
    print(f"Generating stories for {len(questions)} questions...")

    count = 0
    for i, q in enumerate(questions):
        qid = q.get("id", "")
        qtext = q.get("question", "")
        if not qid or not qtext:
            continue
        try:
            await storyteller.get_story(qid, qtext)
            count += 1
            print(f"  [{i+1}/{len(questions)}] {qid}: done")
            # Small delay between requests to avoid rate limiting
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"  [{i+1}/{len(questions)}] {qid}: ERROR - {e}")

    print(f"\nDone! Generated {count} stories. Cache saved to backend/data/story_cache.json")


if __name__ == "__main__":
    asyncio.run(main())
