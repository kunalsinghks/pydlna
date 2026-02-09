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
# Using run.py as the entry point to fix import issues
PyInstaller.__main__.run([
    'run.py',
    '--name=PyDLNA',
    '--onedir',   # Use directory mode for better stability
    '--noconsole',  # Hide console window
    '--icon=favicon.ico' if Path('favicon.ico').exists() else '',
    
    # Include data files - VERY IMPORTANT
    '--add-data=pydlna/web/templates;pydlna/web/templates',
    '--add-data=config.json;.',  # Include default config if needed
    
    # Hidden imports - Uvicorn and SQLAlchemy often need these
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
    '--hidden-import=sqlite3',
    '--hidden-import=engineio.async_drivers.aiohttp',
    
    # Exclude unnecessary modules to save space
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=scipy',
    '--exclude-module=ipython',
    '--exclude-module=notebook',
    
    # Optimization
    '--strip',
    '--noupx',
    
    # Clean build
    '--clean',
])

print("\n✅ Build complete!")
print(f"📦 Executable: {root / 'dist' / 'PyDLNA.exe'}")
if (root / 'dist' / 'PyDLNA.exe').exists():
    print(f"📊 Size: {(root / 'dist' / 'PyDLNA.exe').stat().st_size / 1024 / 1024:.2f} MB")
