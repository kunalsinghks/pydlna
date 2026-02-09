# Building PyDLNA Distribution Packages

This guide explains how to build all distribution formats for PyDLNA.

## Prerequisites

1. **Python 3.11+** installed
2. **PyInstaller** for creating executables
3. **Inno Setup** (optional, for installer)

## Step 1: Install Build Dependencies

```bash
pip install pyinstaller
```

## Step 2: Build Standalone Executable

```bash
python build_exe.py
```

This creates `dist/PyDLNA.exe` - a standalone executable with all dependencies bundled.

**Output:**
- `dist/PyDLNA.exe` (~50 MB)

## Step 3: Create Portable Package

```bash
python build_packages.py
```

This creates:
- `dist/PyDLNA-Portable.zip` - Ready-to-use portable version
- `installer.iss` - Inno Setup script for installer

**Portable Package Contents:**
- `PyDLNA.exe`
- `config.json`
- `README.txt`

## Step 4: Create Installer (Optional)

### Install Inno Setup
1. Download from https://jrsoftware.org/isdl.php
2. Install to default location

### Build Installer
```bash
# Using Inno Setup GUI
1. Open installer.iss in Inno Setup
2. Click Build → Compile
3. Installer will be created in dist/PyDLNA-Setup.exe

# Using Command Line
iscc installer.iss
```

**Output:**
- `dist/PyDLNA-Setup.exe` (~50 MB)

## Distribution Checklist

Before releasing:

- [ ] Test standalone executable
- [ ] Test portable package
- [ ] Test installer
- [ ] Verify all versions on clean Windows install
- [ ] Check file sizes
- [ ] Update version numbers
- [ ] Create GitHub release
- [ ] Upload all packages to GitHub

## File Sizes (Approximate)

- Standalone EXE: ~50 MB
- Portable ZIP: ~50 MB
- Installer: ~50 MB

## Troubleshooting

### "Module not found" errors
Add missing modules to `build_exe.py` hidden imports:
```python
'--hidden-import=module_name',
```

### Large executable size
Exclude unnecessary modules in `build_exe.py`:
```python
'--exclude-module=module_name',
```

### Antivirus false positives
This is common with PyInstaller. Solutions:
1. Sign the executable with a code signing certificate
2. Submit to antivirus vendors as false positive
3. Build with `--noupx` flag (already enabled)

## GitHub Release Process

1. **Tag the release:**
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

2. **Create GitHub Release:**
- Go to Releases → Draft a new release
- Choose the tag
- Add release notes
- Upload all distribution files:
  - PyDLNA-Setup.exe
  - PyDLNA-Portable.zip
  - Source code (auto-generated)

3. **Update download links in README.md and docs/index.html**

## Continuous Integration (Future)

Consider setting up GitHub Actions to automatically build releases:
- Trigger on new tags
- Build all packages
- Upload to GitHub Releases
- Update documentation

Example workflow: `.github/workflows/build.yml`
