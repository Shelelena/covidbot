import pytest
from unittest.mock import patch
from typing import List
from typeguard import check_type

from communicator.patterns import Patterns
from aggregator import Aggregator
from aggregator.rapidapisource import RapidapiSource
from aggregator.rapidapisource.schemas import RapidapiCountryInfo
from aggregator.githubsource import GithubSource
from tests.mocks import mock_load


@pytest.fixture
def mocked_info():
    info = [
        {
            'key': 'all', 'name': 'Мир', 'number': 0,
            'total_cases': 723319, 'new_cases': '+960',
            'recovered_cases': 101010,
            'total_deaths': 33993, 'new_deaths': '+5001',
        },
        {
            'key': 'usa', 'name': 'США', 'number': 1,
            'total_cases': 112560, 'new_cases': '+8434',
            'recovered_cases': 3219,
            'total_deaths': 1878, 'new_deaths': '+182',
        },
        {
            'key': 'italy', 'name': 'Италия', 'number': 2,
            'total_cases': 86498, 'new_cases': '+5909',
            'recovered_cases': 10950,
            'total_deaths': 9134, 'new_deaths': '+919',
        },
        {
            'key': 'china', 'name': 'Китай', 'number': 3,
            'total_cases': 81394, 'new_cases': '+54',
            'recovered_cases': 74971,
            'total_deaths': 3295, 'new_deaths': '+3',
        },
    ]
    check_type(None, info, List[RapidapiCountryInfo])
    return info


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load('RapidapiSource'))
@patch.object(GithubSource, 'load_data', mock_load('GithubSource'))
async def aggr():
    aggr = Aggregator()
    await aggr.load_sources()
    return aggr


def test_greeting_pattern(mocked_info):
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


def test_country_pattern(mocked_info):
    info = mocked_info[1]
    country = Patterns().country(info)
    assert country == (
        '*США*\n\n'
        'Всего подтвержденных случаев:\n112 560\n'
        'Новые случаи за сегодня:\n8 434\n'
        'Всего погибших:\n1 878\n'
        'Погибшие за сегодня:\n182\n'
        'Выздоровевшие:\n3 219\n\n'
        '/c\\_usa - обновить данные\n'
        '/all - статистика по миру\n'
        '/rating - рейтинг стран'
    )


def test_world_pattern_on_aggregator(mocked_info):
    info = mocked_info[0]
    rating = mocked_info[1:]
    world = Patterns().world(info, rating)
    assert world == (
        '*Мир*\n\n'
        'Всего подтвержденных случаев:\n723 319\n'
        'Новые случаи за сегодня:\n960\n'
        'Всего погибших:\n33 993\n'
        'Погибшие за сегодня:\n5 001\n'
        'Выздоровевшие:\n101 010\n\n'
        '*Топ 5 стран*\n\n'
        '`1.`  112 560  США    -> /c\\_usa\n'
        '`2.`  86 498  Италия    -> /c\\_italy\n'
        '`3.`  81 394  Китай    -> /c\\_china\n\n'
        '/all - обновить данные\n'
        '/rating - рейтинг стран'
    )


def test_rating_pattern_on_aggregator(mocked_info):
    rating = mocked_info[1:]
    world = mocked_info[0]
    result = Patterns().rating(rating, world)
    assert result == (
        '*723 319  Мир*    -> /all\n\n'
        '`1.`  112 560  США    -> /c\\_usa\n'
        '`2.`  86 498  Италия    -> /c\\_italy\n'
        '`3.`  81 394  Китай    -> /c\\_china'
    )
