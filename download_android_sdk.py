import urllib.request
import os, time

url = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
dest = os.path.expandvars(r"%LOCALAPPDATA%\Android\cmdline-tools.zip")
dest_part = dest + ".part"

# Remove corrupted old file
for f in [dest, dest_part]:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed old: {f}")

print(f"Downloading Android SDK cmdline-tools (~150MB)...")
req = urllib.request.Request(url)
start = time.time()
last_print = 0

with urllib.request.urlopen(req, timeout=300) as response, open(dest_part, "wb") as f:
    total = int(response.headers.get("Content-Length", 0))
    downloaded = 0
    while True:
        chunk = response.read(8192)
        if not chunk:
            break
        f.write(chunk)
        downloaded += len(chunk)
        if time.time() - last_print > 1.5:
            pct = downloaded / max(total, 1) * 100
            speed = downloaded / max(time.time() - start, 1) / 1024 / 1024
            print(f"  {pct:.0f}% | {downloaded/1024/1024:.1f}/{total/1024/1024:.1f} MB | {speed:.1f} MB/s", end="\r")
            last_print = time.time()

os.rename(dest_part, dest)
elapsed = time.time() - start
size = os.path.getsize(dest)
print(f"\nDone: {size/1024/1024:.1f} MB in {elapsed:.0f}s")

# Extract to Android SDK location
import zipfile
sdk_root = os.path.expandvars(r"%LOCALAPPDATA%\Android")
cmdline = os.path.join(sdk_root, "cmdline-tools", "latest")
os.makedirs(cmdline, exist_ok=True)

print(f"Extracting to {cmdline}...")
with zipfile.ZipFile(dest) as z:
    # The zip has a "cmdline-tools/" prefix, strip it
    for member in z.namelist():
        # Remove "cmdline-tools/" prefix
        rel = member.split("/", 1)[1] if "/" in member else member
        if not rel:
            continue
        target = os.path.join(cmdline, rel)
        if member.endswith("/"):
            os.makedirs(target, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(member) as src, open(target, "wb") as dst:
                dst.write(src.read())
print("Extracted OK")

# Verify sdkmanager exists
sdkmanager = os.path.join(cmdline, "bin", "sdkmanager.bat")
if os.path.exists(sdkmanager):
    print(f"sdkmanager found: {sdkmanager}")
else:
    print("sdkmanager NOT found - checking bin location...")
    for root, dirs, files in os.walk(cmdline):
        for f in files:
            if "sdkmanager" in f:
                print(f"  Found: {os.path.join(root, f)}")
