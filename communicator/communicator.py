import logging
from typing import Union, Optional, List, Tuple, Literal
from pathlib import Path
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from .patterns import Patterns
from .keyboard import RatingPaginationKeyboard
from aggregator import Aggregator, CountryInfo


class Communicator:
    def __init__(self, aggregator: Aggregator):
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
    async def send_greeting(self, message: Message) -> Message:
        return await message.answer(self.patterns.greeting())

    @catch_uncatched
    async def send_help(self, message: Message) -> Message:
        return await message.answer(
            self.patterns.help(),
            disable_web_page_preview=True
        )

    @catch_uncatched
    async def send_country(
        self,
        message: Message,
        country: str,
    ) -> Message:

        info = self.aggregator.country(country)
        if 'error' in info:
            return await self._send_error_message(message, info)
        else:
            graph = self.aggregator.graph(country)
            if info['key'] == 'all':
                rating = self.aggregator.rating(1, 5)
                sent_message = await self._send_world_message(
                    message, info, rating, graph)
            else:
                sent_message = await self._send_country_message(
                    message, info, graph)
            self._save_graph_id(graph, info['key'], sent_message)
            return sent_message

    @catch_uncatched
    async def send_rating(
        self,
        message: Message
    ) -> Message:

        world = self.aggregator.country('all')
        rating = self.aggregator.rating(1, self._max_countries_on_rating_page)
        keyboard = self.keyboard.create()

        return await self._send_rating_message(
            message, rating, world, keyboard)

    @catch_uncatched
    async def turn_rating_page(
        self,
        query: CallbackQuery,
        page: str = '1'
    ) -> Message:

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

    async def _send_country_message(
        self,
        message: Message,
        info: CountryInfo,
        graph: Union[Path, str, None] = None
    ) -> Message:

        return await self._send_message(
            message,
            text=self.patterns.country(info),
            parse_mode="Markdown",
            photo=graph
        )

    async def _send_world_message(
        self,
        message: Message,
        info: CountryInfo,
        rating: List[CountryInfo],
        graph=None
    ) -> Message:

        return await self._send_message(
            message,
            text=self.patterns.world(info, rating),
            parse_mode="Markdown",
            photo=graph,
        )

    async def _send_error_message(
        self,
        message: Message,
        info: CountryInfo,
    ) -> Message:
        return await message.answer(self.patterns.error(info))

    async def _send_no_changes(self, query: CallbackQuery) -> bool:
        return await query.answer(text='Эта страница открыта')

    async def _send_rating_message(
        self,
        message: Message,
        rating: List[CountryInfo],
        world: CountryInfo,
        keyboard: InlineKeyboardMarkup,
    ):

        return await message.answer(
            self.patterns.rating(rating, world),
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    async def _edit_rating_message(
        self,
        message: Message,
        rating: List[CountryInfo],
        world: CountryInfo,
        keyboard: InlineKeyboardMarkup,
    ) -> Message:

        return await message.edit_text(
            text=self.patterns.rating(rating, world),
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    async def _send_message(
        self,
        message: Message,
        text: str,
        parse_mode: Optional[Literal['Markdown']] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        photo: Union[Path, str, None] = None
    ) -> Message:

        if photo is None:
            return await message.answer(
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        elif issubclass(type(photo), Path):
            with photo.open('rb') as file:
                return await message.answer_photo(
                    photo=file,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        else:
            return await message.answer_photo(
                photo=photo,
                caption=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )

    def _countries_on_page(self, page: int) -> Tuple[int, int]:
        return (
            (page-1) * self._max_countries_on_rating_page + 1,
            page * self._max_countries_on_rating_page
        )

    def _find_message(self, *args, **kwargs) -> Message:
        if 'message' in kwargs:
            message = kwargs['message']
        elif 'query' in kwargs:
            message = kwargs['query'].message
        else:
            message = args[0]
            if hasattr(message, 'message'):
                message = message.message
        return message

    async def _try_to_send_error_report(self, message: Message):
        try:
            return await self._send_error_message(
                message,
                {'error': 'Извините, Случилась какая-то ошибка.'}
            )
        except Exception:
            logging.error(
                f'error report failed; chat_id: {message.chat.id}')

    def _save_graph_id(
        self,
        graph: Union[Path, str, None],
        key: str,
        sent_message: Message
    ) -> None:

        if issubclass(type(graph), Path):
            self.aggregator.save_graph_id(
                key,
                sent_message.photo[-1].file_id)
