"""Scan quiz_bank.json for questions with wrong answers."""
import json
import sys
sys.path.insert(0, ".")
from backend.engine.math_verifier import MathVerifier
import sympy as sp

with open("backend/data/quiz_bank.json", "r", encoding="utf-8") as f:
    bank = json.load(f)

questions = bank.get("questions", [])
bad = []
good = []
skipped = []

for q in questions:
    qid = q["id"]
    question = q.get("question", "")
    answer = q.get("correct_answer", "")
    
    is_ok = MathVerifier.verify_question_answer(question, answer)
    
    if is_ok:
        good.append(qid)
    else:
        # Try to extract expression and compute true answer
        expr = MathVerifier._extract_expression(question)
        if expr:
            try:
                true_val = sp.N(sp.simplify(MathVerifier.parse(expr)))
                cleaned = MathVerifier._clean_answer(answer)
                proposed = MathVerifier.parse(cleaned)
                bad.append({
                    "id": qid,
                    "question": question[:80],
                    "stored_answer": answer,
                    "proposed": str(proposed),
                    "computed_true": str(true_val),
                    "expression": expr,
                })
            except:
                skipped.append({"id": qid, "reason": "parse_error", "expr": expr, "ans": answer})
        else:
            skipped.append({"id": qid, "reason": "no_expr", "question": question[:60], "ans": answer})

print(f"GOOD: {len(good)}")
print(f"BAD: {len(bad)}")
print(f"SKIPPED: {len(skipped)}")

if bad:
    print("\n=== WRONG ANSWERS ===")
    for b in bad:
        print(f"\n  [{b['id']}] {b['question'][:60]}")
        print(f"    Stored: {b['stored_answer']}")
        print(f"    True:   {b['computed_true']}")
        print(f"    Expr:   {b['expression']}")

if skipped:
    print(f"\n=== SKIPPED ({len(skipped)}) ===")
    for s in skipped[:5]:
        print(f"  [{s['id']}] {s['reason']}: {s.get('question','')[:60]}")
