import json
import asyncio
import subprocess
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
from telethon.sync import TelegramClient


def load_config(config_file):
    """Загрузка конфигурации из файла."""
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


async def execute_task(task, log_text):
    """Выполнение задачи автопостинга или рекламы."""
    task_type = task.get("type", "post")
    source = task["source_channel"]
    destination = task["destination_channel"]
    count = task.get("post_count", 1) if task_type == "post" else task.get("ad_count", 1)
    interval = task["interval_minutes"]

    log_text.insert(tk.END, f"\nЗапуск задачи: {task_type} из {source} в {destination}, "
                             f"{count} сообщений с интервалом {interval} минут.\n")

    for i in range(count):
        if task_type == "post":
            subprocess.run([
                "python", "copy_post.py",
                "--source", source,
                "--destination", destination,
                "--count", "1"
            ], check=True)
        elif task_type == "ad":
            subprocess.run([
                "python", "copy_ad.py",
                "--source", source,
                "--destination", destination,
                "--new_link", task["new_link"]
            ], check=True)

        log_text.insert(tk.END, "Запуск удаления дубликатов...\n")
        subprocess.run([
            "python", "delete_dub.py",
            "--channel", destination
        ], check=True)

        if i < count - 1:
            log_text.insert(tk.END, f"Задача: ждем {interval} минут перед следующим действием.\n")
            await asyncio.sleep(interval * 60)


async def schedule_tasks(config_file, log_text):
    """Запуск задач в определенное время."""
    config = load_config(config_file)
    tasks = config["tasks"]

    log_text.insert(tk.END, "Начало расписания задач...\n")
    while True:
        now = datetime.now()
        scheduled_tasks = []

        for task in tasks:
            task_time_str = task["start_time"]
            if task_time_str == "24:00":
                task_time_str = "00:00"

            scheduled_time = datetime.strptime(task_time_str, "%H:%M").time()
            scheduled_datetime = datetime.combine(now.date(), scheduled_time)

            if scheduled_datetime < now:
                scheduled_datetime += timedelta(days=1)

            scheduled_tasks.append((scheduled_datetime, task))

        scheduled_tasks.sort(key=lambda x: x[0])
        next_task_time, next_task = scheduled_tasks[0]
        wait_time = (next_task_time - now).total_seconds()

        log_text.insert(tk.END, f"Ближайшая задача '{next_task['type']}' запланирована на {next_task_time}. "
                                 f"Ожидание {wait_time // 60} минут.\n")

        await asyncio.sleep(wait_time)
        log_text.insert(tk.END, f"Выполнение задачи '{next_task['type']}'...\n")
        await execute_task(next_task, log_text)


def start_task_execution(config_file, log_text):
    """Функция-обертка для запуска asyncio с графическим интерфейсом."""
    asyncio.run(schedule_tasks(config_file, log_text))


def select_config_file(entry):
    """Открыть диалог выбора файла конфигурации."""
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)


def start_execution_gui(config_file_entry, log_text):
    """Запустить выполнение задач в отдельном потоке."""
    config_file = config_file_entry.get()
    if not config_file:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите файл конфигурации.")
        return

    threading.Thread(target=start_task_execution, args=(config_file, log_text), daemon=True).start()


def save_config(tasks, log_text):
    """Сохранить задачи в файл конфигурации."""
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return

    config = {"tasks": tasks}
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    log_text.insert(tk.END, f"Конфигурация сохранена в файл {file_path}\n")


def add_task(tasks, task_data, log_text):
    """Добавить задачу в список задач."""
    tasks.append(task_data)
    log_text.insert(tk.END, f"Задача добавлена: {task_data}\n")


def setup_telethon_session(phone, api_id, api_hash, code, log_text):
    """Настройка сессии Telethon."""
    try:
        client = TelegramClient("session", api_id, api_hash)
        client.start(phone=phone, code_callback=lambda: code)
        log_text.insert(tk.END, "Сессия Telethon успешно запущена.\n")
        return client
    except Exception as e:
        log_text.insert(tk.END, f"Ошибка настройки Telethon: {str(e)}\n")
        return None


def create_gui():
    """Создать графический интерфейс."""
    root = tk.Tk()
    root.title("Автопостинг и реклама")

    tasks = []

    tk.Label(root, text="Файл конфигурации:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    config_file_entry = tk.Entry(root, width=40)
    config_file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Button(root, text="Обзор", command=lambda: select_config_file(config_file_entry)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="Телефон:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    phone_entry = tk.Entry(root, width=20)
    phone_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(root, text="API ID:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    api_id_entry = tk.Entry(root, width=20)
    api_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    tk.Label(root, text="API Hash:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    api_hash_entry = tk.Entry(root, width=20)
    api_hash_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    tk.Label(root, text="Код подтверждения:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    code_entry = tk.Entry(root, width=20)
    code_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    log_text = scrolledtext.ScrolledText(root, width=60, height=20, state="normal")
    log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    tk.Button(root, text="Настроить Telethon", command=lambda: setup_telethon_session(
        phone_entry.get(), int(api_id_entry.get()), api_hash_entry.get(), code_entry.get(), log_text
    )).grid(row=6, column=0, columnspan=3, pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
