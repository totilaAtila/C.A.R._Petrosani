@echo off
REM ============================================================================
REM Script de build pentru CARpetrosani - Windows
REM ============================================================================
REM
REM Acest script creeaza executabilul Windows al aplicatiei CARpetrosani
REM folosind PyInstaller cu configuratia din CARpetrosani.spec
REM
REM Prerequisite:
REM - Python 3.11+ instalat
REM - PyInstaller instalat (pip install pyinstaller)
REM - Toate dependintele din requirements.txt instalate
REM
REM Utilizare:
REM   build_windows.bat
REM
REM Output:
REM   dist\CARpetrosani.exe - Executabilul final pentru distributie
REM ============================================================================

echo.
echo ============================================================================
echo Build CARpetrosani pentru Windows
echo ============================================================================
echo.

REM Verificare Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nu este instalat sau nu este in PATH!
    echo.
    echo Instalati Python de la https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detectat:
python --version
echo.

REM Verificare PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller nu este instalat!
    echo.
    echo Instalare PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Instalare PyInstaller esuata!
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller detectat:
pyinstaller --version
echo.

REM Curatare build-uri anterioare
echo [INFO] Curatare build-uri anterioare...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [OK] Curatare completa
echo.

REM Build cu PyInstaller
echo [INFO] Pornire build cu PyInstaller...
echo [INFO] Foloseste configuratia: CARpetrosani.spec
echo.
pyinstaller --clean --noconfirm CARpetrosani.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build esuat!
    echo.
    echo Verificati:
    echo - Toate dependintele sunt instalate (requirements.txt)
    echo - Fisierul CARpetrosani.spec este valid
    echo - Nu exista erori in cod
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [OK] Build complet cu succes!
echo ============================================================================
echo.
echo Executabilul a fost creat:
echo   dist\CARpetrosani.exe
echo.
echo Dimensiune fisier:
dir dist\CARpetrosani.exe | find "CARpetrosani.exe"
echo.
echo Pentru distributie:
echo   1. Copiati dist\CARpetrosani.exe in locatia dorita
echo   2. IMPORTANT: Asigurati-va ca exista arhiva MEMBRII.zip cu parola
echo   3. Rulati executabilul - va solicita parola la pornire
echo.
echo ============================================================================
pause
