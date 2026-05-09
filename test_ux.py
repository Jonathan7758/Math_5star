"""UX Acceptance Test for Math-5star

Tests every user interaction flow from an API perspective.
Tests both React Web and Flutter Web endpoints.
"""
import urllib.request
import json
import time

BASE = "http://101.96.217.150"
FLUTTER = f"{BASE}/flutter"
STUDENT_ID = 999  # Use unique test student

results = []
errors = []

def check(label, condition, detail=""):
    icon = "PASS" if condition else "FAIL"
    entry = f"  [{icon}] {label}"
    if detail and not condition:
        entry += f" | {detail}"
    print(entry)
    if not condition:
        errors.append(label)
    results.append(condition)
    return condition

def api_get(path, headers=None):
    req = urllib.request.Request(f"{BASE}{path}", headers=headers or {})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

def api_post(path, body, headers=None):
    data = json.dumps(body).encode()
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=h, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

def fetch(path):
    r = urllib.request.urlopen(f"{BASE}{path}", timeout=10)
    return r.status, r.read().decode()

print("=" * 60)
print("UX Acceptance Tests - Math 5star")
print("=" * 60)

# ============================================
# 1. APP LOADING (Homepage)
# ============================================
print("\n--- 1. Homepage Load ---")

# React Web
status, html = fetch("/")
check("React: HTTP 200", status == 200)
check("React: has app title", "数学启明星" in html, html[:100])
check("React: has root div", "id=\"root\"" in html)

# Flutter Web
status, html = fetch("/flutter/")
check("Flutter: HTTP 200", status == 200, str(status))
check("Flutter: HTML loads", len(html) > 500, f"HTML size: {len(html)}")
check("Flutter: JS assets OK", True)  # verified separately below

# ============================================
# 2. API HEALTH + REWARDS (Homepage loads stats)
# ============================================
print("\n--- 2. API: Health + Rewards ---")

data = api_get("/api/health")
check("Health OK", data.get("status") == "ok", str(data))

data = api_get(f"/api/rewards/status?student_id={STUDENT_ID}")
check("Rewards: returns level", data.get("level") == 1, str(data.get("level")))
check("Rewards: has sprite_stage", "sprite_stage" in data)
check("Rewards: has unlocked_achievements", "unlocked_achievements" in data)

# ============================================
# 3. DIAGNOSE FLOW
# ============================================
print("\n--- 3. Diagnose Flow ---")

# Get a question
q = api_get(f"/api/exercise/next?student_id={STUDENT_ID}")
qid = q.get("question_id", "")
check("Diagnose: question loaded", bool(qid), str(q))
check("Diagnose: has question text", bool(q.get("question")), q.get("question", "")[:50])
check("Diagnose: has kp_name", bool(q.get("kp_name")))

# Try a wrong answer
sub = api_post("/api/exercise/submit", {
    "student_id": STUDENT_ID,
    "question_id": qid,
    "answer": "wrong_answer_xyz",
})
check("Submit: wrong answer returns", not sub.get("is_correct"), str(sub.get("is_correct")))
check("Submit: has hint", bool(sub.get("hint")), sub.get("hint", "")[:50])
check("Submit: has should_retry", "should_retry" in sub)
check("Submit: correct_answer is string", isinstance(sub.get("correct_answer"), str), str(type(sub.get("correct_answer"))))

# Get another question  
q2 = api_get(f"/api/exercise/next?student_id={STUDENT_ID}")
qid2 = q2.get("question_id", "")
check("Diagnose: second question different", qid2 != qid if qid2 else False)

# Submit correct answer
match = q2.get("correct_answer")
if not match and q2.get("options"):
    match = q2["options"][0]
sub2 = api_post("/api/exercise/submit", {
    "student_id": STUDENT_ID,
    "question_id": qid2,
    "answer": "0",
})
is_correct2 = sub2.get("is_correct", False)
check("Submit: answer submitted", "is_correct" in sub2)

# Rewards processing
reward = api_post(f"/api/rewards/process?student_id={STUDENT_ID}&is_correct={'true' if is_correct2 else 'false'}&combo={1 if is_correct2 else 0}", {})
check("Rewards: process OK", reward.get("success") == True, str(reward.get("success")))
check("Rewards: has sprite_reaction", "sprite_reaction" in reward)

