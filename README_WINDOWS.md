# MoodTracker para Windows

La app puede distribuirse en Windows como ejecutable o instalador de doble clic. El usuario final no necesita instalar Python, abrir PowerShell ni tocar la terminal.

## Que recibe el usuario final

- `MoodTracker-Setup.exe`: instalador recomendado y suficiente por si solo
- `dist\MoodTracker.exe`: ejecutable portable

Con cualquiera de los dos, el usuario comun solo hace doble clic.
Si queres entregar un unico archivo para Windows, usa `MoodTracker-Setup.exe`.

## Requisitos de la maquina de build

Estos requisitos son solo para quien arma la version de Windows:

- Windows 10 u 11
- Python 3 con `tkinter`
- Inno Setup 6 para generar `MoodTracker-Setup.exe`
- Opcional: `app.ico` en la raiz para usar un icono propio

PowerShell ya no es obligatorio para el flujo principal de build.

## Generar la version Windows

En Windows, dentro de esta carpeta:

```bat
build_windows.bat
```

Tambien se puede hacer con doble clic sobre `build_windows.bat`.

El script:

1. instala o actualiza `PyInstaller`
2. genera `dist\MoodTracker.exe`
3. genera `MoodTracker-Setup.exe` si encuentra Inno Setup

## GitHub Actions

El workflow `Build Windows` ahora genera la version original de `moodtracker.py` y publica dos artefactos:

- `MoodTracker-standalone-installer-exe`: el instalador final que alcanza por si solo
- `MoodTracker-portable-exe`: el ejecutable portable

Si solo queres bajar un archivo y usar el programa en Windows, descarga `MoodTracker-standalone-installer-exe`.

## Opciones de build

Solo ejecutable portable:

```bat
build_windows.bat -SkipInstaller
```

Limpiar artefactos previos antes de compilar:

```bat
build_windows.bat -Clean
```

Se pueden combinar:

```bat
build_windows.bat -Clean -SkipInstaller
```

## Ejecutar en desarrollo

```bat
py -3 moodtracker.py
```

## Instalacion para el usuario final

La recomendacion es entregar `MoodTracker-Setup.exe`.

Ese archivo:

- instala la app en Windows
- puede crear acceso directo en escritorio
- puede activar inicio automatico
- deja a MoodTracker listo para abrir con doble clic desde el menu Inicio

## Datos y autoarranque

- Los datos se guardan en `%APPDATA%\MoodTracker\data.json`
- El boton `Inicio auto` registra la app en `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Si la app esta empaquetada, el autoarranque usa el `.exe`
- Si la app corre como script, usa `pythonw.exe` cuando esta disponible
- El instalador tambien puede crear acceso directo de escritorio y activar inicio automatico durante la instalacion
- El `.exe` incluye metadata de version para que Windows muestre nombre y version con mejor aspecto
