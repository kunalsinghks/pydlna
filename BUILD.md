# Building PyDLNA Distribution Packages

This guide explains how to build all distribution formats for PyDLNA v1.1.0+.

## Prerequisites

1. **Python 3.11+** installed
2. **PyInstaller** (`pip install pyinstaller`)
3. **Inno Setup** (Version 6+) for creating the installer
4. **Git** (optional, for version control)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Step 2: Build Standalone Executable

This creates a single file executable (`PyDLNA.exe`) without a console window.

```bash
python build_exe.py
```

**Output:**
- `dist/PyDLNA.exe` (~30 MB)

This script uses `run.py` as the entry point to ensure all imports work correctly in the frozen environment.

## Step 3: Create Installer (Recommended)

1. Ensure Inno Setup is installed.
2. Run the Inno Setup compiler:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Output:**
- `dist/PyDLNA-v1.1.0-Setup.exe` (~31 MB)

This installer includes:
- Desktop shortcut
- Start Menu entry
- Uninstaller
- Automatic firewall rules (if configured)

## Step 4: Create Portable Package

For users who don't want to install:

```powershell
New-Item -ItemType Directory -Force -Path dist/PyDLNA-Portable
Copy-Item dist/PyDLNA.exe dist/PyDLNA-Portable/
Copy-Item config.json dist/PyDLNA-Portable/
Compress-Archive -Path dist/PyDLNA-Portable/* -DestinationPath dist/PyDLNA-Portable.zip -Force
```

**Output:**
- `dist/PyDLNA-Portable.zip`

## Distribution Checklist

Before releasing:

- [ ] Delete `dist/` and `build/` folders
- [ ] Reset `config.json` to defaults (remove personal paths/usernames)
- [ ] Run `python build_exe.py`
- [ ] Run `ISCC installer.iss`
- [ ] Test the installer on a clean VM/Sandbox
- [ ] Verify version number in `installer.iss`
- [ ] Upload to GitHub Releases

## Troubleshooting

### "ImportError: relative import..."
Ensure you are building with `build_exe.py` which uses `run.py`, NOT `pydlna/main.py` directly.

### Console Window Appears
The executable is built with `--noconsole`. If a window appears, check if the build script has `--noconsole` or `--windowed`.

### "Failed to execute script"
Check the logs. If running `PyDLNA.exe` fails silently, try building *without* `--noconsole` temporarily to see the error output.
