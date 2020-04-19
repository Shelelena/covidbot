from pytest import mark
from unittest.mock import patch, Mock, call
import aiogram
from communicator.keyboard import RatingPaginationKeyboard


test_data = [
    [[1], [
        {'text': '- 1 -', 'callback_data': 'rating_page:current:11:all'},
        {'text': '2', 'callback_data': 'rating_page:2:11:all'},
        {'text': '3', 'callback_data': 'rating_page:3:11:all'},
        {'text': '4 >', 'callback_data': 'rating_page:4:11:all'},
        {'text': '11 >>', 'callback_data': 'rating_page:11:11:all'},
    ]],
    [[3], [
        {'text': '1', 'callback_data': 'rating_page:1:11:all'},
        {'text': '2', 'callback_data': 'rating_page:2:11:all'},
        {'text': '- 3 -', 'callback_data': 'rating_page:current:11:all'},
        {'text': '4 >', 'callback_data': 'rating_page:4:11:all'},
        {'text': '11 >>', 'callback_data': 'rating_page:11:11:all'},
    ]],
    [[6, 10, 'russia'], [
        {'text': '<< 1', 'callback_data': 'rating_page:1:10:russia'},
        {'text': '< 5', 'callback_data': 'rating_page:5:10:russia'},
        {'text': '- 6 -', 'callback_data': 'rating_page:current:10:russia'},
        {'text': '7 >', 'callback_data': 'rating_page:7:10:russia'},
        {'text': '10 >>', 'callback_data': 'rating_page:10:10:russia'},
    ]],
    [[10], [
        {'text': '<< 1', 'callback_data': 'rating_page:1:11:all'},
        {'text': '< 8', 'callback_data': 'rating_page:8:11:all'},
        {'text': '9', 'callback_data': 'rating_page:9:11:all'},
        {'text': '- 10 -', 'callback_data': 'rating_page:current:11:all'},
        {'text': '11', 'callback_data': 'rating_page:11:11:all'},
    ]],
    [[2, 3], [
        {'text': '1', 'callback_data': 'rating_page:1:3:all'},
        {'text': '- 2 -', 'callback_data': 'rating_page:current:3:all'},
        {'text': '3', 'callback_data': 'rating_page:3:3:all'},
    ]],
]


@mark.parametrize('input, call_args', test_data)
@patch('aiogram.types.InlineKeyboardMarkup', Mock())
@patch('aiogram.types.InlineKeyboardButton', Mock())
def test_create(input, call_args):
    RatingPaginationKeyboard().create(*input)

    calls = [call(**kwargs) for kwargs in call_args]
    print(len(calls))

    aiogram.types.InlineKeyboardButton.assert_has_calls(calls)
    aiogram.types.InlineKeyboardMarkup.assert_called()
