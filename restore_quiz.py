import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

s = c.open_sftp()
with s.open("/opt/math-home-tutor/backend/data/quiz_bank.json", "r") as f:
    data = f.read()

with open("C:/projects/Math-5star/backend/data/quiz_bank.json", "wb") as lf:
    lf.write(data)
s.close()

import json
d = json.loads(data.decode("utf-8"))
print(f"Restored: {len(d['questions'])} questions")
c.close()
