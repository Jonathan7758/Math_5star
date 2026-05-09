import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)
s = c.open_sftp()
s.put("C:/projects/Math-5star/android_app/build/app/outputs/flutter-apk/app-release.apk",
      "/opt/math-home-tutor/frontend/flutter_app/app-release.apk")
s.close()
c.exec_command("systemctl reload nginx")

import urllib.request
r = urllib.request.urlopen("http://101.96.217.150/flutter/app-release.apk", timeout=10)
size = r.headers.get("Content-Length", "?")
print(f"APK uploaded: {r.status} {size} bytes")
print("Download: http://101.96.217.150/flutter/app-release.apk")
c.close()
