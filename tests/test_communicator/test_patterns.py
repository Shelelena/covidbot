import pytest
from unittest.mock import patch

from communicator.patterns import Patterns
from aggregator import Aggregator
from aggregator.rapidapisource import RapidapiSource
from ..test_aggregator.mocks import mock_load_rapidapi


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load_rapidapi)
async def aggr():
    aggr = Aggregator()
    await aggr.load_sources()
    return aggr


def test_greeting_pattern():
    patterns = Patterns()
    greeting = patterns.greeting()
    assert type(greeting) is str


def test_help_pattern():
    patterns = Patterns()
    greeting = patterns.help()
    assert type(greeting) is str


def test_error():
    patterns = Patterns()
    error_info = {'error': 'Test error'}
    result = patterns.error(error_info)
    assert result == (
        'Test error\n\n'
        '/all - статистика по миру\n'
        '/rating - рейтинг стран\n'
        '/help - справка'
    )


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
        'Новые случаи за сегодня:\n`+3809`\n'
        'Всего погибших:\n`1995`\n'
        'Погибших за сегодня:\n`+299`\n'
        'Выздоровевшие:\n`5700`\n\n'
        '/c\\_france - обновить данные\n'
        '/all - статистика по миру\n'
        '/rating - рейтинг стран'
    )


def test_country_pattern_on_aggregator(aggr):
    info = aggr.country('франция')
    country = Patterns().country(info)
    assert country == (
        '*Франция*\n\n'
        'Всего подтвержденных случаев:\n`32964`\n'
        'Новые случаи за сегодня:\n`+3809`\n'
        'Всего погибших:\n`1995`\n'
        'Погибших за сегодня:\n`+299`\n'
        'Выздоровевшие:\n`5700`\n\n'
        '/c\\_france - обновить данные\n'
        '/all - статистика по миру\n'
        '/rating - рейтинг стран'
    )


def test_world_pattern_on_aggregator(aggr):
    info = aggr.country('all')
    rating = aggr.rating(1, 3)
    world = Patterns().world(info, rating)
    assert world == (
        '*Мир*\n\n'
        'Всего подтвержденных случаев:\n`723319`\n'
        'Новые случаи за сегодня:\n`+960`\n'
        'Всего погибших:\n`33993`\n'
        'Погибших за сегодня:\n`+5001`\n'
        'Выздоровевшие:\n`101010`\n\n'
        '*Топ 5 стран*\n\n'
        '1. `112560` США    -> /c\\_usa\n'
        '2. `86498` Италия    -> /c\\_italy\n'
        '3. `81394` Китай    -> /c\\_china\n\n'
        '/all - обновить данные\n'
        '/rating - рейтинг стран'
    )


def test_rating_pattern_on_aggregator(aggr):
    rating = aggr.rating(1, 3)
    world = aggr.country()
    result = Patterns().rating(rating, world)
    assert result == (
        '*723319 Мир*    -> /all\n\n'
        '1. `112560` США    -> /c\\_usa\n'
        '2. `86498` Италия    -> /c\\_italy\n'
        '3. `81394` Китай    -> /c\\_china'
    )
