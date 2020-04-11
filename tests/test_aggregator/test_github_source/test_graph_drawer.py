import pytest

import random
import pandas
import matplotlib
import numpy

from tests.mocks import mock_load
from aggregator.githubsource.datapreparer import GithibDataPreparer
from aggregator.githubsource.graph import GithubGraph
from aggregator.dictionary import CompatibilityDictionary


mock_load_github = mock_load('GithubSource')


@pytest.fixture
async def data():
    data = await mock_load_github()
    dictionary = CompatibilityDictionary()
    data = GithibDataPreparer.prepare(data, dictionary)
    return data


def test_graph(data):
    for _ in range(5):
        key = random.choice(data.index)
        name = CompatibilityDictionary().key_to_name(key)
        country = data.loc[key]

        fig = GithubGraph.draw(country, name)
        ax = fig.gca()
        assert len(ax.lines) == 1
        line = ax.lines[0]

        dates = list(country.index)
        values = list(country)

        assert ax.get_title() == name
        assert _date(ax.get_xlim()[0]) == _date(dates[0])
        assert _date(ax.get_xlim()[1]) > _date(dates[-1])
        assert ax.get_ylim()[0] == 0
        assert ax.get_ylim()[1] > values[-1]
        assert all([
            _date(xdata) == _date(date)
            for xdata, date in zip(line.get_xdata(), dates)])
        assert all([
            ydata == value
            for ydata, value in zip(line.get_ydata(), values)])


def _date(date):
    if type(date) == numpy.float64:
        return matplotlib.dates.num2date(date).date()
    if type(date) == numpy.datetime64:
        return pandas.to_datetime(date).date()
    elif type(date) == pandas._libs.tslibs.timestamps.Timestamp:
        return date.to_pydatetime().date()
    else:
        print(type(date))
        assert None
