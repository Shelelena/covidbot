import pytest
from unittest.mock import patch, Mock

from pathlib import Path
import random
import pandas
import matplotlib
import numpy

from tests.mocks import mock_load
from aggregator.githubsource.datapreparer import GithibDataPreparer
from aggregator.githubsource.graph import GithubGraph
from aggregator.matcher import CountryNameMatcher


mock_load_github = mock_load('GithubSource')


@pytest.fixture
async def data():
    data = await mock_load_github()
    matcher = CountryNameMatcher()
    data = GithibDataPreparer.prepare(data, matcher)
    return data


def test_graph(data):
    for _ in range(5):
        key = random.choice(data.index)
        name = CountryNameMatcher().key_to_name(key)
        country = data.loc[key]

        fig = GithubGraph.draw(country, name)

        assert type(fig) == matplotlib.figure.Figure
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


def test_save_graph(data, tmpdir):
    for _ in range(5):
        key = random.choice(data.index)
        name = CountryNameMatcher().key_to_name(key)
        country = data.loc[key]
        fig = GithubGraph.draw(country, name)

        with patch.object(matplotlib.figure.Figure, 'savefig', Mock()):
            png_path = GithubGraph.save(fig, f'{key}_appendix')
            fig.savefig.assert_called_with(png_path, dpi=fig.dpi)
            assert png_path == (
                Path.cwd()
                / GithubGraph.directory
                / f'{key}_appendix.png')

        with tmpdir.as_cwd():
            dir_path = Path.cwd() / GithubGraph.directory
            dir_path.mkdir(exist_ok=True)

            png_path = GithubGraph.save(fig, 'whatever')
            assert png_path.is_file()


@patch.object(GithubGraph, 'draw', Mock())
@patch.object(GithubGraph, 'save', Mock())
def test_draw_and_save_graph(data):
    file_name = 'xxx'
    country_name = 'YYY'
    country = 'pandas series data'

    path = GithubGraph.draw_and_save(country, country_name, file_name)

    GithubGraph.draw.assert_called_once_with(country, country_name)
    GithubGraph.save.assert_called_once_with(GithubGraph.draw(), file_name)
    assert path == GithubGraph.save()


def test_drop_all_graphs(tmpdir):
    with tmpdir.as_cwd():
        dir_path = Path.cwd() / GithubGraph.directory
        assert not dir_path.exists()
        GithubGraph.drop_all()
        assert dir_path.exists()

        png_files = ('1.png', 'all_total.png', 'hello_world.png')
        other_files = ('2.txt', 'greeting', 'bite_me.py')
        for file in png_files + other_files:
            (dir_path / file).touch()

        GithubGraph.drop_all()

        for file in png_files:
            assert not (dir_path / file).exists()

        for file in other_files:
            assert (dir_path / file).exists()


def test_reformat_large_values():
    values = [
        (1, '1'),
        (25, '25'),
        (500, '500'),
        (1000, '1k'),
        (2500, '2.5k'),
        (100_000, '100k'),
        (23_000_000, '23M'),
        (14_100_000, '14.1M'),
        (600_000_000, '600M'),
        (71_000_000_000, '71B'),
    ]
    for value, result in values:
        assert GithubGraph._reformat_large_tick_values(value) == result


def _date(date):
    if type(date) == numpy.float64:
        return matplotlib.dates.num2date(date).date()
    elif type(date) == numpy.datetime64:
        return pandas.to_datetime(date).date()
    elif type(date) == pandas._libs.tslibs.timestamps.Timestamp:
        return date.to_pydatetime().date()
    else:
        print(type(date))
        assert None
