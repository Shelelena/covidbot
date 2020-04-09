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
from aggregator.dictionary import CompatibilityDictionary


mock_load_rapidapi = mock_load('RapidapiSource')


@pytest.mark.asyncio
async def test_rapidapi_load():
    response: str = await mock_load_rapidapi()

    assert type(response) == str
    response = json.loads(response)

    check_type(None, response, RapidapiResponse)
    assert response['errors'] == []
    assert response['results'] == len(response['response']) > 200


@pytest.mark.asyncio
@patch.object(logging, 'warning', Mock())
async def test_rapidapi_prepare_data():
    dictionary = CompatibilityDictionary()
    data: str = await mock_load_rapidapi()

    data = RapidapiDataPreparer.prepare(data, dictionary)
    assert type(data) == pd.DataFrame

    dict_data = data.to_dict(orient='records')
    check_type(None, dict_data, List[RapidapiCountryInfo])

    assert set(data.key) - dictionary.keys() == set()
    assert len(data) > 200
    assert list(data.total_cases) == sorted(
        list(data.total_cases), reverse=True)
    assert list(data.number) == list(range(len(data)))

    assert not logging.warning.called


@pytest.mark.asyncio
@patch.object(logging, 'warning', Mock())
@patch.object(CompatibilityDictionary, 'keys', Mock())
async def test_rapidapi_log_new_countries():
    dictionary = CompatibilityDictionary()
    dictionary.keys.return_value = {'us', 'russia', 'china'}

    data = await mock_load_rapidapi()
    data = RapidapiDataPreparer.prepare(data, dictionary)

    assert logging.warning.called
