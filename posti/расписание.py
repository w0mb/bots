import json
import asyncio
import subprocess
from datetime import datetime, timedelta
import os

base_path = os.path.dirname(os.path.abspath(__file__))  # Получаем директорию текущего файла
copy_full_post_path = os.path.join(base_path, "copy_full_post.py")
delet_path = os.path.join(base_path, "scripts/delet.py")
delete_dub_path = os.path.join(base_path, "scripts/delete_dub.py")
copy_ad_path = os.path.join(base_path, "scripts/copy_ad.py")
copy_post_path = os.path.join(base_path, "scripts/copy_post.py")
delete_user_path = os.path.join(base_path, "scripts/delet.py")

def load_config(config_file):
    """Загрузка конфигурации из файла."""
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def run_script(script_path, *args):
    """Универсальная функция для выполнения Python скрипта с аргументами."""
    subprocess.run([ "python", script_path] + list(args), check=True)

async def execute_task(task):
    """Выполнение задачи автопостинга или рекламы."""
    task_type = task.get("type", "post")
    source = task["source_channel"]
    destination = task["destination_channel"]
    count = task.get("post_count", 1) if task_type in ["post", "full_post"] else task.get("ad_count", 1)
    interval = task["interval_minutes"]
    check_dub = task.get("check_dub", True)  # По умолчанию проверка дубликатов включена

    print(f"Запуск задачи: {task_type} из {source} в {destination}, {count} сообщений с интервалом {interval} минут.")
    
    if task_type == "remove_users":
        print("Запуск удаления пользователей с истёкшей подпиской...")
        run_script(delete_user_path)
        print("Удаление пользователей завершено.")
        return

    for i in range(count):
        if task_type == "post":
            run_script(copy_post_path, "--source", source, "--destination", destination, "--count", "1")
        elif task_type == "ad":
            run_script(copy_ad_path, "--source", source, "--destination", destination, "--new_link", task["new_link"])
        elif task_type == "full_post":
            run_script(copy_full_post_path, "--source", source, "--destination", destination, "--count", "1")

        # Проверяем, требуется ли проверка дубликатов
        if check_dub:
            print("Запуск удаления дубликатов...")
            run_script(delete_dub_path, "--channel", destination)

        if i < count - 1:
            print(f"Задача: ждем {interval} минут перед следующим действием.")
            await asyncio.sleep(interval * 60)


async def schedule_tasks():
    """Запуск задач в определенное время."""
    config = load_config("scripts/config.json")
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

            scheduled_tasks.append((scheduled_datetime, task))

        # Сортируем задачи по времени выполнения
        scheduled_tasks.sort(key=lambda x: x[0])

        # Выполняем ближайшую задачу
        next_task_time, next_task = scheduled_tasks[0]
        wait_time = (next_task_time - now).total_seconds()

        print(f"Ближайшая задача '{next_task['type']}' запланирована на {next_task_time}. Ожидание {wait_time // 60} минут.")

        # Ожидание времени выполнения задачи
        await asyncio.sleep(wait_time)
        print(f"Выполнение задачи '{next_task['type']}'...")
        await execute_task(next_task)


if __name__ == "__main__":
    asyncio.run(schedule_tasks())
