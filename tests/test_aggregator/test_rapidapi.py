import pytest
from unittest.mock import patch
import json
import pandas as pd

from aggregator.rapidapisource import RapidapiSource
from exceptions import CountryNotFound
from .mocks import mock_load


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load)
def rapidapi():
    rapidapi = RapidapiSource()
    rapidapi.update()
    return rapidapi


def test_unwrap_column():
    data = mock_load()
    data = json.loads(data)
    data = data['response']
    data = pd.DataFrame(data)

    assert 'cases' in data
    assert 'total_cases' not in data
    assert len(data.columns) == 5

    rapidapi = RapidapiSource()
    data = rapidapi._unwrap_dict_column(data, 'cases')

    assert 'cases' not in data
    assert 'total_cases' in data
    assert len(data.columns) == 9


def test_prepare_data():
    rapidapi = RapidapiSource()
    data = mock_load()
    data = rapidapi.prepare_data(data)

    assert type(data) is pd.DataFrame
    assert len(data.columns) == 12
    assert len(data) == 9
    assert data.loc[0, 'key'] == 'all'
    assert data.loc[1, 'key'] == 'usa'
    assert data.loc[8, 'key'] == 'skorea'
    assert data.loc[7, 'total_deaths'] == 1995


def test_single_country(rapidapi):
    result = rapidapi.single_country('iran')
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
        rapidapi.single_country('Oz')
    assert 'No such country' in str(error.value)


def test_by_keys(rapidapi):
    empty = rapidapi.countries_by_keys()
    assert empty == []

    result = rapidapi.countries_by_keys('spain', 'usa', 'skorea')
    assert len(result) == 3
    countries = {i['key'] for i in result}
    assert countries == {'spain', 'usa', 'skorea'}


def test_by_range(rapidapi):
    world = rapidapi.countries_by_range(0, 0)
    assert world[0]['key'] == 'all'

    result = rapidapi.countries_by_range(1, 5)
    assert len(result) == 5
    countries = [i['key'] for i in result]
    assert countries == ['usa', 'italy', 'china', 'spain', 'germany']
    total_cases = [i['total_cases'] for i in result]
    assert total_cases == sorted(total_cases, reverse=True)


def test_range_out_of_range(rapidapi):
    result = rapidapi.countries_by_range(15, 20)
    assert len(result) == 0

    result = rapidapi.countries_by_range(5, 15)
    assert len(result) == 4
