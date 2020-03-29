import telebot

from aggregator import Aggregator
from config import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)
aggregator = Aggregator()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        (
            'Привет, я помогаю отслеживать текущую обстановку по COVID-19.\n\n'
            'Чтобы получить текущую информацию, введите название страны.'
        )
    )


@bot.message_handler(content_types=['text'])
def return_total_cases(message):
    info = aggregator.get(message.text)
    if 'error' in info:
        bot.send_message(message.chat.id, str(info['error']))
        return
    bot.send_message(message.chat.id, str(info['total_cases']))
