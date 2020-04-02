from pytest import mark
from unittest.mock import patch, Mock, call
import telebot
from communicator.keyboard import PaginationKeyboard


test_data = [
    ['rating_page_1', [
        {'text': '- 1 -', 'callback_data': 'current_rating_page'},
        {'text': '2', 'callback_data': 'rating_page_2'},
        {'text': '3', 'callback_data': 'rating_page_3'},
        {'text': '4 >', 'callback_data': 'rating_page_4'},
        {'text': '11 >>', 'callback_data': 'rating_page_11'},
    ]],
    ['rating_page_3', [
        {'text': '1', 'callback_data': 'rating_page_1'},
        {'text': '2', 'callback_data': 'rating_page_2'},
        {'text': '- 3 -', 'callback_data': 'current_rating_page'},
        {'text': '4 >', 'callback_data': 'rating_page_4'},
        {'text': '11 >>', 'callback_data': 'rating_page_11'},
    ]],
    ['rating_page_6', [
        {'text': '<< 1', 'callback_data': 'rating_page_1'},
        {'text': '< 5', 'callback_data': 'rating_page_5'},
        {'text': '- 6 -', 'callback_data': 'current_rating_page'},
        {'text': '7 >', 'callback_data': 'rating_page_7'},
        {'text': '11 >>', 'callback_data': 'rating_page_11'},
    ]],
    ['rating_page_10', [
        {'text': '<< 1', 'callback_data': 'rating_page_1'},
        {'text': '< 8', 'callback_data': 'rating_page_8'},
        {'text': '9', 'callback_data': 'rating_page_9'},
        {'text': '- 10 -', 'callback_data': 'current_rating_page'},
        {'text': '11', 'callback_data': 'rating_page_11'},
    ]],
]


@mark.parametrize('input, call_args', test_data)
@patch('telebot.types.InlineKeyboardMarkup', Mock())
@patch('telebot.types.InlineKeyboardButton', Mock())
def test_create(input, call_args):
    PaginationKeyboard().create(input)

    calls = [call(**kwargs) for kwargs in call_args]

    telebot.types.InlineKeyboardButton.assert_has_calls(calls)
    telebot.types.InlineKeyboardMarkup.assert_called()
