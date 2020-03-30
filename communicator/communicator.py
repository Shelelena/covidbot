import logging
from datetime import datetime
from .patterns import Patterns


class Communicator:
    def __init__(self, bot, aggregator):
        self.bot = bot
        self.aggregator = aggregator
        self.patterns = Patterns()

    def catch_uncatched(function):
        def wrapped(self, chat_id, *args, **kwargs):
            try:
                return function(self, chat_id, *args, **kwargs)
            except Exception:
                logging.exception(
                    f'time: {str(datetime.now())}; chat: {chat_id}')
                self._send_error(
                    chat_id, {'error': 'Случилось что-то странное'})
        return wrapped

    def run_bot(self):
        self.bot.polling(none_stop=True)

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
        self.bot.send_message(
            chat_id,
            self.patterns.rating(rating, world),
            parse_mode="Markdown"
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
