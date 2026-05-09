import paramiko
import time

HOST = "101.96.217.150"
USER = "root"
PASS = "1Qxcjyb!@"

SERVICE = """[Unit]
Description=Math Home Tutor Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/math-home-tutor
ExecStart=/opt/math-home-tutor/venv/bin/python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
StandardOutput=append:/opt/math-home-tutor/logs/backend.log
StandardError=append:/opt/math-home-tutor/logs/backend_error.log

[Install]
WantedBy=multi-user.target
"""

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=15)

sftp = c.open_sftp()
with sftp.open('/etc/systemd/system/math-tutor.service', 'w') as f:
    f.write(SERVICE.encode())
sftp.close()

for cmd in [
    'systemctl daemon-reload',
    'systemctl stop math-tutor',
    'pkill -f uvicorn; sleep 1',
    'systemctl restart math-tutor',
]:
    stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"$ {cmd}: {out}")
    if err:
        print(f"$ {cmd} ERR: {err[:200]}")

time.sleep(3)
stdin, stdout, stderr = c.exec_command('systemctl status math-tutor --no-pager | head -6', timeout=10)
print(stdout.read().decode())

stdin, stdout, stderr = c.exec_command('curl -s http://127.0.0.1:8000/api/health', timeout=10)
health = stdout.read().decode().strip()
print(f"Health: {health}")

stdin, stdout, stderr = c.exec_command('curl -s http://127.0.0.1:8000/ | head -5', timeout=10)
print(f"Frontend: {stdout.read().decode()[:200]}")

c.close()
