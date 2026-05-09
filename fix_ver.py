import paramiko, json, io

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

d = json.dumps({"version":"1.0.1","version_code":2,"apk_url":"/flutter/app-release.apk","apk_size":22033665,"release_notes":"quiz v1.0.1","min_version_code":1}, ensure_ascii=False, indent=2).encode("utf-8")

s = c.open_sftp()
s.putfo(io.BytesIO(d), "/opt/math-home-tutor/backend/data/version.json")
s.close()

c.exec_command("systemctl restart math-tutor")
import time; time.sleep(2)
stdin, stdout, stderr = c.exec_command("curl -s http://127.0.0.1:8000/api/health/version")
print(stdout.read().decode())
c.close()
