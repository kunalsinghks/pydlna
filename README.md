# PyDLNA - Premium Local Media Server

<div align="center">

![PyDLNA Logo](https://img.shields.io/badge/PyDLNA-Media%20Server-blue?style=for-the-badge)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow?style=for-the-badge&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)](https://github.com)

**Stream your local media to any DLNA/UPnP device on your network**

[Download](https://github.com/kunalsinghks/pydlna/releases) • [Documentation](#features) • [Report Bug](https://github.com/kunalsinghks/pydlna/issues)

</div>

---

## 🎯 Features

- **🌐 Universal Compatibility**: Works with VLC, Smart TVs, Game Consoles, and any DLNA/UPnP client
- **⚡ Fast Streaming**: HTTP Range support for instant seeking and fast-forward
- **🎨 Beautiful Web UI**: Modern, responsive dashboard for browsing and managing media
- **📁 Multi-Library Support**: Add multiple media folders from different drives
- **🔍 Auto-Discovery**: Automatically appears in network players via SSDP/UPnP
- **🎬 Rich Metadata**: Extracts duration, resolution, audio/subtitle tracks from videos
- **🖥️ Desktop Integration**: Native Windows installer with desktop icon and system tray support
- **🔒 Optional Authentication**: Secure your server with username/password
- **💾 Lightweight**: Minimal resource usage with SQLite database

---

## 📥 Download

### Windows (v1.1.1)

| Version | Description | Download |
|---------|-------------|----------|
| **Installer** | Recommended. Includes desktop icon & uninstaller. | [PyDLNA-v1.1.1-Setup.exe](https://github.com/kunalsinghks/pydlna/releases/download/v1.1.1/PyDLNA-v1.1.1-Setup.exe) |
| **Portable** | No installation required. Just extract and run. | [PyDLNA-Portable.zip](https://github.com/kunalsinghks/pydlna/releases/download/v1.1.1/PyDLNA-Portable.zip) |
| **Source** | For developers. | [Source.zip](https://github.com/kunalsinghks/pydlna/archive/refs/tags/v1.1.1.zip) |

### System Requirements
- Windows 10/11 (64-bit)
- 50 MB free disk space
- Network connection

---

## 🚀 Quick Start

### Option 1: Installer (Recommended)
1. Download `PyDLNA-v1.1.0-Setup.exe`
2. Run the installer and follow the prompts
3. Launch **PyDLNA** from the Desktop or Start Menu
4. Access the web interface at `http://localhost:8200`

### Option 2: Portable
1. Download `PyDLNA-Portable.zip`
2. Extract to any folder
3. Run `PyDLNA.exe`
4. Access the web interface at `http://localhost:8200`

### Option 3: From Source
```bash
# Clone the repository
git clone https://github.com/kunalsinghks/pydlna.git
cd pydlna

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

---

## 📖 Usage

### Adding Media Libraries
1. Open the web interface at `http://localhost:8200`
2. Click on **"Server Admin"** tab
3. Under **"Media Libraries"**, enter your media folder path
4. Click **"Add Path"**
5. The server will automatically scan and index your media

### Accessing from DLNA Clients

#### VLC Media Player
1. Open VLC
2. Go to **View** → **Playlist** (Ctrl+L)
3. Click **"Local Network"** → **Universal Plug'n'Play**
4. Look for **"PyDLNA Server"**
5. Browse and play your media

#### Smart TV
1. Open your TV's media player app
2. Look for **"Network"** or **"DLNA Servers"**
3. Select **"PyDLNA Server"**
4. Browse and play

#### Mobile Devices
Use any DLNA/UPnP app:
- **Android**: VLC, BubbleUPnP, Kodi
- **iOS**: VLC, nPlayer, Infuse

---

## ⚙️ Configuration

### Server Settings
Settings are stored in `config.json` in the application directory (or `%AppData%` for installed version).

Default configuration:
```json
{
  "friendly_name": "PyDLNA Server",
  "port": 8200,
  "media_paths": [],
  "username": "admin",
  "password": null
}
```

---

## 🛠️ Advanced Features

### FFmpeg Integration
PyDLNA uses FFmpeg (if available) to extract rich metadata:
- Video duration and resolution
- Audio track count
- Subtitle track detection

**Install FFmpeg** (optional but recommended):
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Add to system PATH
3. Restart PyDLNA

### Authentication
Protect your server with HTTP Basic Auth by setting a password in the Web UI or `config.json`.

### Troubleshooting

#### Server not appearing in VLC/TV
1. **Check firewall**: Allow PyDLNA through Windows Firewall when prompted.
2. **Verify network**: Ensure server and client are on the same Wi-Fi/Ethernet.

#### Videos won't play
1. **Check codec support**: Some devices don't support MKV/HEVC.
2. **Try VLC**: VLC has the best format support.

---

## 🏗️ Building from Source

### Prerequisites
- Python 3.11+
- PyInstaller (for executable)
- Inno Setup (for installer)

### Build Steps
```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Build Executable
python build_exe.py

# 3. Build Installer (requires Inno Setup)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI for the web framework
- SQLModel for database management
- The open-source DLNA/UPnP community

---

<div align="center">

**PyDLNA** - Simple, Fast, Open Source.

⭐ Star this repo if you find it useful!

</div>
