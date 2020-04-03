from pytest import mark
from unittest.mock import patch, Mock, call
import aiogram
from communicator.keyboard import PaginationKeyboard


test_data = [
    [1, [
        {'text': '- 1 -', 'callback_data': 'rating_page:current'},
        {'text': '2', 'callback_data': 'rating_page:2'},
        {'text': '3', 'callback_data': 'rating_page:3'},
        {'text': '4 >', 'callback_data': 'rating_page:4'},
        {'text': '11 >>', 'callback_data': 'rating_page:11'},
    ]],
    [3, [
        {'text': '1', 'callback_data': 'rating_page:1'},
        {'text': '2', 'callback_data': 'rating_page:2'},
        {'text': '- 3 -', 'callback_data': 'rating_page:current'},
        {'text': '4 >', 'callback_data': 'rating_page:4'},
        {'text': '11 >>', 'callback_data': 'rating_page:11'},
    ]],
    [6, [
        {'text': '<< 1', 'callback_data': 'rating_page:1'},
        {'text': '< 5', 'callback_data': 'rating_page:5'},
        {'text': '- 6 -', 'callback_data': 'rating_page:current'},
        {'text': '7 >', 'callback_data': 'rating_page:7'},
        {'text': '11 >>', 'callback_data': 'rating_page:11'},
    ]],
    [10, [
        {'text': '<< 1', 'callback_data': 'rating_page:1'},
        {'text': '< 8', 'callback_data': 'rating_page:8'},
        {'text': '9', 'callback_data': 'rating_page:9'},
        {'text': '- 10 -', 'callback_data': 'rating_page:current'},
        {'text': '11', 'callback_data': 'rating_page:11'},
    ]],
]


@mark.parametrize('input, call_args', test_data)
@patch('aiogram.types.InlineKeyboardMarkup', Mock())
@patch('aiogram.types.InlineKeyboardButton', Mock())
def test_create(input, call_args):
    PaginationKeyboard().create(input)

    calls = [call(**kwargs) for kwargs in call_args]

    aiogram.types.InlineKeyboardButton.assert_has_calls(calls)
    aiogram.types.InlineKeyboardMarkup.assert_called()
