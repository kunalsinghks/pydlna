import requests
import os

TOKEN = "YOUR_TOKEN_HERE"
OWNER = "kunalsinghks"
REPO = "pydlna"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Get release
r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/v1.0.0", headers=headers)
if r.status_code == 200:
    release = r.json()
    upload_url = release["upload_url"].replace("{?name,label}", "")
    
    filepath = "dist/PyDLNA-Portable.zip"
    name = "PyDLNA-Portable.zip"
    
    if os.path.exists(filepath):
        print(f"Uploading {name}...")
        size = os.path.getsize(filepath)
        print(f"Size: {size / 1024 / 1024:.1f} MB")
        
        with open(filepath, "rb") as f:
            upload_headers = {
                "Authorization": f"token {TOKEN}",
                "Content-Type": "application/zip",
            }
            r2 = requests.post(
                f"{upload_url}?name={name}",
                headers=upload_headers,
                data=f
            )
            if r2.status_code == 201:
                print(f"✅ Uploaded successfully!")
                print(f"Download URL: {r2.json()['browser_download_url']}")
            else:
                print(f"❌ Failed: {r2.status_code}")
                print(r2.text[:500])
else:
    print(f"Failed to get release: {r.status_code}")
