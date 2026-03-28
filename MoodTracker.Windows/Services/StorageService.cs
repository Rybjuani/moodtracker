using System.Globalization;
using System.IO;
using System.Text.Json;
using MoodTracker.Windows.Models;

namespace MoodTracker.Windows.Services;

public sealed class StorageService
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true
    };

    public string DataDirectory { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
        "MoodTracker");

    public string DataFilePath => Path.Combine(DataDirectory, "data.json");

    public AppData Load()
    {
        Directory.CreateDirectory(DataDirectory);
        if (!File.Exists(DataFilePath))
        {
            return new AppData();
        }

        try
        {
            var json = File.ReadAllText(DataFilePath);
            return JsonSerializer.Deserialize<AppData>(json, JsonOptions) ?? new AppData();
        }
        catch
        {
            var brokenPath = $"{DataFilePath}.broken-{DateTime.Now:yyyyMMddHHmmss}";
            try
            {
                File.Move(DataFilePath, brokenPath, overwrite: true);
            }
            catch
            {
            }

            return new AppData();
        }
    }

    public void Save(AppData data)
    {
        Directory.CreateDirectory(DataDirectory);
        var json = JsonSerializer.Serialize(data, JsonOptions);
        File.WriteAllText(DataFilePath, json);
    }

    public static string TodayIso() =>
        DateOnly.FromDateTime(DateTime.Now).ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
}
