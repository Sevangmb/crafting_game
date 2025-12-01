@echo off
echo ========================================
echo   Demarrage du jeu Crafting Game
echo ========================================
echo.

REM Verifier si le venv existe
if not exist "venv\Scripts\activate.bat" (
    echo ERREUR: Environnement virtuel non trouve!
    echo Veuillez creer le venv d'abord avec: python -m venv venv
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo [1/4] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Verifier si les migrations sont a jour
echo [2/4] Verification des migrations...
python manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo Migrations necessaires detectees, application...
    python manage.py migrate
)

REM Creer le dossier logs s'il n'existe pas
if not exist "logs" mkdir logs

REM Demarrer le backend Django en arriere-plan
echo [3/4] Demarrage du backend Django en arriere-plan...
start /B "" venv\Scripts\python.exe manage.py runserver > logs\backend.log 2>&1

REM Attendre que le backend demarre
echo Attente du demarrage du backend...
timeout /t 3 /nobreak >nul

REM Demarrer le frontend React en arriere-plan
echo [4/4] Demarrage du frontend React en arriere-plan...
cd frontend
start /B "" cmd /c "npm start > ..\logs\frontend.log 2>&1"
cd ..

echo.
echo ========================================
echo   Jeu demarre avec succes!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Les serveurs tournent en arriere-plan (sans fenetre).
echo.
echo Logs disponibles dans:
echo   - logs\backend.log
echo   - logs\frontend.log
echo.
echo Pour arreter les serveurs:
echo   - Utilisez stop_game.bat
echo   - Ou: taskkill /F /IM python.exe /T
echo         taskkill /F /IM node.exe /T
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul
