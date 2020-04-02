import logging
import time
from datetime import datetime
import requests
from .patterns import Patterns
from .keyboard import PaginationKeyboard


class Communicator:
    def __init__(self, bot, aggregator):
        self.bot = bot
        self.aggregator = aggregator
        self.patterns = Patterns()
        self.keyboard = PaginationKeyboard()
        self._rating_countries_on_page = 20

    def run_bot(self):
        while True:
            try:
                self.bot.polling(none_stop=True, timeout=60)
            except requests.exceptions.Timeout:
                logging.error(
                    ' top level exception: requests Timeout; '
                    f'{str(datetime.now())}'
                )
            except Exception:
                logging.exception(
                    ' top level exception; '
                    f'{str(datetime.now())}'
                )
            finally:
                self.bot.stop_polling()
                time.sleep(15)

    def catch_uncatched(function):
        def wrapped(self, chat_id, *args, **kwargs):
            try:
                attempts = 5
                for attempt in range(1, attempts+1):
                    try:
                        return function(self, chat_id, *args, **kwargs)
                    except requests.exceptions.ConnectionError:
                        logging.error(
                            f' uncatched catched: requests ConnectionError; '
                            f'chat_id: {chat_id}; try: {attempt}; '
                            f'{str(datetime.now())}'
                        )
                        if attempt == attempts:
                            logging.exception()
            except Exception:
                logging.exception(
                    f'uncatched catched: {str(datetime.now())}; '
                    f'chat: {chat_id}'
                )
                self._send_error_message(
                    chat_id, {'error': 'Случилась какая-то ошибка. Извините.'})
        return wrapped

    @catch_uncatched
    def send_greeting(self, chat_id):
        self.bot.send_message(
            chat_id,
            self.patterns.greeting()
        )

    @catch_uncatched
    def send_help(self, chat_id):
        self.bot.send_message(
            chat_id,
            self.patterns.help(),
            disable_web_page_preview=True
        )

    @catch_uncatched
    def send_country(self, chat_id, country):
        info = self.aggregator.get(country)
        if 'error' in info:
            self._send_error_message(chat_id, info)
        elif info['key'] == 'all':
            rating = self.aggregator.rating(1, 5)
            self._send_world_message(chat_id, info, rating)
        else:
            self._send_country_message(chat_id, info)

    @catch_uncatched
    def send_rating(self, chat_id):
        world = self.aggregator.get('all')
        rating = self.aggregator.rating(1, self._rating_countries_on_page)
        keyboard = self.keyboard.create()

        self._send_rating_message(chat_id, rating, world, keyboard)

    @catch_uncatched
    def turn_rating_page(self, chat_id, message_id, call_id, page_id=1):
        if page_id == self.keyboard.current_page_id:
            self._send_no_changes(call_id)
            return

        world = self.aggregator.get('all')
        rating = self.aggregator.rating(
            *self._countries_on_page(page_id))
        keyboard = self.keyboard.create(page_id)

        self._edit_rating_message(
            chat_id, message_id,
            rating, world, keyboard
        )

    def _send_country_message(self, chat_id, info):
        self.bot.send_message(
            chat_id,
            self.patterns.country(info),
            parse_mode="Markdown"
        )

    def _send_world_message(self, chat_id, info, rating):
        self.bot.send_message(
            chat_id,
            self.patterns.world(info, rating),
            parse_mode="Markdown"
        )

    def _send_error_message(self, chat_id, info):
        self.bot.send_message(
            chat_id,
            self.patterns.error(info)
        )

    def _send_no_changes(self, call_id):
        self.bot.answer_callback_query(callback_query_id=call_id)

    def _send_rating_message(self, chat_id, rating, world, keyboard):
        self.bot.send_message(
            chat_id,
            self.patterns.rating(rating, world),
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    def _edit_rating_message(
        self, chat_id, message_id, rating, world, keyboard
    ):
        self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=self.patterns.rating(rating, world),
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    def _countries_on_page(self, page_id):
        page_number = self.keyboard.extract_current_page(page_id)
        return (
            (page_number-1) * self._rating_countries_on_page + 1,
            page_number * self._rating_countries_on_page
        )
