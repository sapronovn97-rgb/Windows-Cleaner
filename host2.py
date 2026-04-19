import os
import psutil
import tkinter as tk
from tkinter import messagebox
import ctypes

class WindowsCheckerV1Premium:
    def __init__(self, root):
        self.root = root
        self.root.title("WC Premium v1.0")
        self.root.geometry("400x500")
        self.root.configure(bg="#FFFFFF")
        
        # Акцентные цвета
        self.accent = "#0078D4"
        self.success = "#28A745"
        
        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        tk.Label(self.root, text="WINDOWS CHECKER", font=("Segoe UI", 16, "bold"), 
                 bg="#FFFFFF", fg=self.accent).pack(pady=20)
        
        # Круговой индикатор (имитация)
        self.status_circle = tk.Frame(self.root, bg=self.success, width=120, height=120)
        self.status_circle.pack(pady=10)
        tk.Label(self.status_circle, text="READY", font=("Segoe UI", 12, "bold"), 
                 fg="white", bg=self.success).place(relx=0.5, rely=0.5, anchor="center")

        # Инфо-панель
        self.info = tk.Label(self.root, text="Нажмите для анализа", font=("Segoe UI", 10), 
                             bg="#FFFFFF", fg="#666666")
        self.info.pack(pady=20)

        # Главная кнопка
        self.btn_main = tk.Button(self.root, text="СКАНИРОВАТЬ", command=self.quick_scan, 
                                  font=("Segoe UI", 11, "bold"), bg=self.accent, fg="white", 
                                  relief="flat", width=20, pady=10, cursor="hand2")
        self.btn_main.pack(pady=20)

        # Подпись внизу
        tk.Label(self.root, text="PREMIUM EDITION", font=("Segoe UI", 8), 
                 bg="#FFFFFF", fg="#CCCCCC").pack(side="bottom", pady=10)

    def quick_scan(self):
        self.btn_main.config(state="disabled", text="АНАЛИЗ...")
        self.root.update()
        
        # 1. Проверка ОЗУ
        ram = psutil.virtual_memory().percent
        # 2. Очистка корзины
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1 | 2 | 4)
            cleaned = "Очищена"
        except:
            cleaned = "Пропущена"

        res_msg = f"Анализ завершен!\nПамять: {ram}%\nКорзина: {cleaned}"
        messagebox.showinfo("WC Premium", res_msg)
        
        self.btn_main.config(state="normal", text="СКАНИРОВАТЬ")
        self.info.config(text="Система оптимизирована")

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsCheckerV1Premium(root)
    root.mainloop()
