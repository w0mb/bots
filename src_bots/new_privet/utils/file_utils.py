import os

import os

def remove_string_from_file(string: str, filename: str):
    if not os.path.exists(filename):
        return False

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    with open(filename, "w", encoding="utf-8") as file:
        found = False
        for line in lines:
            if line.strip() == string:
                found = True
                continue
            file.write(line)

        return found


async def save_string_to_file(link:str, filename: str) -> str:
    if not os.path.exists(filename): open(filename, "w", encoding="utf-8").close()
    with open(filename, "r", encoding="utf-8") as file:
        if os.path.getsize(filename) != 0:
            for line in file:
                if line.strip() == link: return
    with open(filename, "a", encoding="utf-8") as file:
        file.write(link+"\n")

async def get_strings_from_file(filename: str) -> list[str]:
    if not os.path.exists(filename): open(filename, "w", encoding="utf-8").close()
    link_list = []
    with open(filename, "r", encoding="utf-8") as file:
        if os.path.getsize(filename) != 0:
            for line in file: link_list.append(line.strip())
            return link_list