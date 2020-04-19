import pytest
from unittest.mock import patch, AsyncMock, Mock
from typeguard import check_type
from typing import List

import random
import logging
from httpx._exceptions import ReadTimeout, ConnectTimeout

from aggregator import Aggregator
from aggregator.rapidapisource import RapidapiSource
from aggregator.schemas import CountryInfo
from aggregator.githubsource import GithubSource
from aggregator.stopcoronasource import StopcoronaSource
from aggregator.stopcoronasource.schemas import StopcoronaRegionInfo
from tests.mocks import mock_load
from exceptions import CountryNotFound


@pytest.fixture
@patch.object(RapidapiSource, 'load_data', mock_load('RapidapiSource'))
@patch.object(GithubSource, 'load_data', mock_load('GithubSource'))
@patch.object(StopcoronaSource, 'load_data', mock_load('StopcoronaSource'))
async def aggr():
    aggr = Aggregator()
    await aggr.load_sources()
    return aggr


@pytest.mark.asyncio
@patch.object(logging, 'error', Mock())
@patch.object(logging, 'exception', Mock())
@patch.object(RapidapiSource, 'update', AsyncMock())
@patch.object(GithubSource, 'update', AsyncMock())
@patch.object(StopcoronaSource, 'update', AsyncMock())
async def test_update():
    aggr = Aggregator()
    await aggr.update()
    aggr._rapidapi.update.assert_called_once()
    aggr._github.update.assert_called_once()
    aggr._stopcorona.update.assert_called_once()

    with patch.object(RapidapiSource, 'update', _async_raise(ReadTimeout)):
        aggr = Aggregator()
        await aggr.update()
        logging.error.assert_called_with('ReadTimeout in source update')

    with patch.object(GithubSource, 'update', _async_raise(ConnectTimeout)):
        aggr = Aggregator()
        await aggr.update()
        logging.error.assert_called_with('ConnectTimeout in source update')

    with patch.object(GithubSource, 'update', _async_raise(ZeroDivisionError)):
        aggr = Aggregator()
        await aggr.update()
        logging.exception.assert_called_once()


def test_get_country(aggr):
    for _ in range(5):
        country = random.choice(list(aggr._rapidapi._matcher.keys()))
        result = aggr.country(country)

        check_type(None, result, CountryInfo)
        assert result['key'] == country

    wrong_result = aggr.country('oz')
    assert wrong_result == {'error': 'Страна не найдена'}


def test_get_region(aggr):
    for _ in range(5):
        region = random.choice(list(aggr._stopcorona.data.name))
        result = aggr.country(region)

        check_type(None, result, StopcoronaRegionInfo)
        assert result['name'] == region

    wrong_result = aggr.country('oz')
    assert wrong_result == {'error': 'Страна не найдена'}


def test_get_rating(aggr):
    rating = aggr.rating(1, 5)
    check_type(None, rating, List[CountryInfo])

    total_cases = [i['total_cases'] for i in rating]
    assert total_cases == sorted(total_cases, reverse=True)


def test_get_region_rating(aggr):
    rating = aggr.rating(1, 5, parent='russia')
    check_type(None, rating, List[StopcoronaRegionInfo])

    total_cases = [i['total_cases'] for i in rating]
    assert total_cases == sorted(total_cases, reverse=True)


def test_get_graph(aggr):
    with patch.object(GithubSource, 'graph', Mock()):
        result = aggr.graph('country')
        aggr._github.graph.assert_called_once_with('country')
        assert result == aggr._github.graph()

    with patch.object(GithubSource, 'graph', _sync_raise(CountryNotFound)):
        result = aggr.graph('country')
        assert result is None


def test_save_id(aggr):
    aggr.save_graph_id('country', 'id')
    assert aggr._github.graph_ids['country'] == 'id'


def _async_raise(exception):
    async def mocked_method(*args, **kwargs):
        raise exception
    return mocked_method


def _sync_raise(exception):
    def mocked_method(*args, **kwargs):
        raise exception
    return mocked_method
