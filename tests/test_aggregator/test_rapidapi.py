import pytest
from unittest.mock import patch
import json
import pandas as pd

from aggregator.sources import Rapidapi
from exceptions import CountryNotFound
from .mocks import mock_load


def test_unwrap_column():
    data = mock_load()
    data = json.loads(data)
    data = data['response']
    data = pd.DataFrame(data)

    assert 'cases' in data
    assert 'total_cases' not in data
    assert len(data.columns) == 5

    rapidapi = Rapidapi()
    data = rapidapi._unwrap_column(data, 'cases')

    assert 'cases' not in data
    assert 'total_cases' in data
    assert len(data.columns) == 9


def test_prepare_data():
    rapidapi = Rapidapi()
    data = mock_load()
    data = rapidapi._prepare_data(data)

    assert type(data) is pd.DataFrame
    assert len(data.columns) == 12
    assert len(data) == 9
    assert data.loc[0, 'key'] == 'all'
    assert data.loc[1, 'key'] == 'usa'
    assert data.loc[8, 'key'] == 'skorea'
    assert data.loc[7, 'total_deaths'] == 1995


@patch.object(Rapidapi, '_load', mock_load)
def test_get_info():
    rapidapi = Rapidapi()
    rapidapi.load()

    result = rapidapi.get_info('iran')
    assert result == {
        'key': 'iran',
        'country': 'Иран',
        'day': '2020-03-28',
        'time': '2020-03-28T17:15:05+00:00',
        'new_cases': '+3076',
        'active_cases': 21212,
        'critical_cases': 3206,
        'recovered_cases': 11679,
        'total_cases': 35408,
        'new_deaths': '+139',
        'total_deaths': 2517,
        'number': 6,
    }

    with pytest.raises(CountryNotFound) as error:
        rapidapi.get_info('Oz')
    assert 'No such country' in str(error.value)


@patch.object(Rapidapi, '_load', mock_load)
def test_range():
    rapidapi = Rapidapi()
    rapidapi.load()

    world = rapidapi.range(0, 0)
    assert world[0]['key'] == 'all'

    result = rapidapi.range(1, 5)
    assert len(result) == 5
    countries = [i['key'] for i in result]
    assert countries == ['usa', 'italy', 'china', 'spain', 'germany']
    total_cases = [i['total_cases'] for i in result]
    assert total_cases == sorted(total_cases, reverse=True)


@patch.object(Rapidapi, '_load', mock_load)
def test_range_out_of_range():
    rapidapi = Rapidapi()
    rapidapi.load()

    result = rapidapi.range(15, 20)
    assert len(result) == 0

    result = rapidapi.range(5, 15)
    assert len(result) == 4
