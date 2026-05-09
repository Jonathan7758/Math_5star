import paramiko

NGINX_CONF = r'''server {
    listen 80;
    server_name _;
    root /opt/math-home-tutor/frontend/dist;
    index index.html;

    # Flutter app static files (before regex)
    location ^~ /flutter/ {
        alias /opt/math-home-tutor/frontend/flutter_app/;
        try_files $uri /flutter/index.html;
    }

    # React SPA
    location / {
        try_files $uri $uri/ /index.html;
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

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

s = c.open_sftp()
with s.open("/etc/nginx/sites-available/math-tutor", "w") as f:
    f.write(NGINX_CONF.encode())
s.close()

stdin, stdout, stderr = c.exec_command("nginx -t && systemctl reload nginx")
print(stdout.read().decode())
err = stderr.read().decode()
if err: print("ERR:", err[:300])

# Quick test
import urllib.request
test_paths = [
    "/", "/assets/index-DyVfcGur.js", "/sw.js", "/manifest.webmanifest",
    "/flutter/", "/flutter/main.dart.js", "/flutter/flutter_bootstrap.js"
]
for p in test_paths:
    try:
        r = urllib.request.urlopen(f"http://101.96.217.150{p}", timeout=5)
        print(f"  {p}: {r.status}")
    except Exception as e:
        print(f"  {p}: FAIL")

c.close()
