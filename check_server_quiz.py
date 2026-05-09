import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

# Download server quiz bank
sftp = c.open_sftp()
with sftp.open("/opt/math-home-tutor/backend/data/quiz_bank.json", "r") as f:
    server_bank = json.loads(f.read().decode("utf-8"))
sftp.close()

# Search for the quadratic expression question
questions = server_bank.get("questions", [])
matches = [q for q in questions if "x+3" in q.get("question","") and "x-5" in q.get("question","")]
print(f"Found: {len(matches)}")

for q in matches:
    print(f"\nID: {q['id']}")
    print(f"Q: {q['question']}")
    print(f"Stored answer: {q.get('correct_answer')}")
    print(f"Options: {q.get('options')}")

# Also check: what's the correct answer?
# (x+3)(x-5) - (x-2)(x+1) = -x - 13
print("\nExpected correct answer: -x - 13")

# Scan all K11 questions (quadratic expressions)
k11_qs = [q for q in questions if q.get("knowledge_point_id") == "K11"]
print(f"\nAll K11 questions: {len(k11_qs)}")
for q in k11_qs:
    from backend.engine.math_verifier import MathVerifier
    import sys
    sys.path.insert(0, ".")
    try:
        ok = MathVerifier.verify_question_answer(q["question"], q.get("correct_answer", ""))
        status = "OK" if ok else "WRONG"
    except:
        status = "ERR"
    print(f"  [{status}] {q['id']}: {q.get('correct_answer')} | {q['question'][:60]}")

c.close()
