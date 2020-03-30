import telebot

from bot import register_handlers
from aggregator import Aggregator
from config import BOT_TOKEN


def main():
    bot = telebot.TeleBot(BOT_TOKEN)
    aggregator = Aggregator()

    register_handlers(bot, aggregator)
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
