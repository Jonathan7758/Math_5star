"""Deploy Math-5star to production server."""
import paramiko
import os
import sys
import tarfile
import io
from pathlib import Path

HOST = "101.96.217.150"
USER = "root"
PASS = "1Qxcjyb!@"
DEPLOY_DIR = "/opt/math-home-tutor"
LOCAL_DIR = Path(__file__).resolve().parent

def ssh_cmd(client, cmd, sudo=False):
    if sudo:
        cmd = f"sudo {cmd}"
    print(f"  $ {cmd[:100]}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if err.strip():
        print(f"  STDERR: {err.strip()[:200]}")
    return out.strip()

def upload_file(sftp, local_path, remote_path):
    print(f"  Upload: {local_path} -> {remote_path}")
    sftp.put(str(local_path), remote_path)

def upload_dir(sftp, local_dir, remote_dir):
    """Upload directory recursively."""
    sftp.mkdir(remote_dir)
    for item in os.listdir(local_dir):
        local_item = os.path.join(local_dir, item)
        remote_item = f"{remote_dir}/{item}"
        if os.path.isdir(local_item):
            upload_dir(sftp, local_item, remote_item)
        else:
            sftp.put(local_item, remote_item)

def deploy():
    print("=" * 60)
    print("Math-5star Production Deployment")
    print("=" * 60)

    # 1. Connect
    print("\n[1/8] Connecting to server...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=30)
    sftp = client.open_sftp()
    print("  Connected.")

    # 2. Stop existing services
    print("\n[2/8] Stopping existing services...")
    ssh_cmd(client, "systemctl stop math-tutor 2>/dev/null; systemctl stop nginx 2>/dev/null; true")
    ssh_cmd(client, "pkill -f uvicorn 2>/dev/null; pkill -f gunicorn 2>/dev/null; true")
    print("  Done.")

    # 3. Backup and clean
    print("\n[3/8] Preparing directories...")
    ssh_cmd(client, f"mkdir -p {DEPLOY_DIR}/backend/data {DEPLOY_DIR}/frontend/dist {DEPLOY_DIR}/logs")

    # 4. Upload backend
    print("\n[4/8] Uploading backend...")
    backend_files = [
        "backend/main.py", "backend/config.py", "backend/store.py",
        "backend/knowledge_graph.json",
        "backend/explanations.json",
    ]
    # Upload directories
    for d in ["backend/agents", "backend/engine", "backend/models", "backend/routers"]:
        local_d = LOCAL_DIR / d
        remote_d = f"{DEPLOY_DIR}/{d}"
        if local_d.is_dir():
            for f in local_d.iterdir():
                if f.suffix == ".py":
                    remote_p = f"{DEPLOY_DIR}/{d}/{f.name}"
                    upload_file(sftp, f, remote_p)

    for f_path in backend_files:
        local_f = LOCAL_DIR / f_path
        remote_f = f"{DEPLOY_DIR}/{f_path}"
        if local_f.is_file():
            upload_file(sftp, local_f, remote_f)

    # Upload data files
    for data_file in ["quiz_bank.json", "knowledge_graph.json", "explanations.json"]:
        local_f = LOCAL_DIR / "backend" / "data" / data_file
        remote_f = f"{DEPLOY_DIR}/backend/data/{data_file}"
        if local_f.is_file():
            upload_file(sftp, local_f, remote_f)

    print("  Backend uploaded.")

    # 5. Upload frontend build
    print("\n[5/8] Uploading frontend...")
    dist_dir = LOCAL_DIR / "frontend" / "dist"
    for item in dist_dir.iterdir():
        if item.is_file():
            remote_f = f"{DEPLOY_DIR}/frontend/dist/{item.name}"
            sftp.put(str(item), remote_f)
    # Upload assets dir
    assets_dir = dist_dir / "assets"
    for item in assets_dir.iterdir():
        remote_f = f"{DEPLOY_DIR}/frontend/dist/assets/{item.name}"
        sftp.put(str(item), remote_f)
    print("  Frontend uploaded.")

    # 6. Install dependencies
    print("\n[6/8] Installing backend dependencies...")
    ssh_cmd(client, "pip3 install fastapi uvicorn sqlalchemy sympy networkx pydantic 2>&1 | tail -3")
    print("  Done.")

    # 7. Configure Nginx
    print("\n[7/8] Configuring Nginx...")
    nginx_conf = f'''
server {{
    listen 80;
    server_name _;

    # Frontend static files
    root {DEPLOY_DIR}/frontend/dist;
    index index.html;

    # SPA fallback
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # API proxy to backend
    location /api/ {{
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }}

    # SW and assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {{
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
}}
'''
    # Use Python to write the conf with explicit encoding
    encoded_conf = nginx_conf.encode('utf-8')
    with sftp.open(f"{DEPLOY_DIR}/nginx-math-tutor.conf", 'w') as f:
        f.write(encoded_conf)

    ssh_cmd(client, f"cp {DEPLOY_DIR}/nginx-math-tutor.conf /etc/nginx/sites-available/math-tutor")
    ssh_cmd(client, "ls /etc/nginx/sites-enabled/math-tutor 2>/dev/null || ln -s /etc/nginx/sites-available/math-tutor /etc/nginx/sites-enabled/math-tutor")
    ssh_cmd(client, "rm -f /etc/nginx/sites-enabled/default")
    ssh_cmd(client, "nginx -t")
    print("  Nginx configured.")

    # 8. Setup systemd and start services
    print("\n[8/8] Setting up systemd and starting...")
    service_conf = f'''[Unit]
Description=Math Home Tutor Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={DEPLOY_DIR}/backend
ExecStart=python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
StandardOutput=append:{DEPLOY_DIR}/logs/backend.log
StandardError=append:{DEPLOY_DIR}/logs/backend_error.log

[Install]
WantedBy=multi-user.target
'''
    encoded_svc = service_conf.encode('utf-8')
    with sftp.open(f"{DEPLOY_DIR}/math-tutor.service", 'w') as f:
        f.write(encoded_svc)

    ssh_cmd(client, f"cp {DEPLOY_DIR}/math-tutor.service /etc/systemd/system/math-tutor.service")
    ssh_cmd(client, "systemctl daemon-reload")
    ssh_cmd(client, "systemctl enable math-tutor")
    ssh_cmd(client, "systemctl restart math-tutor")
    ssh_cmd(client, "systemctl restart nginx")

    print("\n  Waiting for services to start...")
    import time
    time.sleep(3)

    out = ssh_cmd(client, "systemctl status math-tutor --no-pager | head -5")
    print(out)
    out = ssh_cmd(client, "systemctl status nginx --no-pager | head -5")
    print(out)

    sftp.close()
    client.close()

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print(f"Access: http://{HOST}")
    print("=" * 60)

if __name__ == "__main__":
    deploy()
