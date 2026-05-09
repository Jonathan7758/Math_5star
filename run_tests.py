"""
Comprehensive deployed application test suite.
Tests: API endpoints, React web frontend, Flutter web, Flutter APK accessibility.
Results written to test_report.txt
"""
import urllib.request
import urllib.error
import json
import time
import sys
from datetime import datetime

BASE = "http://101.96.217.150"
RESULTS = []

def test(label, category, fn):
    """Run a test and record result."""
    try:
        start = time.time()
        fn()
        elapsed = time.time() - start
        RESULTS.append({"label": label, "category": category, "status": "PASS", "time": f"{elapsed:.2f}s"})
        print(f"  [PASS] {label} ({elapsed:.2f}s)")
    except Exception as e:
        elapsed = time.time() - start
        RESULTS.append({"label": label, "category": category, "status": "FAIL", "time": f"{elapsed:.2f}s", "error": str(e)[:200]})
        print(f"  [FAIL] {label}: {str(e)[:120]}")

def get(url, timeout=15):
    return urllib.request.urlopen(url, timeout=timeout)

def post(url, data, timeout=15):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout)

def check_status(url, expected=200, timeout=10):
    resp = get(url, timeout)
    assert resp.status == expected, f"Expected {expected}, got {resp.status}"
    return resp

def check_json(url, timeout=10):
    resp = get(url, timeout)
    return json.loads(resp.read())

# ================================================================
# 1. BACKEND API TESTS
# ================================================================

def test_health():
    data = check_json(f"{BASE}/api/health")
    assert data["status"] == "ok"

def test_version():
    data = check_json(f"{BASE}/api/health/version")
    assert "version" in data

def test_achievements():
    data = check_json(f"{BASE}/api/health/achievements")
    assert "achievements" in data
    assert len(data["achievements"]) >= 30

def test_skins():
    data = check_json(f"{BASE}/api/health/skins")
    assert "skins" in data
    assert len(data["skins"]) >= 7

def test_exercise_next():
    data = check_json(f"{BASE}/api/exercise/next?student_id=1")
    assert data["success"] is True
    assert "question_id" in data
    assert "question" in data

def test_exercise_next_by_kp():
    data = check_json(f"{BASE}/api/exercise/next?student_id=1&kp_id=K01")
    assert data["success"] is True
    assert data["knowledge_point_id"] == "K01"

def test_exercise_themes():
    data = check_json(f"{BASE}/api/exercise/themes")
    assert data["success"] is True
    assert len(data["themes"]) == 8

def test_exercise_submit():
    data = post(f"{BASE}/api/exercise/submit", {"student_id": 1, "question_id": "Q-K01-L1-01", "answer": "42", "time_spent": 5.0})
    resp = json.loads(data.read())
    assert resp["success"] is True
    assert "is_correct" in resp

def test_diagnose():
    data = post(f"{BASE}/api/diagnose", {
        "student_id": 1,
        "records": [
            {"kp_id": "K01", "is_correct": False},
            {"kp_id": "K01", "is_correct": False},
            {"kp_id": "K02", "is_correct": False},
        ]
    })
    resp = json.loads(data.read())
    assert resp["success"] is True
    assert "root_causes" in resp

def test_plan():
    data = post(f"{BASE}/api/plan", {
        "student_id": 1,
        "root_causes": [
            {"kp_id": "K01", "kp_name": "Integer Operations", "priority": 0.85, "impacted_nodes": []},
            {"kp_id": "K02", "kp_name": "Fractions Basics", "priority": 0.42, "impacted_nodes": []},
        ]
    })
    resp = json.loads(data.read())
    assert resp["success"] is True
    assert "path" in resp

def test_rewards_status():
    data = check_json(f"{BASE}/api/rewards/status?student_id=1")
    assert "level" in data

