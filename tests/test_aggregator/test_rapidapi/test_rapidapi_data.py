import pytest
from unittest.mock import patch, Mock
from typing import List
from typeguard import check_type

import json
import pandas as pd
import logging

from tests.mocks import mock_load
from aggregator.rapidapisource.datapreparer import RapidapiDataPreparer
from aggregator.rapidapisource.schemas import RapidapiCountryInfo
from aggregator.rapidapisource.schemas import RapidapiResponse
from aggregator.matcher import CountryNameMatcher


mock_load_rapidapi = mock_load('RapidapiSource')


@pytest.mark.asyncio
async def test_rapidapi_load_data_structure():
    response: str = await mock_load_rapidapi()

    assert type(response) == str
    response = json.loads(response)

    check_type(None, response, RapidapiResponse)
    assert response['errors'] == []
    assert response['results'] == len(response['response']) > 200


@pytest.mark.asyncio
@patch.object(logging, 'warning', Mock())
async def test_rapidapi_prepare_data():
    matcher = CountryNameMatcher()
    data: str = await mock_load_rapidapi()

    data = RapidapiDataPreparer.prepare(data, matcher)
    assert type(data) == pd.DataFrame

    rows = data.to_dict(orient='records')
    check_type(None, rows, List[RapidapiCountryInfo])

    assert set(data.key) - matcher.keys() == set()
    assert len(data) > 200
    assert list(data.total_cases) == sorted(
        list(data.total_cases), reverse=True)
    assert list(data.number) == list(range(len(data)))

    assert not logging.warning.called


@pytest.mark.asyncio
@patch.object(logging, 'warning', Mock())
@patch.object(CountryNameMatcher, 'keys', Mock())
async def test_rapidapi_log_new_countries():
    matcher = CountryNameMatcher()
    matcher.keys.return_value = {'us', 'russia', 'china'}

    data = await mock_load_rapidapi()
    data = RapidapiDataPreparer.prepare(data, matcher)

    assert logging.warning.called
