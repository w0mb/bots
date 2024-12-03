import telebot  # импортируем модуль telebot

bot = telebot.TeleBot('8115251126:AAFro_e4toFC8XzGGr8nOXALAwvWEysqY1o') 

@bot.message_handler(commands=['history'])  # определяем обработчик команды /history
def get_history(message):
    chat_id = message.chat.id  # получаем ID чата, из которого была отправлена команда
    messages = bot.history(chat_id, limit=100)  # получаем последние 100 сообщений из чата
    for message in messages:  # проходимся по каждому сообщению из списка сообщений
        bot.send_message(chat_id, message.text)  # отправляем 
        
bot.polling()