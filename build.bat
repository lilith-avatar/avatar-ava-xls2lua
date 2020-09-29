:: Build ava-xls2lua with PyInstaller (Windows)
:: Copyright 2020, Lilith Games, Project DaVinci, Avatar Team
:: Author: Yuancheng Zhang
:: git repo: https://github.com/lilith-avatar/avatar-ava-xls2lua
powershell -command "pyinstaller .\ava-x2l.spec;cp .\dist\ava-x2l.exe .\ava-x2l.exe"