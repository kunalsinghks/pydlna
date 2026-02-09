@echo off
cd /d "%~dp0"
echo Starting PyDLNA Server...
python -m pydlna.main
pause
