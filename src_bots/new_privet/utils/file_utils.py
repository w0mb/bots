import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def remove_string_from_file(filename: str, string: str | None):
    file_path = Path(filename)
    if not file_path.exists():
        logging.warning(f"Файл {filename} не существует, невозможно удалить данные remove_string_from_file")
        return

    if string is None:
        file_path.unlink(missing_ok=True)
        return

    with file_path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    with file_path.open( "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip() == string:
                continue
            file.write(line)


async def save_string_to_file(link: str, filename: str) -> str:
    file_path = Path(filename)
    if not file_path.exists():
        logging.warning(f"Файл {filename} не существует, создаю его.... - save_string_to_file")
        file_path.touch()
    if file_path.stat().st_size > 0:
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip() == link:
                    return
    with file_path.open("a", encoding="utf-8") as file:
        file.write(link + "\n")


async def get_strings_from_file(filename: str) -> list[str]:
    file_path = Path(filename)
    if not file_path.exists():
        file_path.touch()

    link_list = []

    if file_path.stat().st_size == 0:
        logging.warning(f"Файл {filename} пуст. Невозможно получить данные. - get_strings_from_file")
        return link_list

    with file_path.open("r", encoding="utf-8") as file:
        link_list = [line.strip() for line in file]

    return link_list