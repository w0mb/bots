import os
from pathlib import Path

async def remove_string_from_file(string: str, filename: str):
    # Получаем путь к текущей директории, где лежит этот скрипт
    current_dir = Path(__file__).parent
    # Путь к файлу на один уровень выше
    file_path = current_dir.parent / filename

    if not file_path.exists():
        return

    # Чтение файла
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Запись файла (без удаляемой строки)
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip() == string:
                continue
            file.write(line)


async def save_string_to_file(link: str, filename: str) -> str:
    # Получаем путь к текущей директории, где лежит этот скрипт
    current_dir = Path(__file__).parent
    # Путь к файлу на один уровень выше
    file_path = current_dir.parent / filename

    # Создаем файл, если он не существует
    if not file_path.exists():
        file_path.touch()

    # Проверяем, есть ли уже такая строка в файле
    with open(file_path, "r", encoding="utf-8") as file:
        if file_path.stat().st_size != 0:  # Проверяем, что файл не пустой
            for line in file:
                if line.strip() == link:
                    return  # Строка уже есть, ничего не делаем

    # Добавляем строку в файл
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(link + "\n")


async def get_strings_from_file(filename: str) -> list[str]:
    # Получаем путь к текущей директории, где лежит этот скрипт
    current_dir = Path(__file__).parent
    # Путь к файлу на один уровень выше
    file_path = current_dir.parent / filename

    # Создаем файл, если он не существует
    if not file_path.exists():
        file_path.touch()

    # Чтение файла и возврат списка строк
    link_list = []
    with open(file_path, "r", encoding="utf-8") as file:
        if file_path.stat().st_size != 0:  # Проверяем, что файл не пустой
            for line in file:
                link_list.append(line.strip())
    return link_list