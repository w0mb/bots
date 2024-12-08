import json
import asyncio
import subprocess
from datetime import datetime, timedelta

def load_config(config_file):
    """Загрузка конфигурации из файла."""
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_last_execution_date(task_name, date):
    """Сохранение даты последнего выполнения задачи."""
    try:
        with open("last_execution.json", "r", encoding="utf-8") as f:
            last_executions = json.load(f)
    except FileNotFoundError:
        last_executions = {}

    last_executions[task_name] = date.strftime("%Y-%m-%d")
    
    with open("last_execution.json", "w", encoding="utf-8") as f:
        json.dump(last_executions, f, ensure_ascii=False, indent=4)

def get_last_execution_date(task_name):
    """Получение даты последнего выполнения задачи."""
    try:
        with open("last_execution.json", "r", encoding="utf-8") as f:
            last_executions = json.load(f)
    except FileNotFoundError:
        return None
    return last_executions.get(task_name)

async def execute_task(task):
    """Выполнение задачи автопостинга или рекламы."""
    task_type = task.get("type", "post")
    source = task["source_channel"]
    destination = task["destination_channel"]
    count = task.get("post_count", 1) if task_type in ["post", "full_post"] else task.get("ad_count", 1)
    interval = task["interval_minutes"]

    print(f"Запуск задачи: {task_type} из {source} в {destination}, {count} сообщений с интервалом {interval} минут.")
    if task_type == "remove_users":
        print("Запуск удаления пользователей с истёкшей подпиской...")
        subprocess.run([
            "python", "delet.py"
        ], check=True)
        print("Удаление пользователей завершено.")
        return

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
        elif task_type == "full_post":
            # Запуск скрипта для полного копирования постов
            subprocess.run([
                "python", "copy_full_post.py",
                "--source", source,
                "--destination", destination,
                "--count", "1"
            ], check=True)

        # Вызов delete_dub.py после каждого действия
        print("Запуск удаления дубликатов...")
        subprocess.run([
            "python", "delete_dub.py",
            "--channel", destination
        ], check=True)

        if i < count - 1:
            print(f"Задача: ждем {interval} минут перед следующим действием.")
            await asyncio.sleep(interval * 60)

async def schedule_tasks():
    """Запуск задач в определенное время."""
    config = load_config("config.json")
    tasks = config["tasks"]

    print("Начало расписания задач...")
    while True:
        now = datetime.now()
        scheduled_tasks = []

        for task in tasks:
            # Проверка и корректировка времени задачи
            task_time_str = task["start_time"]
            if task_time_str == "24:00":
                task_time_str = "00:00"

            scheduled_time = datetime.strptime(task_time_str, "%H:%M").time()
            scheduled_datetime = datetime.combine(now.date(), scheduled_time)

            # Если время задачи уже прошло, переносим на следующий день
            if scheduled_datetime < now:
                scheduled_datetime += timedelta(days=1)

            # Проверяем, была ли задача выполнена сегодня
            last_execution_date = get_last_execution_date(task["type"])
            if last_execution_date == now.date().strftime("%Y-%m-%d"):
                print(f"Задача '{task['type']}' уже выполнена сегодня. Пропускаем.")
                continue

            scheduled_tasks.append((scheduled_datetime, task))

        # Сортируем задачи по времени выполнения
        scheduled_tasks.sort(key=lambda x: x[0])

        # Выполняем ближайшую задачу
        if scheduled_tasks:
            next_task_time, next_task = scheduled_tasks[0]
            wait_time = (next_task_time - now).total_seconds()

            print(f"Ближайшая задача '{next_task['type']}' запланирована на {next_task_time}. Ожидание {wait_time // 60} минут.")

            # Ожидание времени выполнения задачи
            await asyncio.sleep(wait_time)
            print(f"Выполнение задачи '{next_task['type']}'...")

            await execute_task(next_task)

            # Сохраняем дату выполнения задачи
            save_last_execution_date(next_task["type"], now)

if __name__ == "__main__":
    asyncio.run(schedule_tasks())
