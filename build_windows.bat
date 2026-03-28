@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
set "DIST=%ROOT%dist"
set "BUILD=%ROOT%build"
set "SPEC=%ROOT%moodtracker.spec"
set "VERSION_FILE=%ROOT%windows_version_info.txt"
set "ICON_FILE=%ROOT%app.ico"
set "EXE=%DIST%\MoodTracker.exe"
set "INSTALLER=%ROOT%MoodTracker-Setup.exe"
set "PY_CMD="
set "PY_ARGS="
set "SKIP_INSTALLER=0"
set "CLEAN=0"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="-SkipInstaller" (
    set "SKIP_INSTALLER=1"
    shift
    goto parse_args
)
if /I "%~1"=="--skipinstaller" (
    set "SKIP_INSTALLER=1"
    shift
    goto parse_args
)
if /I "%~1"=="-Clean" (
    set "CLEAN=1"
    shift
    goto parse_args
)
if /I "%~1"=="--clean" (
    set "CLEAN=1"
    shift
    goto parse_args
)
echo Parametro no reconocido: %~1
echo Usa -Clean y/o -SkipInstaller
exit /b 1

:args_done
echo.
echo MoodTracker - Build para Windows
echo.

if "%CLEAN%"=="1" (
    if exist "%DIST%" rmdir /s /q "%DIST%"
    if exist "%BUILD%" rmdir /s /q "%BUILD%"
    if exist "%INSTALLER%" del /q "%INSTALLER%"
)

where py >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=py"
    set "PY_ARGS=-3"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=python"
    ) else (
        echo No se encontro Python 3.
        echo Instala Python 3 en la maquina de build y volve a ejecutar este archivo.
        exit /b 1
    )
)

echo [1/4] Verificando dependencias de build...
call "%PY_CMD%" %PY_ARGS% -m pip install pyinstaller matplotlib
if errorlevel 1 (
    echo Fallo la instalacion de dependencias.
    exit /b 1
)

echo [2/4] Generando ejecutable original en Python...
if exist "%SPEC%" (
    call "%PY_CMD%" %PY_ARGS% -m PyInstaller --noconfirm --clean "%SPEC%"
) else (
    if exist "%ICON_FILE%" (
        echo      Icono detectado: %ICON_FILE%
        call "%PY_CMD%" %PY_ARGS% -m PyInstaller --noconfirm --clean --onefile --windowed --name MoodTracker --collect-submodules matplotlib --version-file "%VERSION_FILE%" --icon "%ICON_FILE%" "%ROOT%moodtracker.py"
    ) else (
        echo      Icono no encontrado. Se usara el icono por defecto.
        call "%PY_CMD%" %PY_ARGS% -m PyInstaller --noconfirm --clean --onefile --windowed --name MoodTracker --collect-submodules matplotlib --version-file "%VERSION_FILE%" "%ROOT%moodtracker.py"
    )
)
if errorlevel 1 (
    echo Fallo la generacion del ejecutable.
    exit /b 1
)

if not exist "%EXE%" (
    echo No se genero %EXE%
    exit /b 1
)

if "%SKIP_INSTALLER%"=="1" (
    echo [3/4] Instalador omitido por parametro
    echo [4/4] Build completada
    echo Ejecutable: %EXE%
    exit /b 0
)

echo [3/4] Generando instalador...
set "ISCC_CMD="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_CMD=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else (
    if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
        set "ISCC_CMD=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    ) else (
        where iscc >nul 2>nul
        if not errorlevel 1 (
            for /f "delims=" %%I in ('where iscc') do (
                set "ISCC_CMD=%%I"
                goto iscc_found
            )
        )
    )
)

:iscc_found
if not defined ISCC_CMD (
    echo No se encontro Inno Setup 6.
    echo Instala Inno Setup 6 en la maquina de build para generar MoodTracker-Setup.exe.
    exit /b 1
)

if exist "%INSTALLER%" del /q "%INSTALLER%"
call "%ISCC_CMD%" /DMyAppVersion=3.0.0 /DMyAppPublisher=MoodTracker "%ROOT%installer_windows.iss"
if errorlevel 1 (
    echo Fallo la generacion del instalador.
    exit /b 1
)

if not exist "%INSTALLER%" (
    echo No se genero %INSTALLER%
    exit /b 1
)

echo [4/4] Build completada
echo Ejecutable: %EXE%
echo Instalador: %INSTALLER%
exit /b 0
