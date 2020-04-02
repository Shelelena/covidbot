from telebot import types
import re


class PaginationKeyboard:
    def __init__(self, total_number_of_pages=11):
        self._last_page = total_number_of_pages
        self._page_id_start = 'rating_page_'
        self.current_page_id = 'current_rating_page'

    def create(self, current_page_id='rating_page_1'):
        current_page = self.extract_current_page(current_page_id)

        page_numbers = self._page_numbers(current_page)
        page_images = self._page_images(current_page, page_numbers)
        page_id_s = self._page_id_s(current_page, page_numbers)

        keyboard = self._keyboard(page_images, page_id_s)
        return keyboard

    def extract_current_page(self, current_page_id):
        pattern = '^' + self._page_id_start + r'(\d+)$'
        match = re.match(pattern, current_page_id)
        assert match
        current_page = int(match.group(1))
        assert 1 <= current_page <= self._last_page
        return current_page

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

    def _page_id_s(self, current_page, page_numbers):
        page_id_s = [self._page_id_start + str(num) for num in page_numbers]
        page_id_s[page_numbers.index(current_page)] = self.current_page_id
        return page_id_s

    def _keyboard(self, page_images, page_id_s):
        buttons = [
            types.InlineKeyboardButton(text=image, callback_data=id)
            for image, id in zip(page_images, page_id_s)
        ]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(*buttons)
        return keyboard
