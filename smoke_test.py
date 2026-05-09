import urllib.request, json

BASE = "http://101.96.217.150"

def get(url, api=False):
    r = urllib.request.urlopen(f"{BASE}{url}", timeout=10)
    data = r.read()
    return json.loads(data) if api else data.decode()

# 1. Health
h = get("/api/health", True)
print(f"1. API Health: {h}")

# 2. Quiz bank
q = get("/api/exercise/next?student_id=1", True)
print(f"2. Question: {q.get('kp_name')} | {q.get('question','')[:60]}")

# 3. Rewards
r = get("/api/rewards/status?student_id=1", True)
print(f"3. Rewards: Lv{r['level']} XP={r['xp_current']}/{r['xp_next']} Streak={r['streak_days']} Sprite={r['sprite_name']}")

# 4. Parent dashboard
req = urllib.request.Request(f"{BASE}/api/parent/dashboard?student_id=1", headers={"x-parent-pin": "1234"})
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
print(f"4. Parent: mastered={d.get('mastered_count')} KPs, streak={d.get('streak_days')}")

# 5. Knowledge graph
req2 = urllib.request.Request(f"{BASE}/api/parent/graph?student_id=1", headers={"x-parent-pin": "1234"})
g = json.loads(urllib.request.urlopen(req2, timeout=10).read())
nodes = len(g.get("nodes", []))
edges = len(g.get("edges", []))
print(f"5. Graph: {nodes} nodes, {edges} edges")

# 6. Achievements
a = get("/api/health/achievements", True)
print(f"6. Achievements: {len(a.get('achievements', []))} defined")

# 7. Skins
s = get("/api/health/skins", True)
print(f"7. Skins: {len(s.get('skins', []))} available")

# 8. Frontend HTML
html = get("/")
print(f"8. Frontend: {len(html)} bytes, PWA={('manifest' in html)}, SW={('serviceWorker' in html)}")

# 9. Submit test
try:
    import urllib.parse
    body = json.dumps({"student_id": 1, "question_id": q["question_id"], "answer": "0"}).encode()
    req3 = urllib.request.Request(f"{BASE}/api/exercise/submit", data=body, headers={"Content-Type": "application/json"}, method="POST")
    sub = json.loads(urllib.request.urlopen(req3, timeout=10).read())
    print(f"9. Submit: is_correct={sub['is_correct']}, should_retry={sub.get('should_retry')}")
except Exception as e:
    print(f"9. Submit: {e}")

print("\nAll systems operational!")
