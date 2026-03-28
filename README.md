# MoodTracker v3

MoodTracker es una app de escritorio en Python + Tkinter para registrar el estado de animo con la misma interfaz compacta en Linux y Windows.

## Estructura

- `moodtracker.py`: aplicacion principal.
- `install.sh`: instalador para Ubuntu/Debian.
- `moodtracker.spec`: configuracion de PyInstaller para Windows.
- `build_windows.bat`: build reproducible para generar `MoodTracker.exe` en Windows.

## Ejecutar en Linux

```bash
python3 moodtracker.py
```

O instalar:

```bash
./install.sh
```

## Generar `MoodTracker.exe` en Windows

Abrir `cmd` o PowerShell en la carpeta del proyecto y ejecutar:

```bat
build_windows.bat
```

Eso instala `PyInstaller` y `matplotlib`, limpia artefactos previos y genera:

```text
dist\MoodTracker.exe
```

## Notas de empaquetado

- La interfaz original no cambia: el build usa la misma app `Tkinter`.
- El autoinicio en Windows funciona tanto ejecutando `moodtracker.py` como ejecutando el `.exe`.
- Los datos en Windows se guardan en `%APPDATA%\MoodTracker\data.json`.
