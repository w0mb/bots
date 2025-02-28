from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)
from aiogram import Bot


# text1 = """bold(❗️ВНИМАНИЕ❗)️
#
# Чтобы заявка была обработана,
# пожалуйста, **подтвердите что
# являетесь совершеннолетним**🔞"""

link = "https://example.com"
link1 = "https://example.com"

text1 = (f"{Bold("️❗ВНИМАНИЕ❗").as_markdown()}\n"
         f"Чтобы заявка была обработана,\n"
         f"пожалуйста, {Bold("подтвердите что").as_markdown()}\n"
         f"{Bold("являетесь совершеннолетним🔞").as_markdown()}")

text_send1 = f"Переходите {link}"
text_send2 = f"Переходи, если не хочешь потеряться{link1}"