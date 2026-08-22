@echo off
rem Starts a tiny local web server for the Trip Explorer and opens it in the browser.
rem (Opening index.html directly from disk does not work: browsers block data loading from file://)
cd /d "%~dp0"
start "" http://localhost:8766/
python -m http.server 8766 --bind 127.0.0.1
