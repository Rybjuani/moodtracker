# MoodTracker Windows Native

Esta carpeta contiene una version nueva de MoodTracker orientada solo a Windows, hecha en `C# + WPF`.

## Objetivo

- generar `MoodTracker.exe` autocontenido
- permitir instalacion con doble clic
- no depender de Python en la PC del usuario final

## Que hace esta version

- registra estado de animo de `-10` a `+10`
- guarda datos en `%APPDATA%\MoodTracker\data.json`
- muestra historial de registros, promedio diario, semanal y mensual
- puede activar inicio automatico con Windows

## Compilar en Windows

Requisitos de la maquina de build:

- Windows 10 u 11
- .NET 8 SDK
- opcional: Inno Setup 6 para crear el instalador
- opcional: `app.ico` en esta carpeta para usar icono propio en el `.exe` y el instalador

Con doble clic o desde `cmd.exe`:

```bat
build_windows_native.bat
```

Eso genera:

- `publish\MoodTracker.exe`
- `MoodTracker-Windows-Setup-1.0.0.exe` si Inno Setup esta instalado

## Publicacion autocontenida

El script usa:

```bat
dotnet publish MoodTracker.Windows.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

Eso empaqueta el runtime dentro del `.exe`, por lo que el usuario final no necesita instalar .NET.

## Detalles de distribucion

- el `.exe` sale autocontenido y de archivo unico
- el instalador incluye solo `MoodTracker.exe`, sin carpeta de archivos sueltos
- el instalador puede crear acceso directo en escritorio
- el instalador puede activar autoarranque con Windows
- si agregas `app.ico`, se usa tanto en la app como en el instalador
