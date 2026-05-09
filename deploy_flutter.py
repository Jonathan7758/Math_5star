import paramiko
import os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)
s = c.open_sftp()

# Create Flutter app directory
c.exec_command("mkdir -p /opt/math-home-tutor/frontend/flutter_app/assets")
c.exec_command("mkdir -p /opt/math-home-tutor/frontend/flutter_app/canvaskit")

# Upload all web build files
build_dir = "C:/projects/Math-5star/android_app/build/web"
uploaded = 0
for f in os.listdir(build_dir):
    src = os.path.join(build_dir, f)
    dst = f"/opt/math-home-tutor/frontend/flutter_app/{f}"
    if os.path.isfile(src):
        s.put(src, dst)
        uploaded += 1
        print(f"  {f}")

# Upload assets
assets_dir = os.path.join(build_dir, "assets")
if os.path.isdir(assets_dir):
    for f in os.listdir(assets_dir):
        src = os.path.join(assets_dir, f)
        dst = f"/opt/math-home-tutor/frontend/flutter_app/assets/{f}"
        if os.path.isfile(src):
            s.put(src, dst)
            uploaded += 1
            print(f"  assets/{f}")

# Upload canvaskit
ck_dir = os.path.join(build_dir, "canvaskit")
if os.path.isdir(ck_dir):
    for f in os.listdir(ck_dir):
        src = os.path.join(ck_dir, f)
        dst = f"/opt/math-home-tutor/frontend/flutter_app/canvaskit/{f}"
        if os.path.isfile(src):
            s.put(src, dst)
            uploaded += 1
            print(f"  canvaskit/{f}")

s.close()
print(f"\nUploaded {uploaded} files")

# Configure Nginx
nginx_conf = '''server {
    listen 80;
    server_name _;
    root /opt/math-home-tutor/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ^~ /flutter/ {
        alias /opt/math-home-tutor/frontend/flutter_app/;
        try_files $uri $uri/ /flutter/index.html;
        index index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location ~* \.webmanifest$ {
        types { } default_type application/manifest+json;
    }
}
'''

s = c.open_sftp()
with s.open("/etc/nginx/sites-available/math-tutor", "w") as f:
    f.write(nginx_conf.encode())
s.close()

stdin, stdout, stderr = c.exec_command("nginx -t && systemctl reload nginx")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("NGINX ERR:", err[:300])

# Verify
stdin, stdout, stderr = c.exec_command("curl -sI http://127.0.0.1/flutter/ | head -5")
print("Flutter:", stdout.read().decode())

stdin, stdout, stderr = c.exec_command("ls /opt/math-home-tutor/frontend/flutter_app/ | head -10")
print("Files:", stdout.read().decode())

c.close()
print("Done!")
