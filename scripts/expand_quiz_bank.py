import asyncio
import json
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

# Set BEFORE importing backend.config (reads env var at import time)
if not os.getenv("LLM_API_KEY"):
    print("ERROR: LLM_API_KEY environment variable not set.")
    print("Usage: $env:LLM_API_KEY='sk-...'; python scripts/expand_quiz_bank.py")
    sys.exit(1)

from backend.agents.llm_agent import LLMAgent
from backend.config import KNOWLEDGE_GRAPH_PATH, QUIZ_BANK_PATH
from backend.engine.knowledge_graph import KnowledgeGraph

TARGET_PER_KP = 10

async def main():
    kg = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
    kg.load()

    with open(QUIZ_BANK_PATH, "r", encoding="utf-8") as f:
        bank = json.load(f)

    existing = bank.get("questions", [])
    existing_ids = {q["id"] for q in existing}

    count_by_kp = {}
    max_lvl = {}
    for q in existing:
        kp = q["knowledge_point_id"]
        count_by_kp[kp] = count_by_kp.get(kp, 0) + 1
        max_lvl[kp] = max(max_lvl.get(kp, 0), q.get("level", 1))

    total_new = 0
    existing_list = list(existing)  # mutable copy for incremental save

    def save_bank():
        """Save incrementally so resuming works after timeout."""
        all_qs = existing_list.copy()
        for i in range(len(all_qs) - 1, 0, -1):
            j = random.randint(0, i)
            all_qs[i], all_qs[j] = all_qs[j], all_qs[i]
        bank_out = {"questions": all_qs}
        with open(QUIZ_BANK_PATH, "w", encoding="utf-8") as f:
            json.dump(bank_out, f, ensure_ascii=False, indent=2)

    for node in kg.digraph.nodes:
        kp_id = node
        try:
            node_data = kg.get_node(kp_id)
        except KeyError:
            node_data = {"id": kp_id, "name": kp_id, "grade": "Y7", "description": ""}

        current = count_by_kp.get(kp_id, 0)
        need = max(0, TARGET_PER_KP - current)
        if need == 0:
            print(f"  {kp_id} ({node_data.get('name')}): {current}/{TARGET_PER_KP} - skip")
            continue

        print(f"  {kp_id} ({node_data.get('name')}): {current}/{TARGET_PER_KP} - generating {need}")

        generated = 0
        attempts = 0
        max_attempts = need * 3

        while generated < need and attempts < max_attempts:
            attempts += 1
            level = max_lvl.get(kp_id, 1)
            if generated >= need // 2:
                level += 1

            q = await LLMAgent.generate_question(
                kp_name=node_data.get("name", kp_id),
                kp_description=node_data.get("description", ""),
                grade=node_data.get("grade", "Y7"),
                level=min(level, 2),
            )

            if q is None:
                print(f"    [attempt {attempts}] sympy fail, retry")
                continue

            qid = f"Q-{kp_id}-L{q.get('type','num')[:1]}-{generated + current + 1:02d}"
            if qid in existing_ids:
                continue

            new_q = {
                "id": qid,
                "knowledge_point_id": kp_id,
                "level": level,
                "type": q.get("type", "numeric"),
                "question": q["question"],
                "correct_answer": q["correct_answer"],
                "hints": q.get("hints", []),
                "explanation": q.get("explanation", ""),
            }
            if q.get("type") == "multiple_choice" and q.get("options"):
                new_q["options"] = q["options"]

            existing_list.append(new_q)
            existing_ids.add(qid)
            generated += 1
            total_new += 1
            print(f"    ✅ [{generated}/{need}] {q.get('type', '?')}: {q.get('question', '')[:60]}...")

        # Incremental save after each KP batch
        save_bank()
        print(f"  → added {generated} new (saved)")

    print(f"\nTotal: {len(existing_list)} questions ({total_new} new)")
    print("Saved to", QUIZ_BANK_PATH)

if __name__ == "__main__":
    asyncio.run(main())
