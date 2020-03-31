import logging
import time
from telebot import types
from datetime import datetime
from .patterns import Patterns


class Communicator:
    def __init__(self, bot, aggregator):
        self.bot = bot
        self.aggregator = aggregator
        self.patterns = Patterns()

    def run_bot(self):
        while True:
            try:
                self.bot.polling(none_stop=True, timeout=60)
            except Exception:
                logging.exception(
                    'top level exception; '
                    f'{str(datetime.now())}'
                )
                self.bot.stop_polling()
                time.sleep(15)

    def catch_uncatched(function):
        def wrapped(self, chat_id, *args, **kwargs):
            try:
                return function(self, chat_id, *args, **kwargs)
            except Exception:
                logging.exception(
                    f'uncatched catched: {str(datetime.now())}; '
                    f'chat: {chat_id}'
                )
                self._send_error(
                    chat_id, {'error': 'Случилась какая-то ошибка. Извините.'})
        return wrapped

    @catch_uncatched
    def send_greeting(self, chat_id):
        logging.debug(f'new greeting! chat_id: {chat_id}')
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
    def send_country_statistics(self, chat_id, country):
        info = self.aggregator.get(country)
        if 'error' in info:
            self._send_error(chat_id, info)
        elif info['key'] == 'all':
            rating = self.aggregator.rating(1, 5)
            self._send_world(chat_id, info, rating)
        else:
            self._send_country(chat_id, info)

    @catch_uncatched
    def send_rating(self, chat_id):
        world = self.aggregator.get('all')
        rating = self.aggregator.rating(1, 20)
        keyboard = self._create_keyboard()
        self.bot.send_message(
            chat_id,
            self.patterns.rating(rating, world),
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    @catch_uncatched
    def edit_rating(self, chat_id, message_id, number=1):
        if number == 'current':
            return
        number = int(number)
        world = self.aggregator.get('all')
        rating = self.aggregator.rating((number-1)*20+1, number*20)
        keyboard = self._create_keyboard(number)
        self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=self.patterns.rating(rating, world),
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    def _send_country(self, chat_id, info):
        self.bot.send_message(
            chat_id,
            self.patterns.country(info),
            parse_mode="Markdown"
        )

    def _send_world(self, chat_id, info, rating):
        self.bot.send_message(
            chat_id,
            self.patterns.world(info, rating),
            parse_mode="Markdown"
        )

    def _send_error(self, chat_id, info):
        self.bot.send_message(
            chat_id,
            self.patterns.error(info)
        )

    def _create_keyboard(self, current_page=1):
        last_page = 11
        assert 1 <= current_page <= last_page
        if current_page < 4:
            pages = [1, 2, 3, 4, last_page]
        elif current_page > last_page-3:
            pages = [1, last_page-3, last_page-2, last_page-1, last_page]
        else:
            pages = [
                1, current_page-1, current_page, current_page+1, last_page]

        page_pics = [str(i) for i in pages]
        if current_page >= 4:
            page_pics[0] = '<< ' + page_pics[0]
            page_pics[1] = '< ' + page_pics[1]
        if current_page <= last_page-3:
            page_pics[-1] = page_pics[-1] + ' >>'
            page_pics[-2] = page_pics[-2] + ' >'

        page_pics[pages.index(current_page)] = (
            '- ' + page_pics[pages.index(current_page)] + ' -')
        pages[pages.index(current_page)] = 'current'

        buttons = [
            types.InlineKeyboardButton(text=pic, callback_data=page)
            for pic, page in zip(page_pics, pages)
        ]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(*buttons)
        return keyboard
