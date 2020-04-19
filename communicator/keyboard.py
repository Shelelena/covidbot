from typing import List, Union
from aiogram import types
from aiogram.utils.callback_data import CallbackData


class RatingPaginationKeyboard:
    def __init__(self):
        self.callback = CallbackData(
            'rating_page',
            'page', 'max_pages', 'parent')
        self.current_page_name: str = 'current'

    def create(
        self,
        current_page: int = 1,
        max_pages: int = 11,
        parent: str = 'all',
    ) -> types.InlineKeyboardMarkup:

        if max_pages == 1:
            return None

        page_numbers = self._page_numbers(current_page, max_pages)
        page_images = self._page_images(current_page, page_numbers, max_pages)
        page_numbers = self._mark_current(current_page, page_numbers)
        print(page_numbers)
        print(page_images)

        keyboard = self._keyboard(page_images, page_numbers, max_pages, parent)
        return keyboard

    def _page_numbers(self, current_page: int, max_pages: int) -> List[int]:
        if max_pages <= 5:
            pages = list(range(1, max_pages+1))
        elif current_page < 4:
            pages = [1, 2, 3, 4, max_pages]
        elif current_page > max_pages - 3:
            pages = [
                1,
                max_pages - 3,
                max_pages - 2,
                max_pages - 1,
                max_pages]
        else:
            pages = [
                1,
                current_page - 1,
                current_page,
                current_page + 1,
                max_pages]
        return pages

    def _page_images(
        self, current_page: int,
        page_numbers: List[int],
        max_pages: int,
    ) -> List[str]:

        page_images = [str(i) for i in page_numbers]

        if max_pages > 5:
            if current_page >= 4:
                page_images[0] = '<< ' + page_images[0]
                page_images[1] = '< ' + page_images[1]
            if current_page <= max_pages-3:
                page_images[-1] = page_images[-1] + ' >>'
                page_images[-2] = page_images[-2] + ' >'

        page_images[page_numbers.index(current_page)] = (
            '- ' + page_images[page_numbers.index(current_page)] + ' -')
        return page_images

    def _mark_current(
        self,
        current_page: int,
        page_numbers: List[int]
    ) -> List[Union[int, str]]:

        page_numbers = page_numbers.copy()
        page_numbers[page_numbers.index(current_page)] = self.current_page_name
        return page_numbers

    def _keyboard(
        self,
        page_images: List[str],
        page_numbers: List[Union[int, str]],
        max_pages: int,
        parent: str,
    ) -> types.InlineKeyboardMarkup:

        buttons = [
            types.InlineKeyboardButton(
                text=image,
                callback_data=self.callback.new(
                    page=number, max_pages=max_pages, parent=parent)
            )
            for image, number in zip(page_images, page_numbers)
        ]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(*buttons)
        return keyboard
