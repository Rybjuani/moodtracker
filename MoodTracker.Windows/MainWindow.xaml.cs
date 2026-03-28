using System.Collections.ObjectModel;
using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using MoodTracker.Windows.Models;
using MoodTracker.Windows.Services;

namespace MoodTracker.Windows;

public partial class MainWindow : Window
{
    private static readonly string[] Descriptions =
    [
        "Malestar extremo",
        "Malestar severo",
        "Muy mal",
        "Bastante mal",
        "Mal",
        "Algo mal",
        "Bajo",
        "Un poco bajo",
        "Levemente bajo",
        "Casi neutral",
        "Neutral",
        "Levemente bien",
        "Algo bien",
        "Un poco bien",
        "Bien",
        "Bastante bien",
        "Muy bien",
        "Genial",
        "Excelente",
        "Extraordinario",
        "Bienestar total"
    ];

    private readonly StorageService _storage = new();
    private readonly MoodAnalyticsService _analytics = new();
    private readonly AutostartService _autostart = new();
    private readonly AppData _data;
    private bool _autostartReady;

    public MainWindow()
    {
        InitializeComponent();
        _data = _storage.Load();
        DateTextBlock.Text = DateTime.Now.ToString("dddd dd MMMM yyyy", new CultureInfo("es-AR"));
        MoodSlider.Value = 0;
        UpdatePreview(0);
        RefreshUi();
        AutostartCheckBox.IsChecked = SafeReadAutostart();
        _autostartReady = true;
    }

    private void MoodSlider_OnValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
    {
        UpdatePreview((int)e.NewValue);
    }

    private void SaveEntry_Click(object sender, RoutedEventArgs e)
    {
        var value = (int)MoodSlider.Value;
        var now = DateTime.Now;
        _data.Entries.Add(new MoodEntry
        {
            Timestamp = now.ToString("s", CultureInfo.InvariantCulture),
            Date = DateOnly.FromDateTime(now).ToString("yyyy-MM-dd", CultureInfo.InvariantCulture),
            Value = value
        });

        _storage.Save(_data);
        RefreshUi();
        MessageBox.Show("Registro guardado.", "MoodTracker", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void AutostartCheckBox_OnChanged(object sender, RoutedEventArgs e)
    {
        if (!_autostartReady)
        {
            return;
        }

        try
        {
            if (AutostartCheckBox.IsChecked == true)
            {
                _autostart.Enable();
            }
            else
            {
                _autostart.Disable();
            }
        }
        catch (Exception ex)
        {
            _autostartReady = false;
            AutostartCheckBox.IsChecked = SafeReadAutostart();
            _autostartReady = true;
            MessageBox.Show($"No se pudo actualizar el inicio automático.\n\n{ex.Message}", "MoodTracker", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private void RefreshUi()
    {
        var average = _analytics.GetTodayAverage(_data.Entries);
        var count = _analytics.GetTodayCount(_data.Entries);

        AverageTextBlock.Text = average is null ? "Promedio hoy: -" : $"Promedio hoy: {FormatSigned(average.Value)}";
        CountTextBlock.Text = count == 0 ? "Sin registros hoy" : $"{count} registro{(count == 1 ? string.Empty : "s")} hoy";

        LatestEntriesListBox.ItemsSource = _analytics
            .GetLatestTodayEntries(_data.Entries, 5)
            .Select(entry => $"{FormatTime(entry.Timestamp)}  |  {FormatSigned(entry.Value)}")
            .ToList();

        EntriesDataGrid.ItemsSource = new ObservableCollection<HistoryRow>(_analytics.BuildEntryRows(_data.Entries));
        DailyDataGrid.ItemsSource = new ObservableCollection<HistoryRow>(_analytics.BuildDailyRows(_data.Entries));
        WeeklyDataGrid.ItemsSource = new ObservableCollection<HistoryRow>(_analytics.BuildWeeklyRows(_data.Entries));
        MonthlyDataGrid.ItemsSource = new ObservableCollection<HistoryRow>(_analytics.BuildMonthlyRows(_data.Entries));
    }

    private void UpdatePreview(int value)
    {
        ValueTextBlock.Text = value == 0 ? "0" : value > 0 ? $"+{value}" : value.ToString(CultureInfo.InvariantCulture);
        EmojiTextBlock.Text = MoodEmoji(value);
        DescriptionTextBlock.Text = Descriptions[value + 10];
        var brush = (System.Windows.Media.Brush)new System.Windows.Media.BrushConverter().ConvertFromString(MoodColor(value))!;
        ValueTextBlock.Foreground = brush;
        DescriptionTextBlock.Foreground = brush;
    }

    private bool SafeReadAutostart()
    {
        try
        {
            return _autostart.IsEnabled();
        }
        catch
        {
            return false;
        }
    }

    private static string MoodColor(double value)
    {
        if (value <= -8)
        {
            return "#BE1414";
        }

        if (value <= -4)
        {
            return "#D25A14";
        }

        if (value <= -1)
        {
            return "#8C6E32";
        }

        if (value == 0)
        {
            return "#8A8AA0";
        }

        if (value <= 4)
        {
            return "#2F8E4F";
        }

        return "#1EB84B";
    }

    private static string MoodEmoji(int value)
    {
        if (value <= -9) return "😭";
        if (value <= -7) return "😢";
        if (value <= -5) return "😔";
        if (value <= -3) return "😕";
        if (value <= -1) return "😶";
        if (value == 0) return "😐";
        if (value <= 2) return "🙂";
        if (value <= 4) return "😌";
        if (value <= 6) return "😊";
        if (value <= 8) return "😁";
        return "🌟";
    }

    private static string FormatSigned(double value) =>
        value > 0 ? $"+{value:0.0}" : value.ToString("0.0", CultureInfo.InvariantCulture);

    private static string FormatTime(string timestamp)
    {
        if (DateTime.TryParse(timestamp, CultureInfo.InvariantCulture, DateTimeStyles.AssumeLocal, out var parsed))
        {
            return parsed.ToString("HH:mm");
        }

        return timestamp;
    }
}
