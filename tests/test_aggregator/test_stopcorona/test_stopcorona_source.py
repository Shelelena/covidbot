import pytest
from unittest.mock import patch, AsyncMock
from typing import List
from typeguard import check_type

import random
import httpx

from tests.mocks import mock_load
from aggregator.stopcoronasource import StopcoronaSource
from aggregator.stopcoronasource.schemas import StopcoronaRegionInfo
from exceptions import CountryNotFound


mock_load_stopcorona = mock_load('StopcoronaSource')


@pytest.fixture
@patch.object(StopcoronaSource, 'load_data', mock_load_stopcorona)
async def stopcorona():
    stopcorona = StopcoronaSource()
    await stopcorona.update()
    return stopcorona


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get', AsyncMock())
async def test_load_stopcorona_data():
    stopcorona = StopcoronaSource('key')
    data = await stopcorona.load_data()
    assert httpx.AsyncClient.get.called
    response = await httpx.AsyncClient.get()
    assert data == response.text


def test_get_range_of_regions(stopcorona):
    data = stopcorona.data

    for _ in range(5):
        start, end = sorted(random.choices(range(1, 81), k=2))

        result = stopcorona.regions_by_range(start, end)
        check_type(None, result, List[StopcoronaRegionInfo])
        assert len(result) == end - start + 1

        total_cases = [region['total_cases'] for region in result]
        assert total_cases == sorted(total_cases, reverse=True)

        keys = [region['key'] for region in result]
        assert keys == list(data.key.loc[start:end])
        assert keys == list(data.key.loc[
            (data.number >= start) & (data.number <= end)])


def test_get_regions_by_keys(stopcorona):
    data = stopcorona.data

    for _ in range(5):
        number_of_keys = random.randint(0, 10)
        keys = random.choices(list(data.key), k=number_of_keys)
        keys = set(keys)

        result = stopcorona.regions_by_keys(*keys)
        check_type(None, result, List[StopcoronaRegionInfo])
        assert len(result) == len(keys)

        result_keys = [country['key'] for country in result]
        assert keys == set(result_keys)


def test_get_single_regions(stopcorona):
    data = stopcorona.data

    for _ in range(5):
        key = random.choice(list(data.key))

        result = stopcorona.single_region(key)
        check_type(None, result, StopcoronaRegionInfo)
        assert result['key'] == key


def test_wrong_country(stopcorona):
    result = stopcorona.regions_by_keys('washington')
    assert len(result) == 0

    with pytest.raises(CountryNotFound):
        stopcorona.single_region('washington')