def test_rewards_process():
    req = urllib.request.Request(
        f"{BASE}/api/rewards/process?student_id=1&is_correct=true&combo=1",
        method="POST", data=b"", headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    assert "sprite_reaction" in data

def test_sprite_state():
    data = check_json(f"{BASE}/api/sprite/state?student_id=1")
    assert "stage" in data

PARENT_HEADERS = {"x-parent-pin": "1234"}

def test_parent_dashboard():
    req = urllib.request.Request(f"{BASE}/api/parent/dashboard?student_id=1", headers=PARENT_HEADERS)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    assert "mastery_heatmap" in data or "weekly_stats" in data or "success" in data

def test_parent_graph():
    req = urllib.request.Request(f"{BASE}/api/parent/graph?student_id=1", headers=PARENT_HEADERS)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    assert "nodes" in data

def test_parent_dashboard_no_pin():
    try:
        resp = get(f"{BASE}/api/parent/dashboard?student_id=1&pin=0000", timeout=5)
        data = json.loads(resp.read())
        assert data.get("success") is False or resp.status in [401, 403]
        print("  [PASS] parent dashboard rejects wrong PIN")
    except urllib.error.HTTPError as e:
        assert e.code in [401, 403], f"Expected 401/403, got {e.code}"

# ================================================================
# 2. REACT FRONTEND TESTS
# ================================================================

def test_react_index():
    resp = check_status(f"{BASE}/", 200)
    html = resp.read().decode()
    assert "启明星" in html or "Math" in html or "root" in html

def test_react_assets_js():
    check_status(f"{BASE}/assets/index-CKSdCkXz.js", 200)

def test_react_assets_css():
    resp = get(f"{BASE}/assets/index-DAidFoJi.css", timeout=10)
    assert resp.status == 200

def test_react_pwa_manifest():
    resp = get(f"{BASE}/manifest.webmanifest", timeout=10)
    assert resp.status == 200
    data = json.loads(resp.read())
    assert "name" in data

def test_react_sw():
    check_status(f"{BASE}/sw.js", 200)

def test_react_spa_routing():
    resp = get(f"{BASE}/quiz", timeout=10)
    html = resp.read().decode()
    assert "启明星" in html or "root" in html  # SPA should return index.html

# ================================================================
# 3. FLUTTER WEB TESTS
# ================================================================

def test_flutter_index():
    resp = check_status(f"{BASE}/flutter/", 200)
    html = resp.read().decode()
    assert "flutter" in html.lower() or "math" in html.lower()

def test_flutter_js():
    check_status(f"{BASE}/flutter/main.dart.js", 200)

def test_flutter_manifest():
    resp = get(f"{BASE}/flutter/manifest.json", timeout=10)
    assert resp.status == 200

def test_flutter_icons():
    check_status(f"{BASE}/flutter/icons/Icon-192.png", 200)

# ================================================================
# 4. FLUTTER APK TESTS
# ================================================================

def test_apk_accessible():
    resp = get(f"{BASE}/flutter/app-release.apk", timeout=30)
    assert resp.status == 200
    cl = resp.headers.get("Content-Length", "0")
    size_mb = int(cl) / 1024 / 1024
    assert size_mb > 1, f"APK too small: {size_mb:.1f}MB"
    print(f"       APK size: {size_mb:.1f}MB")

def test_version_json():
    resp = get(f"{BASE}/api/health/version", timeout=10)
    data = json.loads(resp.read())
    assert "apk_url" in data or "version" in data

# ================================================================
# 5. UX / STORYTELLER TESTS
# ================================================================

def test_story_api():
    data = post(f"{BASE}/api/exercise/story", {
        "question_id": "Q-K01-L1-01",
        "question_text": "计算 3 + 5 = ?",
        "theme": "space"
    })
    resp = json.loads(data.read())
    assert resp["success"] is True
    assert "story_question" in resp
    assert "theme" in resp

def test_story_api_random_theme():
    data = post(f"{BASE}/api/exercise/story", {
        "question_id": "Q-K01-L1-02",
        "question_text": "计算 10 - 7 = ?",
        "theme": None
    })
    resp = json.loads(data.read())
    assert resp["success"] is True
    assert resp.get("generated") is not None

def test_all_themes_work():
    for theme_key in ["fruit_shop", "animals", "space", "game_world", "baking", "sports", "ocean", "carnival"]:
        data = post(f"{BASE}/api/exercise/story", {
            "question_id": f"Q-TEST-{theme_key}",
            "question_text": "5 + 3 = ?",
            "theme": theme_key
        })
        resp = json.loads(data.read())
        assert resp["success"] is True
        assert resp["theme"] == theme_key

# ================================================================
# 6. FRONTEND STORYTELLER RENDERING TEST
# ================================================================

def test_frontend_includes_themes():
    resp = get(f"{BASE}/", timeout=10)
    html = resp.read().decode()
    # The frontend JS should include theme-related code
    resp2 = get(f"{BASE}/assets/index-CKSdCkXz.js", timeout=15)
    js = resp2.read().decode()
    # Check that storyteller integration code is in the bundle
    has_themes = "exercise/themes" in js or "story_question" in js or "storyText" in js
    assert has_themes, "Storyteller code not found in frontend JS bundle"

def test_frontend_includes_mathjax():
    resp = get(f"{BASE}/", timeout=10)
    html = resp.read().decode()
    assert "mathjax" in html.lower(), "MathJax script not found in index.html"

# ================================================================
# RUN ALL TESTS
# ================================================================

ALL_TESTS = [
    # Category: API Core
    ("API Health Check", "API", test_health),
    ("API Version", "API", test_version),
    ("API Achievements List", "API", test_achievements),
    ("API Skins List", "API", test_skins),
    
    # Category: Exercise
    ("Get Next Question", "Exercise", test_exercise_next),
    ("Get Question by KP", "Exercise", test_exercise_next_by_kp),
    ("Get Themes (8)", "Exercise", test_exercise_themes),
    ("Submit Answer", "Exercise", test_exercise_submit),
    
    # Category: Diagnose & Plan
    ("Diagnose API", "Diagnose", test_diagnose),
    ("Plan API", "Plan", test_plan),
    
    # Category: Rewards & Sprite
    ("Rewards Status", "Rewards", test_rewards_status),
    ("Rewards Process", "Rewards", test_rewards_process),
    ("Sprite State", "Sprite", test_sprite_state),
    
    # Category: Parent
    ("Parent Dashboard (PIN)", "Parent", test_parent_dashboard),
    ("Parent Graph", "Parent", test_parent_graph),
    ("Parent Wrong PIN Rejected", "Parent", test_parent_dashboard_no_pin),
    
    # Category: React Frontend
    ("React Index HTML", "React", test_react_index),
    ("React JS Bundle", "React", test_react_assets_js),
    ("React CSS Bundle", "React", test_react_assets_css),
    ("React PWA Manifest", "React", test_react_pwa_manifest),
    ("React Service Worker", "React", test_react_sw),
    ("React SPA Routing", "React", test_react_spa_routing),
    
    # Category: Flutter Web
    ("Flutter Index HTML", "Flutter Web", test_flutter_index),
    ("Flutter Main JS", "Flutter Web", test_flutter_js),
    ("Flutter Manifest", "Flutter Web", test_flutter_manifest),
    ("Flutter Icons", "Flutter Web", test_flutter_icons),
    
    # Category: APK
    ("APK Downloadable", "APK", test_apk_accessible),
    ("Version API for APK", "APK", test_version_json),
    
    # Category: Storyteller (UX)
    ("Storyteller API (space theme)", "Storyteller", test_story_api),
    ("Storyteller API (random theme)", "Storyteller", test_story_api_random_theme),
    ("All 8 Themes Work", "Storyteller", test_all_themes_work),
    
    # Category: Frontend Integration (UX)
    ("Frontend includes themes code", "Frontend Integration", test_frontend_includes_themes),
    ("Frontend includes MathJax", "Frontend Integration", test_frontend_includes_mathjax),
]

print("=" * 60)
print(f"Math-5star Comprehensive Test Suite")
print(f"Target: {BASE}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

for t in ALL_TESTS:
    test(t[0], t[1], t[2])

# Summary
passed = sum(1 for r in RESULTS if r["status"] == "PASS")
failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
total = len(RESULTS)

print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} passed, {failed} failed")
print("=" * 60)

# Group by category
from collections import defaultdict
by_cat = defaultdict(lambda: {"pass": 0, "fail": 0})
for r in RESULTS:
    by_cat[r["category"]]["pass" if r["status"] == "PASS" else "fail"] += 1

print("\nBy Category:")
for cat, counts in sorted(by_cat.items()):
    pct = counts["pass"] / (counts["pass"] + counts["fail"]) * 100 if (counts["pass"] + counts["fail"]) > 0 else 0
    print(f"  {cat:25s}: {counts['pass']}/{counts['pass']+counts['fail']} ({pct:.0f}%)")

# Write report
with open("C:/projects/Math-5star/test_report.txt", "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write(f"Math-5star Test Report\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Target: {BASE}\n")
    f.write(f"Version: v1.2 (P0 Storyteller + MathJax)\n")
    f.write("=" * 60 + "\n\n")
    
    f.write(f"## Summary\n")
    f.write(f"Total: {total} | Passed: {passed} | Failed: {failed} | Pass Rate: {passed/total*100:.0f}%\n\n")
    
    f.write("## Results by Category\n")
    for cat, counts in sorted(by_cat.items()):
        pct = counts["pass"] / (counts["pass"] + counts["fail"]) * 100 if (counts["pass"] + counts["fail"]) > 0 else 0
        f.write(f"  {cat}: {counts['pass']}/{counts['pass']+counts['fail']} ({pct:.0f}%)\n")
    
    f.write("\n## Detailed Results\n\n")
    for r in RESULTS:
        status_icon = "PASS" if r["status"] == "PASS" else "FAIL"
        f.write(f"[{status_icon}] [{r['category']}] {r['label']} ({r['time']})\n")
        if r["status"] == "FAIL":
            f.write(f"       Error: {r.get('error', 'Unknown')}\n")
    
    f.write(f"\n## UX Assessment\n\n")
    f.write("### Storyteller Integration (P0.1)\n")
    f.write("- Backend API: /api/exercise/story + /api/exercise/themes deployed\n")
    f.write("- Frontend: QuizPage has theme selector (8 themes + random)\n")
    f.write("- Frontend: QuestionCardEnhanced renders themed dialogue bubble\n")
    f.write("- 8 theme visual styles (gradient + border + accent per theme)\n\n")
    f.write("### MathJax Rendering (P0.2)\n")
    f.write("- MathJax v3 CDN script added to index.html\n")
    f.write("- MathText component calls MathJax.typesetPromise() for LaTeX rendering\n")
    f.write("- Fallback to regex-based styling when MathJax unavailable\n\n")
    f.write("### Known Issues\n")
    f.write("- 1 pre-existing backend test failure (test_submit_equivalent_answer)\n")
    f.write("- Flutter app missing ~10 v1.0 features (achievements, skin shop, etc.)\n")
    f.write("- Canvaskit files not uploaded (large size, without them Flutter web may use HTML renderer)\n")

    f.write(f"\n## Test Environment\n")
    f.write(f"- Server: 101.96.217.150 (Ubuntu 24.04)\n")
    f.write(f"- Backend: Python 3.12 + FastAPI + Uvicorn\n")
    f.write(f"- Frontend: React 18 + Vite + Tailwind\n")
    f.write(f"- Flutter: 3.29.3 + Flame 1.18\n")
    f.write(f"- Nginx: reverse proxy on port 80\n")

print("\nReport written to: C:/projects/Math-5star/test_report.txt")
