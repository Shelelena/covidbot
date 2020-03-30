import telebot

from communicator import register_handlers, Communicator
from aggregator import Aggregator
from config import BOT_TOKEN, RAPIDAPI_KEY


def main():
    bot = telebot.TeleBot(BOT_TOKEN)
    aggregator = Aggregator(rapidapi_key=RAPIDAPI_KEY)
    communicator = Communicator(bot, aggregator)
    register_handlers(communicator)

    communicator.run_bot()


if __name__ == '__main__':
    main()
