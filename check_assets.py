import urllib.request

BASE = "http://101.96.217.150"

# Check all critical assets
checks = [
    ("/", "index.html"),
    ("/assets/index-BxBKMZfM.js", "main JS"),
    ("/assets/index-DC3a8Qe6.css", "main CSS"),
    ("/sw.js", "service worker"),
    ("/manifest.webmanifest", "PWA manifest"),
    ("/registerSW.js", "SW registration"),
]

all_ok = True
for path, label in checks:
    try:
        r = urllib.request.urlopen(f"{BASE}{path}", timeout=10)
        content_type = r.headers.get("Content-Type", "")
        length = len(r.read())
        icon = "+" if r.status == 200 else "X"
        print(f"  [{icon}] {label}: {r.status} {length}B {content_type[:30]}")
    except Exception as e:
        print(f"  [X] {label}: {e}")
        all_ok = False

print(f"\nAll assets accessible: {all_ok}")
print(f"\nAccess URL: {BASE}")
print("Open on your phone to test mobile experience!")
