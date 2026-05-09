import json
import sympy as sp

with open("backend/data/quiz_bank.json", "r", encoding="utf-8") as f:
    bank = json.load(f)

# Find K11 (quadratic expressions) questions
k11 = [q for q in bank["questions"] if q.get("knowledge_point_id") == "K11"]
print(f"K11 questions: {len(k11)}")

# For each K11 question, try to verify answer with SymPy
for q in k11:
    qid = q["id"]
    question = q.get("question", "")
    stored_ans = str(q.get("correct_answer", ""))
    
    # Extract the algebraic expression
    # Try to find pattern like (x+3)(x-5) or expand/simplify
    import re
    
    # Try to simplify the expression
    try:
        # Extract expression between specific markers
        simplified = sp.simplify(question.replace("展开并化简","").replace("展开并化简:","").replace("Expand and simplify","").strip())
        computed = str(sp.expand(sp.simplify(simplified)))
    except:
        computed = "?"
    
    match = stored_ans == computed
    status = "OK" if match else f"MISMATCH (computed: {computed})"
    print(f"\n  {qid}: {status}")
    print(f"    Q: {question[:80]}")
    print(f"    Stored: {stored_ans}")
    if not match:
        print(f"    Computed: {computed}")
