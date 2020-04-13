import pytest
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime, timedelta

from aggregator.sources import Source


def test_cant_create_source_abstraction():
    with pytest.raises(TypeError) as error:
        Source()
    assert "Can't instantiate abstract class" in str(error.value)


def test_abstract_methods_not_inherited():
    class Heir(Source):
        pass
    with pytest.raises(TypeError) as error:
        Heir()
    assert "Can't instantiate abstract class" in str(error.value)


class MinimalHeir(Source):
    def __init__(self):
        self.expire_time = timedelta(seconds=30)
        self.last_updated = None

    async def load_data(self):
        return 'data'

    def prepare_data(self, data):
        return data


def test_minimal_heir():
    MinimalHeir()
    assert issubclass(MinimalHeir, Source)


def test_is_expired():
    heir = MinimalHeir()
    assert heir.is_expired()
    heir.last_updated = datetime.now() - timedelta(minutes=1)
    assert heir.is_expired()


def test_is_not_expired():
    heir = MinimalHeir()
    heir.last_updated = datetime.now() - timedelta(seconds=10)
    assert not heir.is_expired()


@pytest.mark.asyncio
@patch.object(MinimalHeir, 'load_data', AsyncMock())
@patch.object(MinimalHeir, 'prepare_data', Mock())
async def test_update():
    heir = MinimalHeir()
    await heir.update()
    heir.load_data.assert_called_once()
    heir.prepare_data.assert_called_once()
    assert datetime.now() - heir.last_updated < timedelta(seconds=3)