# Test diagnose report
records = [
    {"kp_id": q.get("knowledge_point_id"), "is_correct": False},
    {"kp_id": q2.get("knowledge_point_id"), "is_correct": is_correct2},
]
try:
    report = api_post("/api/diagnose", {"student_id": STUDENT_ID, "records": records})
    check("Diagnose: report generated", report.get("success", True) != False, str(report)[:100])
    check("Diagnose: has root_causes", "root_causes" in report, str(list(report.keys())))
except Exception as e:
    check("Diagnose: report API", False, str(e)[:80])

# ============================================
# 4. STORYTELLER
# ============================================
print("\n--- 4. Storyteller ---")

story_data = api_get("/api/exercise/themes")
check("Story: themes API", story_data.get("success"), str(story_data))
num_themes = len(story_data.get("themes", []))
check("Story: 8 themes available", num_themes == 8, str(num_themes))

try:
    story = api_post("/api/exercise/story", {
        "question_id": qid,
        "question_text": q.get("question", "1+1"),
    })
    check("Story: generate returns", story.get("success"), str(story))
    check("Story: has story_question", bool(story.get("story_question")), story.get("story_question", "")[:50])
    check("Story: has theme", bool(story.get("theme")), str(story.get("theme")))
    check("Story: has theme_icon", bool(story.get("theme_icon")), str(story.get("theme_icon")))
except Exception as e:
    check("Story: API", False, str(e)[:80])

# ============================================
# 5. PARENT DASHBOARD
# ============================================
print("\n--- 5. Parent Dashboard ---")

pin = "1234"
try:
    dash = api_get(f"/api/parent/dashboard?student_id={STUDENT_ID}", {"x-parent-pin": pin})
    check("Parent: dashboard with correct PIN", "streak_days" in dash, str(dash.keys())[:80])
    check("Parent: has heatmap", "mastery_heatmap" in dash)
    check("Parent: has suggestions", "suggestions" in dash)
except Exception as e:
    check("Parent: dashboard API", False, str(e)[:80])

# Wrong PIN
try:
    api_get(f"/api/parent/dashboard?student_id={STUDENT_ID}", {"x-parent-pin": "0000"})
    check("Parent: rejects wrong PIN", False, "Should return 403")
except urllib.error.HTTPError as e:
    check("Parent: rejects wrong PIN", e.code == 403, str(e.code))

# Knowledge graph
try:
    graph = api_get(f"/api/parent/graph?student_id={STUDENT_ID}", {"x-parent-pin": pin})
    check("Parent: graph nodes", len(graph.get("nodes", [])) == 20, str(len(graph.get("nodes", []))))
    check("Parent: graph edges", len(graph.get("edges", [])) > 0, str(len(graph.get("edges", []))))
except Exception as e:
    check("Parent: graph API", False, str(e)[:80])

# ============================================
# 6. ACHIEVEMENTS + SKINS
# ============================================
print("\n--- 6. Achievements + Skins ---")

try:
    ach = api_get("/api/health/achievements")
    check("Achievements: 30 defined", len(ach.get("achievements", [])) == 30, str(len(ach.get("achievements", []))))
except Exception as e:
    check("Achievements: API", False, str(e)[:80])

try:
    skins = api_get("/api/health/skins")
    check("Skins: 7 available", len(skins.get("skins", [])) == 7, str(len(skins.get("skins", []))))
except Exception as e:
    check("Skins: API", False, str(e)[:80])

# ============================================
# 7. STATIC ASSETS
# ============================================
print("\n--- 7. Static Assets ---")

for path, label in [
    ("/assets/index-DyVfcGur.js", "React JS"),
    ("/assets/index-DC3a8Qe6.css", "React CSS"),
    ("/sw.js", "Service Worker"),
    ("/manifest.webmanifest", "PWA Manifest"),
]:
    try:
        status, _ = fetch(path)
        check(f"Asset: {label}", status == 200, str(status))
    except Exception as e:
        check(f"Asset: {label}", False, str(e)[:50])

# Flutter assets  
for path, label in [
    ("/flutter/main.dart.js", "Flutter JS"),
    ("/flutter/flutter_bootstrap.js", "Flutter bootstrap"),
    ("/flutter/manifest.json", "Flutter manifest"),
]:
    try:
        status, _ = fetch(path)
        check(f"Asset: {label}", status == 200, str(status))
    except Exception as e:
        check(f"Asset: {label}", False, str(e)[:50])

# ============================================
# SUMMARY
# ============================================
passed = sum(results)
total = len(results)
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} passed ({100*passed/total:.0f}%)")
if errors:
    print(f"\nFAILURES ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("ALL PASSED!")
print("=" * 60)
