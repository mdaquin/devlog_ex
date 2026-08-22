@echo off
REM Double-cliquer sur ce fichier (Windows) pour lancer le programme.
REM
REM Il se charge de tout : trouver Python, creer un environnement virtuel
REM .venv, installer openpyxl, puis demarrer main.py.

REM Se placer dans le dossier du script, quel que soit l'endroit d'ou on le lance.
cd /d "%~dp0"

echo Preparation du programme...

REM Le lanceur "py" est installe avec Python sur Windows ; sinon on tente "python".
set PYTHON=py -3
%PYTHON% --version >nul 2>&1
if errorlevel 1 set PYTHON=python
%PYTHON% --version >nul 2>&1
if errorlevel 1 goto pas_de_python

REM Creer l'environnement virtuel la premiere fois seulement.
if not exist ".venv\Scripts\python.exe" (
    echo Creation de l'environnement virtuel ^(une seule fois^)...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto erreur_venv
)

REM Installer openpyxl seulement s'il manque.
".venv\Scripts\python.exe" -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    ".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt
    if errorlevel 1 goto erreur_dependances
)

echo Lancement...
REM pythonw.exe lance l'interface sans laisser de fenetre noire ouverte.
start "" ".venv\Scripts\pythonw.exe" main.py
exit /b 0

:pas_de_python
echo.
echo ERREUR : Python est introuvable. Installez-le depuis https://www.python.org/downloads/
echo          en cochant "Add python.exe to PATH".
echo.
pause
exit /b 1

:erreur_venv
echo.
echo ERREUR : impossible de creer l'environnement virtuel.
echo.
pause
exit /b 1

:erreur_dependances
echo.
echo ERREUR : l'installation des dependances a echoue.
echo.
pause
exit /b 1
