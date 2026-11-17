@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no esta instalado.
    echo Instala las dependencias con:
    echo python -m pip install -r requirements.txt pyinstaller
    exit /b 1
)

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name "El Respiro de la Sierra" ^
    --icon "%CD%\recursos\imagenes\Logo.ico" ^
    --add-data "%CD%\recursos;recursos" ^
    --distpath dist ^
    --workpath build\work ^
    --specpath build ^
    main.py

if errorlevel 1 (
    echo Error al crear el ejecutable.
    exit /b 1
)

echo Ejecutable creado en: dist\El Respiro de la Sierra.exe
