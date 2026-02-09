import requests
import os
import sys

TOKEN = "YOUR_TOKEN_HERE"
OWNER = "kunalsinghks"
REPO = "pydlna"
TAG = "v1.0.0"
FILEPATH = "dist/PyDLNA-Setup.exe"
FILENAME = "PyDLNA-Setup.exe"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

print(f"Checking existing release {TAG}...")
r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{TAG}", headers=headers)

if r.status_code != 200:
    print(f"Release not found: {r.status_code}")
    sys.exit(1)

release = r.json()
upload_url = release["upload_url"].replace("{?name,label}", "")

# Check for existing assets
for asset in release.get("assets", []):
    if asset["name"] == FILENAME:
        print(f"Deleting existing asset {asset['id']} ({asset['name']})...")
        r_del = requests.delete(asset["url"], headers=headers)
        if r_del.status_code == 204:
            print("Deleted successfully.")
        else:
            print(f"Failed to delete: {r_del.status_code}")

# Upload new asset
if os.path.exists(FILEPATH):
    print(f"Uploading {FILENAME}...")
    size = os.path.getsize(FILEPATH)
    print(f"Size: {size / 1024 / 1024:.2f} MB")
    
    with open(FILEPATH, "rb") as f:
        upload_headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/octet-stream",
        }
        r2 = requests.post(
            f"{upload_url}?name={FILENAME}",
            headers=upload_headers,
            data=f
        )
        if r2.status_code == 201:
            print(f"✅ Uploaded successfully!")
            print(f"Download URL: {r2.json()['browser_download_url']}")
        else:
            print(f"❌ Failed upload: {r2.status_code}")
            print(r2.text[:200])
else:
    print(f"File not found: {FILEPATH}")
