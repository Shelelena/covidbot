from aiogram import types
from aiogram.utils.callback_data import CallbackData


class PaginationKeyboard:
    def __init__(self, total_number_of_pages=11):
        self.callback = CallbackData('rating_page', 'page')
        self._last_page = total_number_of_pages
        self._page_id_prefix = 'rating_page:'
        self.current_page_name = 'current'

    def create(self, current_page=1):
        page_numbers = self._page_numbers(current_page)
        page_images = self._page_images(current_page, page_numbers)
        page_numbers = self._mark_current(current_page, page_numbers)

        keyboard = self._keyboard(page_images, page_numbers)
        return keyboard

    def _page_numbers(self, current_page):
        if current_page < 4:
            pages = [1, 2, 3, 4, self._last_page]
        elif current_page > self._last_page - 3:
            pages = [
                1,
                self._last_page - 3,
                self._last_page - 2,
                self._last_page - 1,
                self._last_page]
        else:
            pages = [
                1,
                current_page - 1,
                current_page,
                current_page + 1,
                self._last_page]
        return pages

    def _page_images(self, current_page, page_numbers):
        page_images = [str(i) for i in page_numbers]
        if current_page >= 4:
            page_images[0] = '<< ' + page_images[0]
            page_images[1] = '< ' + page_images[1]
        if current_page <= self._last_page-3:
            page_images[-1] = page_images[-1] + ' >>'
            page_images[-2] = page_images[-2] + ' >'
        page_images[page_numbers.index(current_page)] = (
            '- ' + page_images[page_numbers.index(current_page)] + ' -')
        return page_images

    def _mark_current(self, current_page, page_numbers):
        page_numbers = page_numbers.copy()
        page_numbers[page_numbers.index(current_page)] = self.current_page_name
        return page_numbers

    def _keyboard(self, page_images, page_numbers):
        buttons = [
            types.InlineKeyboardButton(
                text=image,
                callback_data=self.callback.new(page=number)
            )
            for image, number in zip(page_images, page_numbers)
        ]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(*buttons)
        return keyboard
