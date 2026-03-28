@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PROJECT=MoodTracker.Windows.csproj"
set "PUBLISH_DIR=%~dp0publish"
set "APP_NAME=MoodTracker"
set "APP_VERSION=1.0.0"
set "APP_PUBLISHER=MoodTracker"
set "INSTALLER=%~dp0%APP_NAME%-Windows-Setup-%APP_VERSION%.exe"
set "ICON_FILE=%~dp0app.ico"

echo.
echo MoodTracker Windows Native - Build
echo.

where dotnet >nul 2>nul
if errorlevel 1 (
    echo No se encontro dotnet SDK.
    echo Instala .NET 8 SDK en la maquina de build y volve a ejecutar este archivo.
    exit /b 1
)

echo [1/3] Publicando ejecutable autocontenido...
dotnet publish "%PROJECT%" -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -p:DebugType=None -p:DebugSymbols=false -o "%PUBLISH_DIR%"
if errorlevel 1 (
    echo Fallo dotnet publish.
    exit /b 1
)

if not exist "%PUBLISH_DIR%\MoodTracker.exe" (
    echo No se genero %PUBLISH_DIR%\MoodTracker.exe
    exit /b 1
)

echo [2/3] Verificando Inno Setup...
set "ISCC_CMD="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_CMD if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC_CMD (
    echo Inno Setup no encontrado. Se deja listo el .exe portable.
    echo Ejecutable: %PUBLISH_DIR%\MoodTracker.exe
    exit /b 0
)

echo [3/3] Generando instalador...
if exist "%INSTALLER%" del /q "%INSTALLER%"
if exist "%ICON_FILE%" (
    call "%ISCC_CMD%" /DMyAppName=%APP_NAME% /DMyAppVersion=%APP_VERSION% /DMyAppPublisher=%APP_PUBLISHER% /DMyAppSetupIconFile="%ICON_FILE%" "%~dp0installer_windows_native.iss"
) else (
    call "%ISCC_CMD%" /DMyAppName=%APP_NAME% /DMyAppVersion=%APP_VERSION% /DMyAppPublisher=%APP_PUBLISHER% "%~dp0installer_windows_native.iss"
)
if errorlevel 1 (
    echo Fallo la generacion del instalador.
    exit /b 1
)

echo Build completada
echo Ejecutable: %PUBLISH_DIR%\MoodTracker.exe
echo Instalador: %INSTALLER%
exit /b 0
