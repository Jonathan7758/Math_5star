import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

conf = r'''server {
    listen 80;
    server_name _;
    root /opt/math-home-tutor/frontend/dist;
    index index.html;

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

s = c.open_sftp()
with s.open("/etc/nginx/sites-available/math-tutor", "w") as f:
    f.write(conf.encode())
s.close()

stdin, stdout, stderr = c.exec_command("nginx -t && systemctl reload nginx", timeout=10)
print(stdout.read().decode())
print(stderr.read().decode())

# Verify
stdin, stdout, stderr = c.exec_command("curl -sI http://127.0.0.1/manifest.webmanifest | grep -i content-type", timeout=10)
print("Manifest MIME:", stdout.read().decode().strip())

c.close()
