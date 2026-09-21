@echo off
setlocal

cd /d "%~dp0"

echo.
echo ========================================
echo     Ultimate Stockfish Reader
echo          BUILDING Chess.exe
echo ========================================
echo.

if not exist "main.py" (
    echo [ERROR] main.py not found.
    pause
    exit /b 1
)

if not exist "assets\app.ico" (
    echo [ERROR] assets\app.ico not found.
    pause
    exit /b 1
)

if not exist "engine\bin\stockfish.exe" (
    echo [ERROR] engine\bin\stockfish.exe not found.
    pause
    exit /b 1
)

echo [INFO] Cleaning old build...

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo.
echo [INFO] Building...

pyinstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name Chess ^
    --icon "assets\app.ico" ^
    --add-binary "engine\bin\stockfish.exe;engine\bin" ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo          BUILD SUCCESS
echo ========================================
echo.
echo Output:
echo dist\Chess.exe
echo.

pause
endlocal