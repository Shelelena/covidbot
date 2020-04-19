import pytest
from unittest.mock import patch
from typing import List, Union
from typeguard import check_type

from communicator.patterns import Patterns
from aggregator import Aggregator
from aggregator.rapidapisource import RapidapiSource
from aggregator.schemas import CountryInfo
from aggregator.githubsource import GithubSource
from aggregator.stopcoronasource import StopcoronaSource
from aggregator.stopcoronasource.schemas import StopcoronaRegionInfo
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
        {
            'key': 'russia', 'name': 'Россия', 'number': 4,
            'total_cases': 42853, 'new_cases': '+6060',
            'recovered_cases': 3291,
            'total_deaths': 361, 'new_deaths': '+48',
        },
        {
            'key': 'moskva', 'name': 'Москва', 'number': 1,
            'total_cases': 24324,
            'recovered_cases': 1763,
            'total_deaths': 176,
        },
        {
            'key': 'sanktpeterburg', 'name': 'Санкт-Петербург', 'number': 2,
            'total_cases': 1760,
            'recovered_cases': 239,
            'total_deaths': 8,
        },
    ]
    check_type(None, info, List[Union[
        CountryInfo, StopcoronaRegionInfo]])
    return info


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load('RapidapiSource'))
@patch.object(GithubSource, 'load_data', mock_load('GithubSource'))
@patch.object(StopcoronaSource, 'load_data', mock_load('StopcoronaSource'))
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


def test_world_pattern(mocked_info):
    info = mocked_info[0]
    subrating = mocked_info[1:4]
    world = Patterns().country(info, subrating)
    assert world == (
        '*Мир*\n\n'
        'Всего подтвержденных случаев:\n723 319\n'
        'Новые случаи за сегодня:\n960\n'
        'Всего погибших:\n33 993\n'
        'Погибшие за сегодня:\n5 001\n'
        'Выздоровевшие:\n101 010\n\n'
        '*Топ 3*\n\n'
        '`1.`  112 560  США    -> /c\\_usa\n'
        '`2.`  86 498  Италия    -> /c\\_italy\n'
        '`3.`  81 394  Китай    -> /c\\_china\n\n'
        '/all - обновить данные\n'
        '/rating - рейтинг стран'
    )


def test_rating_pattern(mocked_info):
    rating = mocked_info[1:4]
    world = mocked_info[0]
    result = Patterns().rating(rating, world)
    assert result == (
        '*723 319  Мир*    -> /all\n\n'
        '`1.`  112 560  США    -> /c\\_usa\n'
        '`2.`  86 498  Италия    -> /c\\_italy\n'
        '`3.`  81 394  Китай    -> /c\\_china'
    )


def test_region_pattern(mocked_info):
    info = mocked_info[5]
    region = Patterns().country(info)
    assert region == (
        '*Москва*\n\n'
        'Всего подтвержденных случаев:\n24 324\n'
        'Всего погибших:\n176\n'
        'Выздоровевшие:\n1 763\n\n'
        '/c\\_moskva - обновить данные\n'
        '/all - статистика по миру\n'
        '/rating - рейтинг стран'
    )


def test_region_rating_pattern(mocked_info):
    rating = mocked_info[5:7]
    world = mocked_info[4]
    result = Patterns().rating(rating, world)
    assert result == (
        '*42 853  Россия*    -> /russia\n\n'
        '`1.`  24 324  Москва    -> /c\\_moskva\n'
        '`2.`  1 760  Санкт-Петербург    -> /c\\_sanktpeterburg'
    )
