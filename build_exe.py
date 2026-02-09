"""
PyInstaller build script for PyDLNA
Creates standalone executable with all dependencies bundled
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# Clean previous builds
if Path('build').exists():
    shutil.rmtree('build')
if Path('dist').exists():
    shutil.rmtree('dist')

# Get project root
root = Path(__file__).parent

# Build configuration
PyInstaller.__main__.run([
    'pydlna/main.py',
    '--name=PyDLNA',
    '--onefile',
    '--windowed',
    '--icon=assets/icon.ico' if Path('assets/icon.ico').exists() else '',
    
    # Include data files
    '--add-data=pydlna/web/templates;pydlna/web/templates',
    
    # Hidden imports
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.protocols.websockets',
    '--hidden-import=uvicorn.protocols.websockets.auto',
    '--hidden-import=uvicorn.lifespan',
    '--hidden-import=uvicorn.lifespan.on',
    '--hidden-import=sqlalchemy.ext.asyncio',
    '--hidden-import=aiosqlite',
    
    # Exclude unnecessary modules
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=scipy',
    '--exclude-module=tkinter',
    
    # Optimization
    '--strip',
    '--noupx',
    
    # Clean build
    '--clean',
])

print("\n✅ Build complete!")
print(f"📦 Executable: {root / 'dist' / 'PyDLNA.exe'}")
print(f"📊 Size: {(root / 'dist' / 'PyDLNA.exe').stat().st_size / 1024 / 1024:.2f} MB")
