import pytest
from unittest.mock import patch, AsyncMock
from typing import List
from typeguard import check_type

import random
import httpx

from tests.mocks import mock_load
from aggregator.rapidapisource import RapidapiSource
from aggregator.schemas import CountryInfo
from exceptions import NoRapidapiKey, CountryNotFound


mock_load_rapidapi = mock_load('RapidapiSource')


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load_rapidapi)
async def rapidapi():
    rapidapi = RapidapiSource()
    await rapidapi.update()
    return rapidapi


@pytest.mark.asyncio
async def test_no_key_error():
    rapidapi = RapidapiSource()
    with pytest.raises(NoRapidapiKey):
        await rapidapi.update()


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get', AsyncMock())
async def test_load_rapidapi_data():
    rapidapi = RapidapiSource('key')
    data = await rapidapi.load_data()
    assert httpx.AsyncClient.get.called
    response = await httpx.AsyncClient.get()
    assert data == response.text


def test_get_range_of_countries(rapidapi):
    data = rapidapi.data

    for _ in range(5):
        start, end = sorted(random.choices(range(201), k=2))

        result = rapidapi.countries_by_range(start, end)
        check_type(None, result, List[CountryInfo])
        assert len(result) == end - start + 1

        total_cases = [country['total_cases'] for country in result]
        assert total_cases == sorted(total_cases, reverse=True)

        keys = [country['key'] for country in result]
        assert keys == list(data.key.loc[start:end])
        assert keys == list(data.key.loc[
            (data.number >= start) & (data.number <= end)])


def test_get_range_of_countries_that_are_out_of_range(rapidapi):
    data = rapidapi.data

    interval = len(data) - 5, len(data) + 5
    result = rapidapi.countries_by_range(*interval)
    assert len(result) == 5

    result = rapidapi.countries_by_range(-100, -50)
    assert result == []


def test_get_countries_by_keys(rapidapi):
    data = rapidapi.data

    for _ in range(5):
        number_of_keys = random.randint(0, 10)
        keys = random.choices(data.key, k=number_of_keys)
        keys = set(keys)

        result = rapidapi.countries_by_keys(*keys)
        check_type(None, result, List[CountryInfo])
        assert len(result) == len(keys)

        result_keys = [country['key'] for country in result]
        assert keys == set(result_keys)


def test_get_single_countries(rapidapi):
    data = rapidapi.data

    for _ in range(5):
        key = random.choice(data.key)

        result = rapidapi.single_country(key)
        check_type(None, result, CountryInfo)
        assert result['key'] == key


def test_wrong_country(rapidapi):
    result = rapidapi.countries_by_keys('oz')
    assert len(result) == 0

    with pytest.raises(CountryNotFound):
        rapidapi.single_country('oz')
