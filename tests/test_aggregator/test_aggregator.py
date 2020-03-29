from unittest.mock import patch, MagicMock

from aggregator import Aggregator
from aggregator.sources import Rapidapi
from mocks import mock_load


@patch.object(Rapidapi, '_load', mock_load)
def test_aggregator_case():
    aggr = Aggregator()
    data = aggr.get('France')
    assert data == {
            'Country': 'France',
            'Total cases': 32964,
        }


@patch.object(Rapidapi, 'is_expired', MagicMock())
@patch.object(Rapidapi, 'load', MagicMock())
@patch.object(Rapidapi, 'get_info', MagicMock())
def test_aggregator_calls():
    aggr = Aggregator()

    aggr._rapidapi.is_expired.return_value = False
    aggr.get('Germany')
    aggr.get('USA')

    aggr._rapidapi.is_expired.return_value = True
    aggr.get('Italy')

    assert aggr._rapidapi.is_expired.call_count == 3
    assert aggr._rapidapi.load.call_count == 2
    assert aggr._rapidapi.get_info.call_count == 3
