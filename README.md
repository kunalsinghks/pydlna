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
- **🖼️ Multi-Format**: Supports videos (MKV, MP4, AVI), audio (MP3, FLAC, WAV), and images
- **🔒 Optional Authentication**: Secure your server with username/password
- **💾 Lightweight**: Minimal resource usage with SQLite database

---

## 📥 Download

### Windows

| Version | Description | Download |
|---------|-------------|----------|
| **Installer** | Recommended for most users | [PyDLNA-Setup.exe](https://github.com/kunalsinghks/pydlna/releases/latest/download/PyDLNA-Setup.exe) |
| **Portable** | No installation required | [PyDLNA-Portable.zip](https://github.com/kunalsinghks/pydlna/releases/latest/download/PyDLNA-Portable.zip) |
| **Source** | For developers | [Source.zip](https://github.com/kunalsinghks/pydlna/archive/refs/heads/main.zip) |

### System Requirements
- Windows 10/11 (64-bit)
- 100 MB free disk space
- Network connection

---

## 🚀 Quick Start

### Option 1: Installer (Recommended)
1. Download `PyDLNA-Setup.exe`
2. Run the installer and follow the prompts
3. Launch PyDLNA from the Start Menu
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
python -m pydlna.main
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
3. Click **"Local Network"** in the sidebar
4. Look for **"Kunals"** (or your custom server name)
5. Browse and play your media

#### Smart TV
1. Open your TV's media player app
2. Look for **"Network"** or **"DLNA Servers"**
3. Select **"Kunals"**
4. Browse and play

#### Mobile Devices
Use any DLNA/UPnP app:
- **Android**: VLC, BubbleUPnP, Kodi
- **iOS**: VLC, nPlayer, Infuse

---

## ⚙️ Configuration

### Server Settings
Edit `config.json` in the installation directory:

```json
{
  "friendly_name": "Kunals",
  "port": 8200,
  "media_paths": ["C:\\Videos", "D:\\Movies"],
  "username": "admin",
  "password": null
}
```

### Command Line Options
```bash
python -m pydlna.main --help

Options:
  --port PORT          Server port (default: 8200)
  --host HOST          Bind address (default: 0.0.0.0)
  --no-gui            Run without GUI window
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
Protect your server with HTTP Basic Auth:

```json
{
  "username": "admin",
  "password": "your_secure_password"
}
```

### Custom Port
If port 8200 is in use:

```json
{
  "port": 9000
}
```

---

## 🐛 Troubleshooting

### Server not appearing in VLC/TV
1. **Check firewall**: Allow Python/PyDLNA through Windows Firewall
2. **Verify network**: Ensure server and client are on the same network
3. **Restart discovery**: Close and reopen VLC/TV app
4. **Check logs**: Look for errors in the console window

### Videos won't play
1. **Check codec support**: Some devices don't support MKV/HEVC
2. **Try different player**: VLC has the best format support
3. **Verify file path**: Ensure media files are accessible

### Slow scanning
1. **Limit scope**: Don't add entire drives, only media folders
2. **Install FFmpeg**: Speeds up metadata extraction
3. **Check disk speed**: Slow external drives can cause delays

### Port 1900 already in use
Another UPnP service is running. Either:
- Disable Windows Media Player Network Sharing
- Stop other DLNA servers
- PyDLNA will still work, but discovery may be limited

---

## 🏗️ Building from Source

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Development Setup
```bash
# Clone repository
git clone https://github.com/kunalsinghks/pydlna.git
cd pydlna

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python -m pydlna.main
```

### Building Executables
```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
python build_exe.py

# Output: dist/PyDLNA.exe
```

---

## 📁 Project Structure

```
pydlna/
├── pydlna/
│   ├── core/           # Core functionality
│   │   └── ssdp.py    # SSDP/UPnP discovery
│   ├── services/       # DLNA services
│   │   ├── cds.py     # Content Directory Service
│   │   └── cms.py     # Connection Manager Service
│   ├── web/           # Web interface
│   │   ├── server.py  # FastAPI application
│   │   └── templates/ # HTML templates
│   ├── config.py      # Configuration management
│   ├── db.py          # Database layer
│   ├── models.py      # Data models
│   ├── scanner.py     # Media scanner
│   └── main.py        # Entry point
├── config.json        # User configuration
├── requirements.txt   # Python dependencies
└── README.md         # This file
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

- FastAPI for the excellent web framework
- SQLModel for elegant database management
- The DLNA/UPnP community for protocol documentation

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/kunalsinghks/pydlna/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kunalsinghks/pydlna/discussions)

---

<div align="center">

**Made with ❤️ by Kunal**

⭐ Star this repo if you find it useful!

</div>
