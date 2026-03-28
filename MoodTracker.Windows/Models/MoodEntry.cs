namespace MoodTracker.Windows.Models;

public sealed class MoodEntry
{
    public required string Timestamp { get; init; }

    public required string Date { get; init; }

    public required int Value { get; init; }
}
