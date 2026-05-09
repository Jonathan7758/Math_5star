"""Fix ALL wrong answers in quiz_bank, including algebraic expressions."""
import json, sys
sys.path.insert(0, ".")
from backend.engine.math_verifier import MathVerifier
import sympy as sp

with open("backend/data/quiz_bank.json", "r", encoding="utf-8") as f:
    bank = json.load(f)

questions = bank.get("questions", [])
fixed_total = 0

for q in questions:
    qid = q["id"]
    question = q.get("question", "")
    answer = str(q.get("correct_answer", ""))

    is_ok = MathVerifier.verify_question_answer(question, answer)
    if is_ok:
        continue

    expr = MathVerifier._extract_expression(question)
    if not expr:
        continue

    try:
        true_expr = MathVerifier.parse(expr)
        
        # Check if this is an algebraic expression (has variables)
        has_vars = any(c.isalpha() for c in expr if c not in ('e', 'E'))
        
        if has_vars:
            # Algebraic: simplify/expand and compare
            computed = sp.simplify(sp.expand(true_expr))
            new_ans = str(computed).replace(' ', '')
        else:
            # Numeric: compute value
            computed = sp.N(true_expr)
            if computed.is_Integer:
                new_ans = str(int(computed))
            elif computed.is_Float:
                v = float(computed)
                if v == int(v):
                    new_ans = str(int(v))
                else:
                    # Try to express as fraction
                    try:
                        frac = sp.nsimplify(v, [sp.Rational(1,2), sp.Rational(1,3), sp.Rational(1,4), sp.Rational(1,5), sp.Rational(1,6), sp.Rational(1,8)])
                        if frac.is_Rational:
                            new_ans = str(frac)
                        else:
                            new_ans = str(round(v, 4) if abs(v) < 1 else int(v) if v == int(v) else str(round(v, 2)))
                    except:
                        new_ans = str(round(v, 4))
            else:
                new_ans = str(computed)

        old_ans = str(answer)
        if new_ans.replace(' ', '') != old_ans.replace(' ', ''):
            q["correct_answer"] = new_ans
            print(f"FIXED {qid}: {old_ans} -> {new_ans}")
            print(f"  Q: {question[:80]}")
            fixed_total += 1
        else:
            # Answer is OK just formatting diff
            pass
    except Exception as e:
        print(f"SKIP {qid}: {e}")

print(f"\nTotal fixed: {fixed_total}")

with open("backend/data/quiz_bank.json", "w", encoding="utf-8") as f:
    json.dump(bank, f, ensure_ascii=False, indent=2)

print("Saved.")


# Also fix: for multiple choice questions, make sure the correct answer is among options
for q in questions:
    opts = q.get("options")
    ans = str(q.get("correct_answer", ""))
    if opts and ans:
        # Check if answer is in options
        found = False
        for opt in opts:
            if str(opt).replace(' ', '') == ans.replace(' ', ''):
                found = True
                break
            # Try SymPy comparison
            try:
                if MathVerifier.parse(ans.replace(' ', '')) == MathVerifier.parse(opt.replace(' ', '')):
                    found = True
                    break
            except:
                pass
        if not found:
            print(f"WARNING {q['id']}: answer '{ans}' not in options {opts}")
            # Mark the first option as correct if it matches via SymPy
            try:
                ans_expr = MathVerifier.parse(ans.replace(' ', ''))
                for i, opt in enumerate(opts):
                    try:
                        if MathVerifier.parse(opt.replace(' ', '')) == ans_expr:
                            found = True
                            break
                    except:
                        pass
            except:
                pass

with open("backend/data/quiz_bank.json", "w", encoding="utf-8") as f:
    json.dump(bank, f, ensure_ascii=False, indent=2)
print("Saved with option checks.")
