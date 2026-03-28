param(
    [switch]$Clean,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dist = Join-Path $Root "dist"
$Build = Join-Path $Root "build"
$Spec = Join-Path $Root "moodtracker.spec"
$InstallerName = "MoodTracker-Setup.exe"
$InstallerPath = Join-Path $Root $InstallerName
$VersionFile = Join-Path $Root "windows_version_info.txt"
$IconFile = Join-Path $Root "app.ico"

Write-Host ""
Write-Host "MoodTracker - Build para Windows" -ForegroundColor Cyan
Write-Host ""

if ($Clean) {
    if (Test-Path $Dist) { Remove-Item $Dist -Recurse -Force }
    if (Test-Path $Build) { Remove-Item $Build -Recurse -Force }
    if (Test-Path $Spec) { Remove-Item $Spec -Force }
}

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    $pyCmd = "py"
    $baseArgs = @("-3")
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "No se encontro Python 3. Instala Python 3 y volve a ejecutar este script."
    }
    $pyCmd = "python"
    $baseArgs = @()
}

Write-Host "[1/4] Verificando PyInstaller..."
& $pyCmd @baseArgs -m pip install pyinstaller

Write-Host "[2/4] Generando ejecutable..."
$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", "MoodTracker",
    "--version-file", $VersionFile,
    (Join-Path $Root "moodtracker.py")
)

if (Test-Path $IconFile) {
    $pyInstallerArgs += @("--icon", $IconFile)
    Write-Host "     Icono detectado: $IconFile"
} else {
    Write-Host "     Icono no encontrado. Se usara el icono por defecto."
}

& $pyCmd @baseArgs $pyInstallerArgs

$Exe = Join-Path $Dist "MoodTracker.exe"
if (-not (Test-Path $Exe)) {
    throw "No se genero $Exe"
}

if ($SkipInstaller) {
    Write-Host "[3/4] Instalador omitido por parametro"
    Write-Host "[4/4] Build completada"
    Write-Host "Ejecutable:" $Exe -ForegroundColor Green
    exit 0
}

Write-Host "[3/4] Generando instalador..."
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $iscc) {
    $defaultIscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (Test-Path $defaultIscc) {
        $isccPath = $defaultIscc
    } else {
        throw "No se encontro Inno Setup. Instala Inno Setup 6 y volve a ejecutar este script."
    }
} else {
    $isccPath = $iscc.Source
}

if (Test-Path $InstallerPath) {
    Remove-Item $InstallerPath -Force
}

& $isccPath `
    "/DMyAppVersion=3.0.0" `
    "/DMyAppPublisher=MoodTracker" `
    (Join-Path $Root "installer_windows.iss")

if (-not (Test-Path $InstallerPath)) {
    throw "No se genero $InstallerPath"
}

Write-Host "[4/4] Build completada"
Write-Host "Ejecutable:" $Exe -ForegroundColor Green
Write-Host "Instalador:" $InstallerPath -ForegroundColor Green
