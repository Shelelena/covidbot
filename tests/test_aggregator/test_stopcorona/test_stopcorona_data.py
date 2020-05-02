import pytest
from typing import List
from typeguard import check_type

import re
from bs4 import BeautifulSoup
import json
import pandas as pd

from tests.mocks import mock_load
from aggregator.stopcoronasource.datapreparer import StopcoronaDataPreparer
from aggregator.schemas import RegionInfo, StopcoronaResponseItems


mock_load_stopcorona = mock_load('StopcoronaSource')


@pytest.mark.asyncio
async def test_stopcorona_load_data_structure():
    response: str = await mock_load_stopcorona()

    assert type(response) == str
    soup = BeautifulSoup(response, 'html.parser')

    region_table = soup.find_all('cv-spread-overview')
    assert len(region_table) == 1
    region_table = region_table[0]

    assert ':spread-data' in region_table.attrs
    json_data: str = region_table.attrs[':spread-data']
    json_data: dict = json.loads(json_data)

    assert 50 < len(json_data) < 150
    check_type(None, json_data, List[StopcoronaResponseItems])


@pytest.mark.asyncio
async def test_sropcorona_prepare_data():
    data: str = await mock_load_stopcorona()

    data = StopcoronaDataPreparer.prepare(data)
    assert type(data) == pd.DataFrame

    rows = data.to_dict(orient='records')
    check_type(None, rows, List[RegionInfo])

    assert 50 < len(data) < 150
    assert list(data.total_cases) == sorted(
        list(data.total_cases), reverse=True)
    assert list(data.number) == list(range(1, len(data)+1))

    for row in rows:
        assert re.match(r'^[А-Яа-я \-\(\)]+$', row['name'])
        assert re.match(r'^[a-z]+$', row['key'])
        assert len(row['key']) <= 23

    unique_keys = {row['key'] for row in rows}
    assert len(unique_keys) == len(rows)
