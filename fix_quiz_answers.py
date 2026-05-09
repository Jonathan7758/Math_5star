"""Fix wrong answers in quiz_bank.json"""
import json, sys, os
sys.path.insert(0, ".")
from backend.engine.math_verifier import MathVerifier
import sympy as sp

with open("backend/data/quiz_bank.json", "r", encoding="utf-8") as f:
    bank = json.load(f)

questions = bank.get("questions", [])
fixed = 0

for q in questions:
    qid = q["id"]
    question = q.get("question", "")
    answer = q.get("correct_answer", "")

    is_ok = MathVerifier.verify_question_answer(question, answer)
    if is_ok:
        continue

    expr = MathVerifier._extract_expression(question)
    if not expr:
        continue

    try:
        true_val = sp.N(sp.simplify(MathVerifier.parse(expr)))
        new_ans = str(int(true_val)) if true_val == int(true_val) else str(true_val)
        # Simplify fraction if possible
        try:
            frac = sp.nsimplify(true_val, [sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(1, 4), sp.Rational(1, 5)])
            if frac.is_Rational:
                new_ans = str(frac)
        except:
            pass

        old_ans = str(answer)
        q["correct_answer"] = new_ans
        print(f"[FIXED] {qid}: {old_ans} -> {new_ans}")
        print(f"  Q: {question[:80]}")
        print(f"  Expr: {expr}")
        fixed += 1
    except Exception as e:
        print(f"[SKIP] {qid}: {e}")

print(f"\nFixed: {fixed} questions")

with open("backend/data/quiz_bank.json", "w", encoding="utf-8") as f:
    json.dump(bank, f, ensure_ascii=False, indent=2)

print("Saved quiz_bank.json")
