import os
import sys
import ctypes
import shutil
import winreg
import wmi
import threading
import subprocess
import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk

# Функция для путей внутри EXE
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SystemExpertV2:
    def __init__(self, root):
        self.root = root
        self.root.title("System Expert Pro v2.0")
        self.root.geometry("700x550")
        self.setup_ui()
        self.update_dashboard()

    def setup_ui(self):
        # Фоновое изображение и Иконка
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
            img = Image.open(resource_path("bg.png")).resize((700, 550))
            self.bg_img = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=self.bg_img).place(relwidth=1, relheight=1)
        except: self.root.configure(bg="#1a1a1a")

        # Заголовок
        tk.Label(self.root, text="Windows Checker v2.0", font=("Arial", 22, "bold"), fg="#00FF00", bg="#1a1a1a").pack(pady=15)

        # Информационная панель (Dashboard)
        self.dash_frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief="groove")
        self.dash_frame.pack(pady=10, padx=20, fill="x")
        
        self.temp_label = tk.Label(self.dash_frame, text="Температура ЦП: --°C", fg="white", bg="#1a1a1a", font=("Consolas", 11))
        self.temp_label.pack(side="left", padx=20, pady=5)
        
        self.status_label = tk.Label(self.dash_frame, text="Статус: Готов", fg="#00FF00", bg="#1a1a1a", font=("Consolas", 11))
        self.status_label.pack(side="right", padx=20, pady=5)

        # Контейнер для кнопок
        btn_frame = tk.Frame(self.root, bg="#1a1a1a")
        btn_frame.pack(pady=20)

        btn_style = {"font": ("Arial", 10, "bold"), "width": 25, "pady": 8}

        # Кнопки старых функций
        tk.Button(btn_frame, text="🧹 Полная Очистка", command=self.run_cleaner, bg="#e67e22", fg="white", **btn_style).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(btn_frame, text="🔍 SMART Диагностика", command=self.run_smart, bg="#3498db", fg="white", **btn_style).grid(row=0, column=1, padx=10, pady=10)
        
        # Кнопки НОВЫХ функций
        tk.Button(btn_frame, text="📅 Анализ Планировщика", command=self.check_scheduler, bg="#9b59b6", fg="white", **btn_style).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(btn_frame, text="🛡️ Целостность Файлов", command=self.check_integrity, bg="#2ecc71", fg="white", **btn_style).grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(btn_frame, text="⚙️ Сканер Реестра", command=self.run_reg_check, bg="#7f8c8d", fg="white", **btn_style).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(btn_frame, text="❌ Выход", command=self.root.quit, bg="#c0392b", fg="white", **btn_style).grid(row=2, column=1, padx=10, pady=10)

    # --- ЛОГИКА ОБНОВЛЕНИЯ ---
    def update_dashboard(self):
        try:
            w = wmi.WMI(namespace="root\\wmi")
            temp_raw = w.MSAcpi_ThermalZoneTemperature()[0].CurrentTemperature
            temp = (temp_raw / 10.0) - 273.15
            self.temp_label.config(text=f"Температура ЦП: {temp:.1f}°C", fg="#FF4500" if temp > 70 else "white")
        except:
            self.temp_label.config(text="Температура ЦП: Н/Д")
        self.root.after(3000, self.update_dashboard)

    # --- ЛОГИКА ФУНКЦИЙ ---
    def run_cleaner(self):
        self.status_label.config(text="Статус: Очистка...", fg="yellow")
        paths = [os.environ.get('TEMP'), r'C:\Windows\Temp', r'C:\Windows\Prefetch']
        cleaned = 0
        for p in paths:
            if os.path.exists(p):
                for f in os.listdir(p):
                    try:
                        fp = os.path.join(p, f); cleaned += os.path.getsize(fp)
                        if os.path.isfile(fp): os.unlink(fp)
                        else: shutil.rmtree(fp)
                    except: continue
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1 | 2 | 4)
        messagebox.showinfo("Готово", f"Освобождено: {cleaned // (1024*1024)} МБ")
        self.status_label.config(text="Статус: Готов", fg="#00FF00")

    def run_smart(self):
        try:
            c = wmi.WMI()
            report = "\n".join([f"{d.Caption}: {d.Status}" for d in c.Win32_DiskDrive()])
            messagebox.showinfo("SMART Диагностика", report)
        except: messagebox.showerror("Ошибка", "Нет доступа к SMART")

    def check_scheduler(self):
        try:
            # Получаем список задач
            res = subprocess.check_output("schtasks /query /fo LIST /v", shell=True, stderr=subprocess.STDOUT)
            decoded = res.decode('cp866')
            
            log_win = tk.Toplevel(self.root)
            log_win.title("Задачи планировщика")
            txt = scrolledtext.ScrolledText(log_win, width=80, height=30, font=("Consolas", 9))
            txt.pack(expand=True, fill="both")
            txt.insert(tk.INSERT, decoded)
            txt.config(state="disabled")
        except Exception as e: messagebox.showerror("Ошибка", str(e))

    def check_integrity(self):
        messagebox.showinfo("Инфо", "Запуск проверки SFC (только чтение). Процесс идет в фоне.")
        subprocess.Popen("sfc /verifyonly", shell=True)

    def run_reg_check(self):
        try:
            path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
            count = winreg.QueryInfoKey(key)[1]
            messagebox.showinfo("Реестр", f"Программ в автозагрузке: {count}")
        except: messagebox.showerror("Ошибка", "Доступ запрещен")

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemExpertV2(root)
    root.mainloop()
