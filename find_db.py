import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

cmds = [
    "find /opt/math-home-tutor -name '*.db' 2>/dev/null",
    "ls -la /opt/math-home-tutor/backend/data/ 2>/dev/null",
    "cat /opt/math-home-tutor/backend/config.py",
    "ls -la /opt/math-home-tutor/*.db 2>/dev/null",
    "ls -la /opt/math-home-tutor/backend/*.db 2>/dev/null",
]

for cmd in cmds:
    print(f"\n=== {cmd}")
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err: print("ERR:", err[:200])

c.close()
