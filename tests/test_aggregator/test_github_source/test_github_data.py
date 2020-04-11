import pytest
from typing import Dict
from typeguard import check_type

import csv
import io
import re
import pandas as pd
from datetime import datetime

from tests.mocks import mock_load
from aggregator.githubsource.datapreparer import GithibDataPreparer
from aggregator.dictionary import CompatibilityDictionary


mock_load_github = mock_load('GithubSource')


@pytest.mark.asyncio
async def test_github_load_data_structure():
    response: str = await mock_load_github()

    assert type(response) == str
    data = list(csv.reader(io.StringIO(response)))

    column_names = data[0]
    assert column_names[:5] == [
        'Province/State', 'Country/Region', 'Lat', 'Long', '1/22/20']
    assert all([
        re.match(r'^\d{1,2}/\d{1,2}/\d{1,2}$', date)
        for date in column_names[4:]
    ])

    assert all([
        all([
            value.isnumeric() and int(value) >= 0
            for value in row[4:]
        ]) for row in data[1:]
    ])


@pytest.mark.asyncio
async def test_github_data_preparer():
    dictionary = CompatibilityDictionary()
    data: str = await mock_load_github()

    data = GithibDataPreparer.prepare(data, dictionary)
    assert type(data) == pd.DataFrame

    columns = data.to_dict()
    check_type(None, columns, Dict[datetime, Dict[str, int]])

    exceptions = {'kosovo'}
    assert set(data.index) - dictionary.keys() == exceptions
    assert len(data) > 200


@pytest.mark.asyncio
async def test_region_handling():
    dictionary = CompatibilityDictionary()
    data: str = await mock_load_github()

    data = GithibDataPreparer._csv_to_dataframe(data)
    data = GithibDataPreparer._colnames_to_datetime(data)
    data = GithibDataPreparer._country_and_region_names_to_keys(
        data, dictionary)

    unhandled_regions = data.filter(['country', 'region']).dropna()
    unhandled_regions = unhandled_regions.loc[
        ~unhandled_regions.region.isin(dictionary.keys())]
    exceptions = {'australia', 'canada', 'china'}
    unhandled_regions = unhandled_regions.loc[
        ~unhandled_regions.country.isin(exceptions)]
    assert len(unhandled_regions) == 0, str(unhandled_regions)
