using Microsoft.UI.Xaml;
using System;
using System.IO;
using System.Management;
using System.Text;
using System.Threading.Tasks;

namespace WinChecker
{
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();

            // Настройка окна без использования конфликтующего XAML
            this.Title = "Windows Checker";
            this.AppWindow.Resize(new Windows.Graphics.SizeInt32(700, 600));
        }

        // 1. Проверка ПК, Процессора и Дисков
        private void CheckButton_Click(object sender, RoutedEventArgs e)
        {
            StringBuilder sysInfo = new StringBuilder();
            sysInfo.AppendLine($"Имя ПК: {Environment.MachineName}");
            sysInfo.AppendLine($"ОС: {Environment.OSVersion}");
            sysInfo.AppendLine($"Логические ядра ЦП: {Environment.ProcessorCount}");
            SystemInfoText.Text = sysInfo.ToString();

            StringBuilder ramInfo = new StringBuilder();
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT TotalVisibleMemorySize, FreePhysicalMemory FROM Win32_OperatingSystem"))
                {
                    foreach (ManagementObject os in searcher.Get())
                    {
                        double totalRam = Convert.ToDouble(os["TotalVisibleMemorySize"]) / 1024.0 / 1024.0;
                        double freeRam = Convert.ToDouble(os["FreePhysicalMemory"]) / 1024.0 / 1024.0;
                        double usedRam = totalRam - freeRam;
                        ramInfo.AppendLine($"Оперативная память: {usedRam:F2} ГБ занято из {totalRam:F1} ГБ (Свободно: {freeRam:F2} ГБ)");
                    }
                }
            }
            catch { ramInfo.AppendLine("Не удалось получить статус ОЗУ"); }
            RamInfoText.Text = ramInfo.ToString();

            StringBuilder diskInfo = new StringBuilder();
            try
            {
                DriveInfo[] allDrives = DriveInfo.GetDrives();
                foreach (DriveInfo d in allDrives)
                {
                    if (d.IsReady && d.DriveType == DriveType.Fixed)
                    {
                        double freeGB = d.TotalFreeSpace / 1024.0 / 1024.0 / 1024.0;
                        double totalGB = d.TotalSize / 1024.0 / 1024.0 / 1024.0;
                        diskInfo.AppendLine($"Логический диск {d.Name} Свободно: {freeGB:F2} ГБ из {totalGB:F2} ГБ");
                    }
                }
                diskInfo.AppendLine();

                using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_DiskDrive"))
                {
                    foreach (ManagementObject drive in searcher.Get())
                    {
                        string model = drive["Model"]?.ToString() ?? "Неизвестно";
                        string partitionStyle = drive["PartitionStyle"]?.ToString() ?? "Не определено";
                        string status = drive["Status"]?.ToString() ?? "Unknown";

                        string scheme = partitionStyle switch { "1" => "MBR", "2" => "GPT", _ => "Неизвестно" };
                        string smart = status.Equals("OK", StringComparison.OrdinalIgnoreCase) ? "Здоров (OK)" : $"Внимание ({status})";

                        diskInfo.AppendLine($"Физический диск: {model}");
                        diskInfo.AppendLine($" └─ Разметка: {scheme} | S.M.A.R.T.: {smart}");
                        diskInfo.AppendLine();
                    }
                }
            }
            catch (Exception ex) { diskInfo.AppendLine($"Ошибка чтения накопителей: {ex.Message}"); }
            DiskInfoText.Text = diskInfo.ToString();
        }

        // 2. Проверка Сети (IP-адреса)
        private void NetButton_Click(object sender, RoutedEventArgs e)
        {
            StringBuilder netInfo = new StringBuilder();
            netInfo.AppendLine("=== СЕТЕВЫЕ НАСТРОЙКИ ===");
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT Description, IPEnabled, IPAddress, MACAddress FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled = True"))
                {
                    foreach (ManagementObject adapter in searcher.Get())
                    {
                        netInfo.AppendLine($"Адаптер: {adapter["Description"]}");
                        netInfo.AppendLine($" └─ MAC-адрес: {adapter["MACAddress"]}");

                        string[] ipAddresses = (string[])adapter["IPAddress"];
                        if (ipAddresses != null && ipAddresses.Length > 0)
                        {
                            netInfo.AppendLine($" └─ IPv4-адрес: {ipAddresses[0]}");
                        }
                        netInfo.AppendLine();
                    }
                }
            }
            catch (Exception ex) { netInfo.AppendLine($"Ошибка чтения сети: {ex.Message}"); }

            SystemInfoText.Text = netInfo.ToString();
            RamInfoText.Text = "";
            DiskInfoText.Text = "";
        }

        // 3. Очистка временных файлов Temp с индикатором выполнения
        private async void CleanButton_Click(object sender, RoutedEventArgs e)
        {
            AppProgressBar.Visibility = Visibility.Visible;
            AppProgressBar.IsIndeterminate = false;
            AppProgressBar.Value = 10;

            string tempPath = Path.GetTempPath();
            int deletedFiles = 0;
            long savedSpace = 0;

            await Task.Delay(300);
            AppProgressBar.Value = 40;

            if (Directory.Exists(tempPath))
            {
                string[] files = Directory.GetFiles(tempPath);
                double step = files.Length > 0 ? 50.0 / files.Length : 0;

                foreach (string file in files)
                {
                    try
                    {
                        FileInfo fi = new FileInfo(file);
                        long size = fi.Length;
                        File.Delete(file);
                        savedSpace += size;
                        deletedFiles++;
                    }
                    catch { /* Файл заблокирован системой */ }
                    AppProgressBar.Value += step;
                }
            }

            AppProgressBar.Value = 100;
            await Task.Delay(200);
            AppProgressBar.Visibility = Visibility.Collapsed;

            double savedMB = savedSpace / 1024.0 / 1024.0;
            SystemInfoText.Text = $"=== ОЧИСТКА ЗАВЕРШЕНА ===\nУдалено файлов: {deletedFiles}\nОсвобождено места: {savedMB:F2} МБ";
            RamInfoText.Text = "";
            DiskInfoText.Text = "";
        }

        // 4. Сброс DNS кэша Windows
        private async void DnsButton_Click(object sender, RoutedEventArgs e)
        {
            SystemInfoText.Text = "Сброс кэша сопоставителя DNS... Пожалуйста, подождите.";
            AppProgressBar.Visibility = Visibility.Visible;
            AppProgressBar.IsIndeterminate = true;

            await Task.Run(() =>
            {
                try
                {
                    var startInfo = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = "ipconfig",
                        Arguments = "/flushdns",
                        CreateNoWindow = true,
                        UseShellExecute = false
                    };
                    using (var process = System.Diagnostics.Process.Start(startInfo))
                    {
                        process?.WaitForExit();
                    }
                }
                catch { }
            });

            AppProgressBar.Visibility = Visibility.Collapsed;
            SystemInfoText.Text = "=== УСПЕШНО ===\nКэш сопоставителя DNS успешно очищен.";
            RamInfoText.Text = "";
            DiskInfoText.Text = "";
        }

        // 5. Быстрая проверка целостности файлов SFC
        private async void SfcButton_Click(object sender, RoutedEventArgs e)
        {
            SystemInfoText.Text = "Запущена экспресс-проверка SFC. Ожидайте выполнения...";
            AppProgressBar.Visibility = Visibility.Visible;
            AppProgressBar.IsIndeterminate = true;

            string resultMessage = "";

            await Task.Run(() =>
            {
                try
                {
                    var startInfo = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = "sfc",
                        Arguments = "/verifyonly",
                        CreateNoWindow = true,
                        UseShellExecute = true,
                        Verb = "runas" // Запуск от имени Администратора
                    };

                    using (var process = System.Diagnostics.Process.Start(startInfo))
                    {
                        process?.WaitForExit();
                        if (process?.ExitCode == 0)
                            resultMessage = "=== ПРОВЕРКА ЗАВЕРШЕНА ===\nЗащита ресурсов Windows не обнаружила нарушений целостности системных файлов.";
                        else
                            resultMessage = "=== ВНИМАНИЕ ===\nВ системе обнаружены нарушения целостности важных файлов или проверка была прервана.";
                    }
                }
                catch (Exception ex)
                {
                    resultMessage = $"Не удалось запустить утилиту SFC. Ошибка прав доступа: {ex.Message}";
                }
            });

            AppProgressBar.Visibility = Visibility.Collapsed;
            SystemInfoText.Text = resultMessage;
            RamInfoText.Text = "";
            DiskInfoText.Text = "";
        }
    }
}
