# MoodTracker

MoodTracker mantiene dos caminos de escritorio para Windows sin perder la interfaz original de la app:

- `moodtracker.py`: version original en `Python + Tkinter`, con la UI compacta actual.
- `MoodTracker.Windows/`: alternativa nativa en `C# + WPF`.

## Contexto del repo

- La experiencia original y mas fiel al programa actual es `moodtracker.py`.
- El build de Windows para conservar esa interfaz se hace con `PyInstaller`.
- El repo tambien incluye una implementacion nativa para Windows y workflow de GitHub Actions.

## Ejecutar la app original

En Linux:

```bash
python3 moodtracker.py
```

O instalarla:

```bash
./install.sh
```

En Windows, para desarrollo:

```bat
py -3 moodtracker.py
```

## Generar `MoodTracker.exe` con la interfaz original

En una maquina Windows:

```bat
build_windows.bat
```

Ese flujo genera:

- `dist\MoodTracker.exe`
- `MoodTracker-Setup.exe` si Inno Setup esta instalado

Para mas detalle del empaquetado original en Windows, ver `README_WINDOWS.md`.

## Build nativo alternativo

La variante `WPF` se compila desde:

```bat
cd MoodTracker.Windows
build_windows_native.bat
```

## Datos y autoinicio

- En Windows los datos se guardan en `%APPDATA%\MoodTracker\data.json`.
- El boton `Inicio auto` funciona tanto ejecutando el script como ejecutando el `.exe`.
