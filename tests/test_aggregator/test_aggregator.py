from unittest.mock import patch, MagicMock

from aggregator import Aggregator
from aggregator.sources import Rapidapi
from .mocks import mock_load


@patch.object(Rapidapi, '_load', mock_load)
def test_aggregator_case():
    aggr = Aggregator()
    data = aggr.get('France')
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


@patch.object(Rapidapi, 'is_expired', MagicMock())
@patch.object(Rapidapi, 'load', MagicMock())
@patch.object(Rapidapi, 'get_info', MagicMock())
def test_aggregator_calls():
    aggr = Aggregator()

    aggr._rapidapi.is_expired.return_value = False
    aggr.get('Germany')
    aggr.get('USA')

    aggr._rapidapi.is_expired.return_value = True
    aggr.get('Italy')

    assert aggr._rapidapi.is_expired.call_count == 3
    assert aggr._rapidapi.load.call_count == 2
    assert aggr._rapidapi.get_info.call_count == 3


@patch.object(Rapidapi, '_load', mock_load)
def test_wrong_country():
    aggr = Aggregator()
    result = aggr.get('Oz')
    assert len(result) == 1
    assert 'error' in result


@patch.object(Rapidapi, '_load', mock_load)
def test_aggergator_rating():
    aggr = Aggregator()

    rating = aggr.rating(1, 5)
    assert len(rating) == 5
    countries = [i['country'] for i in rating]
    assert countries == ['США', 'Италия', 'Китай', 'Испания', 'Германия']
    total_cases = [i['total_cases'] for i in rating]
    assert total_cases == sorted(total_cases, reverse=True)

    empty_rating = aggr.rating(10, 15)
    assert empty_rating == []
