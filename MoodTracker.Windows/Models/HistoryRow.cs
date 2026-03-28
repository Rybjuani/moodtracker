namespace MoodTracker.Windows.Models;

public sealed class HistoryRow
{
    public required string Label { get; init; }

    public required double Value { get; init; }

    public string ValueText => Value >= 0 ? $"+{Value:0.0}" : $"{Value:0.0}";
}
