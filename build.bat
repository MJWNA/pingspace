@echo off
rem Local build of dist\PingSpace.exe, same as the release workflow.
rem Uses a clean virtual environment so only what the app needs is bundled.
python -m venv .build-venv || exit /b 1
call .build-venv\Scripts\activate.bat
python -m pip install --quiet -r requirements.txt "pyinstaller>=6.10" || exit /b 1
python -m unittest discover -s tests || exit /b 1
pyinstaller --noconfirm --clean --onefile --noconsole --uac-admin ^
  --name PingSpace --icon assets/pingspace.ico ^
  --add-data "ui:ui" --add-data "ips.json:." --add-data "data/gcp_ranges_snapshot.json:data" ^
  main.py || exit /b 1
echo.
echo Built dist\PingSpace.exe
