@echo off
rem Serves the W5 Trip Explorer at http://localhost:8767/ and opens the browser.
cd /d "%~dp0"
start "" http://localhost:8767/
python -m http.server 8767
