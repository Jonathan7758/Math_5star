import urllib.request, json

# Test storyteller API
body = json.dumps({"question_id": "Q-K01-L1-01", "question_text": "Calculate: 2 + 3 = ?"}).encode()
req = urllib.request.Request("http://101.96.217.150/api/exercise/story", data=body, headers={"Content-Type": "application/json"}, method="POST")
try:
    r2 = urllib.request.urlopen(req, timeout=30)
    d2 = json.loads(r2.read())
    print("Success:", d2["success"])
    print("Generated:", d2["generated"])
    print("Theme:", d2["theme_name"])
    print("Original: Calculate: 2 + 3 = ?")
    print("Story:", d2["story_question"][:120])
except Exception as e:
    print(f"Story API error: {e}")
