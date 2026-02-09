import requests
import os

TOKEN = "YOUR_TOKEN_HERE"
OWNER = "kunalsinghks"
REPO = "pydlna"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Create release
release_data = {
    "tag_name": "v1.0.0",
    "name": "PyDLNA v1.0.0 - Initial Release",
    "body": """## 🎉 PyDLNA v1.0.0 - Initial Release

Premium Local Media Server - Stream to any DLNA/UPnP device on your network!

### ✨ Features
- 🌐 **Universal Compatibility** - Works with VLC, Smart TVs, Game Consoles
- ⚡ **Fast Streaming** - HTTP Range support for instant seeking
- 🎨 **Beautiful Web UI** - Modern dashboard at http://localhost:8200
- 📁 **Multi-Library** - Add multiple media folders
- 🔍 **Auto-Discovery** - Automatically appears in network players via SSDP/UPnP
- 🎬 **Rich Metadata** - Extracts duration, resolution, audio/subtitle tracks

### 📥 Downloads
- **PyDLNA-Setup.exe** - Standalone executable (recommended)
- **PyDLNA-Portable.zip** - Portable version, no installation needed

### 🚀 Quick Start
1. Download and run `PyDLNA-Setup.exe`
2. Open http://localhost:8200 in your browser
3. Add your media folders in "Server Admin"
4. Access from VLC, Smart TV, or any DLNA client!

### 💻 System Requirements
- Windows 10/11 (64-bit)
- 50 MB disk space

### 📝 Note
This is a standalone Python application. Some antivirus may flag it - this is a false positive common with PyInstaller executables.
""",
    "draft": False,
    "prerelease": False
}

print("Creating release...")
r = requests.post(
    f"https://api.github.com/repos/{OWNER}/{REPO}/releases",
    headers=headers,
    json=release_data
)

if r.status_code == 201:
    release = r.json()
    print(f"✅ Release created: {release['html_url']}")
    upload_url = release["upload_url"].replace("{?name,label}", "")
    
    # Upload assets
    files = [
        ("dist/PyDLNA-Setup.exe", "PyDLNA-Setup.exe", "application/octet-stream"),
        ("dist/PyDLNA-Portable.zip", "PyDLNA-Portable.zip", "application/zip")
    ]
    
    for filepath, name, content_type in files:
        if os.path.exists(filepath):
            print(f"Uploading {name}...")
            size = os.path.getsize(filepath)
            print(f"  Size: {size / 1024 / 1024:.1f} MB")
            
            with open(filepath, "rb") as f:
                upload_headers = {
                    "Authorization": f"token {TOKEN}",
                    "Content-Type": content_type,
                }
                r2 = requests.post(
                    f"{upload_url}?name={name}",
                    headers=upload_headers,
                    data=f
                )
                if r2.status_code == 201:
                    print(f"  ✅ Uploaded successfully!")
                else:
                    print(f"  ❌ Failed: {r2.status_code} - {r2.text[:200]}")
        else:
            print(f"❌ File not found: {filepath}")
            
    print("\n🎉 Done! Release URL:", release['html_url'])
    
elif r.status_code == 422:
    print("Release already exists! Checking...")
    # Get existing release
    r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/v1.0.0", headers=headers)
    if r.status_code == 200:
        release = r.json()
        print(f"Found existing release: {release['html_url']}")
else:
    print(f"❌ Failed to create release: {r.status_code}")
    print(r.text)
