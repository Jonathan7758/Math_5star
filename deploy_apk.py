import paramiko
import os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=30)
s = c.open_sftp()

# Upload latest APK
apk_path = "C:/projects/Math-5star/android_app/build/app/outputs/flutter-apk/app-release.apk"
remote = "/opt/math-home-tutor/frontend/flutter_app/app-release.apk"
print(f"Uploading APK ({os.path.getsize(apk_path)/1024/1024:.1f}MB)...")
s.put(apk_path, remote)
print("APK uploaded")

# Upload version.json
s.put("C:/projects/Math-5star/backend/data/version.json", "/opt/math-home-tutor/backend/data/version.json")
print("Version uploaded")

s.close()

# Restart backend and verify
c.exec_command("systemctl restart math-tutor")

import urllib.request
r = urllib.request.urlopen("http://101.96.217.150/api/health/version", timeout=10)
import json
v = json.loads(r.read())
print(f"Version API: v{v['version']} code={v['version_code']}")

# Check APK size
r2 = urllib.request.urlopen("http://101.96.217.150/flutter/app-release.apk", timeout=10)
size = r2.headers.get("Content-Length", "?")
print(f"APK URL: {r2.status} {int(size)/1024/1024:.1f}MB")

c.close()
print("Done")
