from unittest.mock import patch

from communicator.patterns import Patterns
from aggregator import Aggregator
from aggregator.sources import Rapidapi
from ..test_aggregator.mocks import mock_load


def test_greeting_pattern():
    patterns = Patterns()
    greeting = patterns.greeting()
    assert type(greeting) is str


def test_country_pattern():
    info = {
        'key': 'france',
        'country': 'Франция',
        'day': '2020-03-28',
        'time': '2020-03-28T17:15:05+00:00',
        'new_cases': '+3809',
        'active_cases': 25269,
        'critical_cases': 3787,
        'recovered_cases': 5700,
        'total_cases': 32964,
        'new_deaths': '+299',
        'total_deaths': 1995,
        'number': 7,
    }
    country = Patterns().country(info)
    assert country == (
        '*Франция*\n\n'
        'Всего подтвержденных случаев:\n`32964`\n'
        'Новые случаи за сутки:\n`+3809`\n'
        'Всего погибших:\n`1995`\n'
        'Погибших за последние сутки:\n`+299`\n'
        'Выздоровевшие:\n`5700`\n\n'
        '/country\\_france - обновить данные\n'
        '/rating - перейти к рейтингу стран'
    )


@patch.object(Rapidapi, '_load', mock_load)
def test_country_pattern_on_aggregator():
    info = Aggregator().get('франция')
    country = Patterns().country(info)
    assert country == (
        '*Франция*\n\n'
        'Всего подтвержденных случаев:\n`32964`\n'
        'Новые случаи за сутки:\n`+3809`\n'
        'Всего погибших:\n`1995`\n'
        'Погибших за последние сутки:\n`+299`\n'
        'Выздоровевшие:\n`5700`\n\n'
        '/country\\_france - обновить данные\n'
        '/rating - перейти к рейтингу стран'
    )


@patch.object(Rapidapi, '_load', mock_load)
def test_rating_pattern_on_aggregator():
    rating = Aggregator().rating(1, 3)
    world = Aggregator().get()
    result = Patterns().rating(rating, world)
    assert result == (
        '*723319 Мир*    -> /country\\_all\n\n'
        '`112560` США    -> /country\\_usa\n'
        '`86498` Италия    -> /country\\_italy\n'
        '`81394` Китай    -> /country\\_china'
    )
