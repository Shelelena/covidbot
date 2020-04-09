import pytest
import json
import pandas as pd
from typing import List
from typeguard import check_type

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
async def test_rapidapi_prepare_data():
    dictionary = CompatibilityDictionary()
    data: str = await mock_load_rapidapi()

    data: pd.DataFrame = RapidapiDataPreparer.prepare(data, dictionary)
    assert type(data) == pd.DataFrame
    assert set(data.key) - dictionary.keys() == set()
    assert len(data) > 200

    data = data.to_dict(orient='records')
    check_type(None, data, List[RapidapiCountryInfo])
