from aiogram.utils.formatting import Bold

link = "https://example.com"
link1 = "https://example.com"

text1 = (f"{Bold("️❗ВНИМАНИЕ❗").as_markdown()}\n"
         f"Чтобы заявка была обработана,\n"
         f"пожалуйста, {Bold("подтвердите что").as_markdown()}\n"
         f"{Bold("являетесь совершеннолетним🔞").as_markdown()}")

text_send1 = f"Переходите {link}"
text_send2 = f"Переходи, если не хочешь потеряться{link1}"