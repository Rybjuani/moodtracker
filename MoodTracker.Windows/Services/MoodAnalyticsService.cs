using System.Globalization;
using MoodTracker.Windows.Models;

namespace MoodTracker.Windows.Services;

public sealed class MoodAnalyticsService
{
    public double? GetTodayAverage(IEnumerable<MoodEntry> entries)
    {
        var today = StorageService.TodayIso();
        var values = entries.Where(entry => entry.Date == today).Select(entry => entry.Value).ToArray();
        if (values.Length == 0)
        {
            return null;
        }

        return Math.Round(values.Average(), 2);
    }

    public int GetTodayCount(IEnumerable<MoodEntry> entries)
    {
        var today = StorageService.TodayIso();
        return entries.Count(entry => entry.Date == today);
    }

    public IReadOnlyList<MoodEntry> GetLatestTodayEntries(IEnumerable<MoodEntry> entries, int take)
    {
        var today = StorageService.TodayIso();
        return entries
            .Where(entry => entry.Date == today)
            .OrderBy(entry => entry.Timestamp)
            .TakeLast(take)
            .ToList();
    }

    public IReadOnlyList<HistoryRow> BuildEntryRows(IEnumerable<MoodEntry> entries)
    {
        return entries
            .OrderByDescending(entry => entry.Timestamp)
            .Select(entry => new HistoryRow
            {
                Label = FormatTimestamp(entry.Timestamp),
                Value = entry.Value
            })
            .ToList();
    }

    public IReadOnlyList<HistoryRow> BuildDailyRows(IEnumerable<MoodEntry> entries)
    {
        return entries
            .GroupBy(entry => entry.Date)
            .Select(group => new HistoryRow
            {
                Label = group.Key,
                Value = Math.Round(group.Average(entry => entry.Value), 2)
            })
            .OrderByDescending(row => row.Label)
            .ToList();
    }

    public IReadOnlyList<HistoryRow> BuildWeeklyRows(IEnumerable<MoodEntry> entries)
    {
        return entries
            .GroupBy(entry =>
            {
                var date = DateOnly.ParseExact(entry.Date, "yyyy-MM-dd", CultureInfo.InvariantCulture);
                var week = ISOWeek.GetWeekOfYear(date.ToDateTime(TimeOnly.MinValue));
                var year = ISOWeek.GetYear(date.ToDateTime(TimeOnly.MinValue));
                return $"{year}-W{week:00}";
            })
            .Select(group => new HistoryRow
            {
                Label = group.Key,
                Value = Math.Round(group.Average(entry => entry.Value), 2)
            })
            .OrderByDescending(row => row.Label)
            .ToList();
    }

    public IReadOnlyList<HistoryRow> BuildMonthlyRows(IEnumerable<MoodEntry> entries)
    {
        return entries
            .GroupBy(entry => entry.Date[..7])
            .Select(group => new HistoryRow
            {
                Label = group.Key,
                Value = Math.Round(group.Average(entry => entry.Value), 2)
            })
            .OrderByDescending(row => row.Label)
            .ToList();
    }

    private static string FormatTimestamp(string value)
    {
        if (DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeLocal, out var timestamp))
        {
            return timestamp.ToString("dd/MM/yyyy HH:mm");
        }

        return value;
    }
}
