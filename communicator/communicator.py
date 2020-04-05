import logging
from .patterns import Patterns
from .keyboard import RatingPaginationKeyboard


class Communicator:
    def __init__(self, aggregator):
        self.aggregator = aggregator
        self.patterns = Patterns()
        self.keyboard = RatingPaginationKeyboard()
        self._max_countries_on_rating_page = 20

    def catch_uncatched(coroutine):
        async def wrapped(self, *args, **kwargs):
            try:
                return await coroutine(self, *args, **kwargs)

            except Exception:
                message = self._find_message(*args, **kwargs)
                logging.exception(
                    f'uncatched catched; chat: {message.chat.id}')
                return await self._try_to_send_error_report(message)

        return wrapped

    @catch_uncatched
    async def send_greeting(self, message):
        return await message.answer(self.patterns.greeting())

    @catch_uncatched
    async def send_help(self, message):
        return await message.answer(
            self.patterns.help(),
            disable_web_page_preview=True
        )

    @catch_uncatched
    async def send_country(self, message, country):
        info = self.aggregator.country(country)
        if 'error' in info:
            return await self._send_error_message(message, info)
        elif info['key'] == 'all':
            rating = self.aggregator.rating(1, 5)
            return await self._send_world_message(message, info, rating)
        else:
            return await self._send_country_message(message, info)

    @catch_uncatched
    async def send_rating(self, message):
        world = self.aggregator.country('all')
        rating = self.aggregator.rating(1, self._max_countries_on_rating_page)
        keyboard = self.keyboard.create()

        return await self._send_rating_message(
            message, rating, world, keyboard)

    @catch_uncatched
    async def turn_rating_page(self, query, page='1'):
        if page == self.keyboard.current_page_name:
            return await self._send_no_changes(query)
        page = int(page)

        world = self.aggregator.country('all')
        rating = self.aggregator.rating(
            *self._countries_on_page(page))
        keyboard = self.keyboard.create(page)

        return await self._edit_rating_message(
            query.message,
            rating, world, keyboard
        )

    async def _send_country_message(self, message, info):
        return await message.answer(
            self.patterns.country(info),
            parse_mode="Markdown"
        )

    async def _send_world_message(self, message, info, rating):
        return await message.answer(
            self.patterns.world(info, rating),
            parse_mode="Markdown"
        )

    async def _send_error_message(self, message, info):
        return await message.answer(self.patterns.error(info))

    async def _send_no_changes(self, query):
        return await query.answer()

    async def _send_rating_message(self, message, rating, world, keyboard):
        return await message.answer(
            self.patterns.rating(rating, world),
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    async def _edit_rating_message(self, message, rating, world, keyboard):
        return await message.edit_text(
            text=self.patterns.rating(rating, world),
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    def _countries_on_page(self, page):
        return (
            (page-1) * self._max_countries_on_rating_page + 1,
            page * self._max_countries_on_rating_page
        )

    def _find_message(self, *args, **kwargs):
        if 'message' in kwargs:
            message = kwargs['message']
        elif 'query' in kwargs:
            message = kwargs['query'].message
        else:
            message = args[0]
            if hasattr(message, 'message'):
                message = message.message
        return message

    async def _try_to_send_error_report(self, message):
        try:
            return await self._send_error_message(
                message,
                {'error': 'Извините, Случилась какая-то ошибка.'}
            )
        except Exception:
            logging.error(
                f'error report failed; chat_id: {message.chat.id}')
