@echo off
echo ========================================
echo   Arret des serveurs du jeu
echo ========================================
echo.

echo Arret du backend Django (Python)...
taskkill /F /IM python.exe /T >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Backend arrete
) else (
    echo   [INFO] Aucun processus Python en cours
)

echo.
echo Arret du frontend React (Node)...
taskkill /F /IM node.exe /T >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Frontend arrete
) else (
    echo   [INFO] Aucun processus Node en cours
)

echo.
echo ========================================
echo   Serveurs arretes avec succes!
echo ========================================
echo.
pause
