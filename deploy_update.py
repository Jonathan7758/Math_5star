import paramiko
import os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=30)
s = c.open_sftp()

# Upload frontend dist
dist_dir = "C:/projects/Math-5star/frontend/dist"
for f in os.listdir(dist_dir):
    src = os.path.join(dist_dir, f)
    dst = f"/opt/math-home-tutor/frontend/dist/{f}"
    if os.path.isfile(src):
        print(f"  {f}")
        s.put(src, dst)

assets_dir = os.path.join(dist_dir, "assets")
for f in os.listdir(assets_dir):
    src = os.path.join(assets_dir, f)
    dst = f"/opt/math-home-tutor/frontend/dist/assets/{f}"
    print(f"  assets/{f}")
    s.put(src, dst)

# Upload fixed backend files
s.put("C:/projects/Math-5star/backend/routers/exercise.py", "/opt/math-home-tutor/backend/routers/exercise.py")
s.put("C:/projects/Math-5star/backend/store.py", "/opt/math-home-tutor/backend/store.py")
print("  exercise.py + store.py")

s.close()

# Restart
stdin, stdout, stderr = c.exec_command("systemctl restart math-tutor && sleep 2 && curl -s http://127.0.0.1:8000/api/health", timeout=15)
print(f"Health: {stdout.read().decode().strip()}")

# Verify frontend
stdin, stdout, stderr = c.exec_command("curl -sI http://127.0.0.1/ | head -3", timeout=10)
print(f"Frontend: {stdout.read().decode().strip()}")

c.close()
print("Done!")
