import os

def remove_string_from_file(string: str, filename: str):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, filename)

    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    with open(file_path, "w", encoding="utf-8") as file:
        found = False
        for line in lines:
            if line.strip() == string:
                found = True
                continue
            file.write(line)

        return found


async def save_string_to_file(link:str, filename: str) -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, filename)
    if not os.path.exists(file_path): open(file_path, "w", encoding="utf-8").close()
    with open(file_path, "r", encoding="utf-8") as file:
        if os.path.getsize(file_path) != 0:
            for line in file:
                if line.strip() == link: return
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(link+"\n")

async def get_strings_from_file(filename: str) -> list[str]:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, filename)
    if not os.path.exists(file_path): open(file_path, "w", encoding="utf-8").close()
    link_list = []
    with open(file_path, "r", encoding="utf-8") as file:
        if os.path.getsize(file_path) != 0:
            for line in file: link_list.append(line.strip())
            return link_list