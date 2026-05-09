import urllib.request

r = urllib.request.urlopen("http://101.96.217.150/assets/index-oaAPaWfr.js", timeout=15)
js = r.read().decode()

# Check for unique strings that would prove our code is there
checks = [
    "戳戳我",
    "pointerEvents",
    "touchend",
    "addEventListener",
    "SpriteDisplay",
    "TAP_MESSAGES",
]
for s in checks:
    found = s in js
    print(f"  '{s}': {'YES' if found else 'NO'}")
