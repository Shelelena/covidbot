import pytest
from typing import List
from typeguard import check_type

import re
from bs4 import BeautifulSoup
import pandas as pd

from tests.mocks import mock_load
from aggregator.stopcoronasource.datapreparer import StopcoronaDataPreparer
from aggregator.schemas import RegionInfo


mock_load_stopcorona = mock_load('StopcoronaSource')


@pytest.mark.asyncio
async def test_stopcorona_load_data_structure():
    response: str = await mock_load_stopcorona()

    assert type(response) == str
    soup = BeautifulSoup(response, 'html.parser')

    region_table = soup.find_all('div', class_='d-map__list')
    assert len(region_table) == 1

    regions = region_table[0].find_all('tr')
    assert 50 < len(regions) < 150

    for region in regions:
        name = region.find_all('th')
        assert len(name) == 1
        assert not name[0].text.isnumeric()

        values = region.find_all('td')
        assert len(values) == 3
        for value in values:
            assert value.text.isnumeric()


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
