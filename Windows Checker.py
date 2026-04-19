
import os
import sys
import ctypes
import shutil
import winreg
import wmi
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Функция для корректных путей внутри EXE
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SystemExpertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("All-in-One System Expert v1.0")
        self.root.geometry("600x450")
        self.setup_ui()

    def setup_ui(self):
        # Фон и Иконка
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
            img = Image.open(resource_path("bg.png")).resize((600, 450))
            self.bg_img = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=self.bg_img).place(relwidth=1, relheight=1)
        except: self.root.configure(bg="#2c3e50")

        # Заголовок
        tk.Label(self.root, text="Windows Checker", font=("Arial", 24, "bold"), fg="white", bg="#1a1a1a").pack(pady=20)

        # Контейнер для кнопок
        frame = tk.Frame(self.root, bg="#1a1a1a")
        frame.pack(pady=10)

        btn_style = {"font": ("Arial", 10, "bold"), "width": 25, "pady": 10}

        tk.Button(frame, text="🔍 SMART Диагностика", command=self.run_smart, bg="#3498db", fg="white", **btn_style).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(frame, text="🧹 Полная Очистка", command=self.run_cleaner, bg="#e67e22", fg="white", **btn_style).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(frame, text="📂 Проверка Системных Файлов", command=self.run_sys_check, bg="#2ecc71", fg="white", **btn_style).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(frame, text="⚙️ Сканер Реестра", command=self.run_reg_check, bg="#9b59b6", fg="white", **btn_style).grid(row=1, column=1, padx=10, pady=10)

        self.status = tk.Label(self.root, text="Система готова к работе", fg="white", bg="#1a1a1a", font=("Arial", 10))
        self.status.pack(side="bottom", pady=20)

    # --- ЛОГИКА ---
    def run_smart(self):
        try:
            c = wmi.WMI()
            report = "\n".join([f"{d.Caption}: {d.Status}" for d in c.Win32_DiskDrive()])
            messagebox.showinfo("SMART Status", report)
        except: messagebox.showerror("Ошибка", "Не удалось получить данные SMART")

    def run_cleaner(self):
        self.status.config(text="Идет очистка...")
        paths = [os.environ.get('TEMP'), r'C:\Windows\Temp']
        cleaned = 0
        for p in paths:
            if os.path.exists(p):
                for f in os.listdir(p):
                    try:
                        fp = os.path.join(p, f)
                        cleaned += os.path.getsize(fp)
                        if os.path.isfile(fp): os.unlink(fp)
                        else: shutil.rmtree(fp)
                    except: continue
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1 | 2 | 4)
        messagebox.showinfo("Очистка", f"Освобождено: {cleaned // (1024*1024)} МБ")
        self.status.config(text="Очистка завершена")

    def run_sys_check(self):
        critical = [r"C:\Windows\System32\ntoskrnl.exe", r"C:\Windows\System32\drivers\etc\hosts"]
        report = "\n".join([f"{f}: {'OK' if os.path.exists(f) else 'ОТСУТСТВУЕТ'}" for f in critical])
        messagebox.showinfo("Системные файлы", report)

    def run_reg_check(self):
        try:
            path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                count = winreg.QueryInfoKey(key)[1]
            messagebox.showinfo("Реестр", f"В автозагрузке найдено программ: {count}")
        except: messagebox.showerror("Ошибка", "Доступ к реестру ограничен")

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemExpertApp(root)
    root.mainloop()
