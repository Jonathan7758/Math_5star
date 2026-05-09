import urllib.request
import os
import time

url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.29.3-stable.zip"
dest = r"C:\Users\PC\AppData\Local\Temp\opencode\flutter_new.zip"
dest_part = dest + ".part"

# Check existing partial download
existing_size = 0
if os.path.exists(dest_part):
    existing_size = os.path.getsize(dest_part)
    print(f"Resuming from {existing_size / 1024 / 1024:.1f} MB")

# Also check if we have a complete download already
if os.path.exists(dest):
    size = os.path.getsize(dest)
    if size > 1000 * 1024 * 1024:
        print(f"Already downloaded: {size / 1024 / 1024:.1f} MB")
        exit(0)
    else:
        os.remove(dest)

# Download with resume
req = urllib.request.Request(url)
if existing_size > 0:
    req.add_header("Range", f"bytes={existing_size}-")

print("Downloading Flutter SDK (~1.1GB)...")
start_time = time.time()
last_print = 0

with urllib.request.urlopen(req, timeout=300) as response, open(dest_part, "ab") as f:
    total = existing_size + int(response.headers.get("Content-Length", 0))
    downloaded = existing_size

    while True:
        chunk = response.read(8192)
        if not chunk:
            break
        f.write(chunk)
        downloaded += len(chunk)

        if time.time() - last_print > 2:
            pct = downloaded / max(total, 1) * 100
            speed = (downloaded - existing_size) / max(time.time() - start_time, 1) / 1024 / 1024
            print(f"  {pct:.1f}% | {downloaded / 1024 / 1024:.1f}/{total / 1024 / 1024:.1f} MB | {speed:.1f} MB/s", end="\r")
            last_print = time.time()

# Rename on success
if os.path.exists(dest):
    os.remove(dest)
os.rename(dest_part, dest)

elapsed = time.time() - start_time
size = os.path.getsize(dest)
print(f"\nDownloaded: {size / 1024 / 1024:.1f} MB in {elapsed:.0f}s ({size / 1024 / 1024 / elapsed:.1f} MB/s)")
