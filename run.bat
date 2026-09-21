@echo off
setlocal

REM ============================================================
REM Ultimate Stockfish Reader
REM Create Desktop shortcut automatically
REM ============================================================

cd /d "%~dp0"

set "PROJECT=%~dp0"
set "PROJECT=%PROJECT:~0,-1%"
set "MAIN=%PROJECT%\main.py"
set "VENV_PYTHONW=%PROJECT%\.venv\Scripts\pythonw.exe"
set "VENV_PYTHON=%PROJECT%\.venv\Scripts\python.exe"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Ultimate Stockfish Reader.lnk"
set "ICON=%PROJECT%\assets\app.ico"

echo.
echo ========================================
echo   Ultimate Stockfish Reader
echo   Desktop Shortcut Installer
echo ========================================
echo.

REM ------------------------------------------------------------
REM Check main.py
REM ------------------------------------------------------------

if not exist "%MAIN%" (
    echo [ERROR] Cannot find:
    echo %MAIN%
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Prefer virtual environment
REM ------------------------------------------------------------

if exist "%VENV_PYTHONW%" (
    set "PYTHONW=%VENV_PYTHONW%"
    echo [INFO] Using virtual environment:
    echo %PYTHONW%
    goto :CREATE_SHORTCUT
)

REM ------------------------------------------------------------
REM Fallback to system pythonw
REM ------------------------------------------------------------

where pythonw.exe >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%P in ('where pythonw.exe') do (
        set "PYTHONW=%%P"
        goto :CREATE_SHORTCUT
    )
)

echo [ERROR] pythonw.exe was not found.
echo.
echo Make sure Python is installed.
pause
exit /b 1


:CREATE_SHORTCUT

REM ------------------------------------------------------------
REM Create shortcut with PowerShell
REM ------------------------------------------------------------

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$project = '%PROJECT%';" ^
    "$target = '%PYTHONW%';" ^
    "$main = '%MAIN%';" ^
    "$shortcutPath = '%SHORTCUT%';" ^
    "$icon = '%ICON%';" ^
    "$shell = New-Object -ComObject WScript.Shell;" ^
    "$shortcut = $shell.CreateShortcut($shortcutPath);" ^
    "$shortcut.TargetPath = $target;" ^
    "$shortcut.Arguments = '""' + $main + '""';" ^
    "$shortcut.WorkingDirectory = $project;" ^
    "$shortcut.Description = 'Ultimate Stockfish Reader';" ^
    "if (Test-Path $icon) { $shortcut.IconLocation = $icon } else { $shortcut.IconLocation = $target + ',0' };" ^
    "$shortcut.Save();"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to create Desktop shortcut.
    pause
    exit /b 1
)

echo.
echo [OK] Desktop shortcut created:
echo %SHORTCUT%
echo.
echo Double-click "Ultimate Stockfish Reader" on the Desktop to launch the app.
echo.

REM ------------------------------------------------------------
REM Optional: do not leave a command window open
REM ------------------------------------------------------------

pause

endlocal
