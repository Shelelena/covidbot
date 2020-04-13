import pytest
from unittest.mock import patch, Mock, AsyncMock

import httpx
from datetime import datetime
from pathlib import Path
import pandas as pd

from tests.mocks import mock_load
from aggregator.githubsource import GithubSource
from aggregator.githubsource.datapreparer import GithibDataPreparer
from aggregator.githubsource.graph import GithubGraph
from aggregator.dictionary import CompatibilityDictionary
from exceptions import CountryNotFound


mock_load_github = mock_load('GithubSource')


@pytest.fixture
@patch.object(GithubSource, 'load_data', mock_load_github)
async def github():
    github = GithubSource()
    await github.update()
    return github


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get', AsyncMock())
async def test_load_github_data():
    github = GithubSource()
    data = await github.load_data()
    assert httpx.AsyncClient.get.called
    response = await httpx.AsyncClient.get()
    assert data == response.text


@pytest.mark.asyncio
async def test_data_is_new():
    data = await mock_load_github()
    data = GithibDataPreparer.prepare(data, CompatibilityDictionary())
    github = GithubSource()
    assert github._new_data(data)

    github.data = data.copy()
    assert not github._new_data(data)

    new_date = datetime(year=3_000, month=1, day=1)
    data[new_date] = [0]*len(data)
    assert github._new_data(data)

    new_date = datetime(year=1_000, month=1, day=1)
    data[new_date] = [0]*len(data)
    assert not github._new_data(data)


def test_dropping_old_graphs(tmpdir):
    with tmpdir.as_cwd():
        dir_path = Path.cwd() / GithubGraph.directory
        github = GithubSource()

        assert not dir_path.exists()
        github._drop_graphs()
        assert dir_path.exists()

        pic_file = dir_path / 'pic_1.png'
        pic_file.touch()
        github.graph_file_paths = {'dict': 'is_not_empty'}
        github.graph_ids = {'1': '2', '3': '4'}

        assert pic_file.exists()

        github._drop_graphs()

        assert not pic_file.exists()
        assert github.graph_file_paths == github.graph_ids == {}


@pytest.mark.asyncio
@patch.object(GithubSource, '_drop_graphs', Mock())
async def test_prepare_github_data():
    github = GithubSource()
    data: str = await mock_load_github()
    result_data = github.prepare_data(data)

    assert type(result_data) == pd.DataFrame
    assert github._drop_graphs.called


@patch.object(GithubGraph, 'draw_and_save', Mock())
def test_get_graph(github):
    assert github.graph_file_paths == github.graph_ids == {}

    result = github.graph('russia')
    GithubGraph.draw_and_save.assert_called_once()
    assert github.graph_file_paths == {'russia': GithubGraph.draw_and_save()}
    assert github.graph_ids == {}
    assert result == GithubGraph.draw_and_save()

    github.graph_file_paths['usa'] = 'us_file_path'
    result = github.graph('usa')
    assert result == 'us_file_path'

    github.save_graph_id('usa', 'us_file_id')
    assert github.graph_ids == {'usa': 'us_file_id'}
    result = github.graph('usa')
    assert result == 'us_file_id'

    with pytest.raises(CountryNotFound):
        github.graph('oz')
