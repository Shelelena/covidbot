import pytest
from unittest.mock import patch, Mock
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
        self._expire_time = timedelta(seconds=30)

    def _load(self):
        return 'data'

    def _prepare_data(self, data):
        return data


def test_minimal_heir():
    MinimalHeir()
    assert issubclass(MinimalHeir, Source)


def test_is_expired():
    heir = MinimalHeir()
    heir._last_updated = datetime.now() - timedelta(minutes=1)
    assert heir.is_expired()


def test_is_not_expired():
    heir = MinimalHeir()
    heir._last_updated = datetime.now() - timedelta(seconds=10)
    assert not heir.is_expired()


@patch.object(MinimalHeir, '_load', Mock())
@patch.object(MinimalHeir, '_prepare_data', Mock())
def test_load():
    heir = MinimalHeir()
    heir.load()
    heir._load.assert_called_once()
    heir._prepare_data.assert_called_once()
    assert datetime.now() - heir._last_updated < timedelta(seconds=3)
