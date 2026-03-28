using Microsoft.Win32;

namespace MoodTracker.Windows.Services;

public sealed class AutostartService
{
    private const string RegistryPath = @"Software\Microsoft\Windows\CurrentVersion\Run";
    private const string ValueName = "MoodTracker";

    public bool IsEnabled()
    {
        using var key = Registry.CurrentUser.OpenSubKey(RegistryPath, writable: false);
        var value = key?.GetValue(ValueName) as string;
        return !string.IsNullOrWhiteSpace(value);
    }

    public void Enable()
    {
        var exePath = Environment.ProcessPath
            ?? throw new InvalidOperationException("No se pudo determinar la ruta del ejecutable.");

        using var key = Registry.CurrentUser.OpenSubKey(RegistryPath, writable: true)
            ?? Registry.CurrentUser.CreateSubKey(RegistryPath, writable: true)
            ?? throw new InvalidOperationException("No se pudo abrir el registro de Windows.");

        key.SetValue(ValueName, $"\"{exePath}\"");
    }

    public void Disable()
    {
        using var key = Registry.CurrentUser.OpenSubKey(RegistryPath, writable: true);
        key?.DeleteValue(ValueName, throwOnMissingValue: false);
    }
}
