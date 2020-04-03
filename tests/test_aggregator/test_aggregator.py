import pytest
from unittest.mock import patch, MagicMock

from aggregator import Aggregator
from aggregator.rapidapisource import RapidapiSource
from .mocks import mock_load


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load)
def aggr():
    aggr = Aggregator()
    aggr.load_sources()
    return aggr


def test_aggregator_case(aggr):
    data = aggr.country('France')
    assert data == {
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


@patch.object(RapidapiSource, 'is_expired', MagicMock())
@patch.object(RapidapiSource, 'update', MagicMock())
@patch.object(RapidapiSource, 'single_country', MagicMock())
def test_aggregator_calls(aggr):
    aggr._rapidapi.is_expired.return_value = False
    aggr.country('Germany')
    aggr.country('USA')

    aggr._rapidapi.is_expired.return_value = True
    aggr.country('Italy')

    assert aggr._rapidapi.is_expired.call_count == 3
    assert aggr._rapidapi.update.call_count == 1
    assert aggr._rapidapi.single_country.call_count == 3


def test_wrong_country(aggr):
    result = aggr.country('Oz')
    assert len(result) == 1
    assert 'error' in result


def test_aggergator_rating(aggr):
    rating = aggr.rating(1, 5)
    assert len(rating) == 5
    countries = [i['country'] for i in rating]
    assert countries == ['США', 'Италия', 'Китай', 'Испания', 'Германия']
    total_cases = [i['total_cases'] for i in rating]
    assert total_cases == sorted(total_cases, reverse=True)

    empty_rating = aggr.rating(10, 15)
    assert empty_rating == []
