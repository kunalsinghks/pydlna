"""
Create portable and installer packages for PyDLNA
"""

import os
import shutil
import zipfile
from pathlib import Path
import subprocess

def create_portable():
    """Create portable ZIP package"""
    print("📦 Creating portable package...")
    
    portable_dir = Path('dist/PyDLNA-Portable')
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    shutil.copy('dist/PyDLNA.exe', portable_dir / 'PyDLNA.exe')
    
    # Copy default config
    shutil.copy('config.json', portable_dir / 'config.json')
    
    # Create README
    with open(portable_dir / 'README.txt', 'w') as f:
        f.write("""PyDLNA - Portable Version

Quick Start:
1. Run PyDLNA.exe
2. Open http://localhost:8200 in your browser
3. Add your media folders in the "Server Admin" tab

Configuration:
- Edit config.json to customize settings
- Server name, port, and media paths can be changed

Support:
- GitHub: https://github.com/YOUR_USERNAME/pydlna
- Issues: https://github.com/YOUR_USERNAME/pydlna/issues

Enjoy streaming your media!
""")
    
    # Create ZIP
    zip_path = Path('dist/PyDLNA-Portable.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in portable_dir.rglob('*'):
            if file.is_file():
                zipf.write(file, file.relative_to(portable_dir.parent))
    
    print(f"✅ Portable package created: {zip_path}")
    print(f"📊 Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Cleanup temp directory
    shutil.rmtree(portable_dir)

def create_installer():
    """Create Inno Setup installer"""
    print("📦 Creating installer...")
    
    # Create Inno Setup script
    iss_content = f"""
; PyDLNA Installer Script

#define MyAppName "PyDLNA"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Kunal"
#define MyAppURL "https://github.com/YOUR_USERNAME/pydlna"
#define MyAppExeName "PyDLNA.exe"

[Setup]
AppId={{{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=PyDLNA-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\\PyDLNA.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{{app}}"; Flags: ignoreversion onlyifdoesntexist
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('PyDLNA has been installed successfully!' + #13#10 + #13#10 + 
           'Access the web interface at: http://localhost:8200' + #13#10 + #13#10 +
           'Click OK to launch PyDLNA.', mbInformation, MB_OK);
  end;
end;
"""
    
    iss_path = Path('installer.iss')
    with open(iss_path, 'w') as f:
        f.write(iss_content)
    
    print("✅ Inno Setup script created: installer.iss")
    print("\n⚠️  To create the installer:")
    print("1. Install Inno Setup from https://jrsoftware.org/isdl.php")
    print("2. Run: iscc installer.iss")
    print("3. Installer will be created in dist/PyDLNA-Setup.exe")

if __name__ == '__main__':
    # Check if executable exists
    if not Path('dist/PyDLNA.exe').exists():
        print("❌ Error: PyDLNA.exe not found!")
        print("Run 'python build_exe.py' first to build the executable.")
        exit(1)
    
    # Create packages
    create_portable()
    create_installer()
    
    print("\n✅ All packages created successfully!")
    print("\n📦 Distribution files:")
    print("  - dist/PyDLNA.exe (Standalone)")
    print("  - dist/PyDLNA-Portable.zip (Portable)")
    print("  - installer.iss (Installer script)")
