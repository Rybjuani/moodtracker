# MoodTracker

Version nueva de escritorio orientada a Windows, con ejecutable autocontenido e instalador.

## Estructura

- `MoodTracker.Windows/`: app nativa en `C# + WPF`
- `moodtracker.py`: version anterior en Python, mantenida como referencia

## Build de Windows

La forma recomendada es usar GitHub Actions. El workflow compila en Windows y publica estos artefactos:

- `MoodTracker-exe`: contiene `MoodTracker.exe`
- `MoodTracker-installer`: contiene el instalador `.exe`

Tambien se puede compilar localmente en una PC Windows con:

```bat
cd MoodTracker.Windows
build_windows_native.bat
```

## Usuario final

El usuario final de Windows no necesita instalar Python ni .NET.

Solo tiene que abrir:

- `MoodTracker-Windows-Setup-1.0.0.exe`
- o `MoodTracker.exe` si queres distribuirlo portable
