import aiogram
import logging
import time

from communicator import register_handlers, Communicator
from aggregator import Aggregator
from config import BOT_TOKEN, RAPIDAPI_KEY, LOG_FILE


def main():
    set_logging()

    bot = aiogram.Bot(BOT_TOKEN)
    dispatcher = aiogram.Dispatcher(bot)

    aggregator = Aggregator(rapidapi_key=RAPIDAPI_KEY)
    communicator = Communicator(aggregator)
    register_handlers(communicator, dispatcher)

    run(dispatcher)


def set_logging():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=LOG_FILE,
    )


def run(dispatcher):
    while True:
        try:
            aiogram.executor.start_polling(dispatcher)
        except Exception:
            logging.exception('top level exception')
            time.sleep(15)


if __name__ == '__main__':
    main()
