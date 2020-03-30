from pytest import fixture
from unittest.mock import MagicMock
from communicator import Communicator


@fixture
def comm():
    communicator = Communicator(bot=MagicMock(), aggregator=MagicMock())
    communicator.patterns = MagicMock()
    return communicator


def test_greeting(comm):
    comm.send_greeting('chat_id_1')

    comm.patterns.greeting.assert_called_once()
    comm.bot.send_message.assert_called_once_with(
        'chat_id_1', comm.patterns.greeting())


def test_country_statistics(comm):
    comm.send_country_statistics('chat_id_2', 'country_1')

    comm.aggregator.get.assert_called_once_with('country_1')
    comm.patterns.country.assert_called_once_with(
        comm.aggregator.get())
    comm.bot.send_message.assert_called_once_with(
        'chat_id_2', comm.patterns.country(), parse_mode="Markdown")


def test_world_statistics(comm):
    comm.aggregator.get.return_value = {'key': 'all'}
    comm.send_country_statistics('chat_id_5', 'country_3')

    comm.aggregator.rating.assert_called_once_with(1, 5)
    comm.patterns.world.assert_called_once_with(
        comm.aggregator.get(), comm.aggregator.rating())
    comm.bot.send_message.assert_called_once_with(
        'chat_id_5', comm.patterns.world(), parse_mode="Markdown")


def test_country_statistics_with_error(comm):
    comm.aggregator.get.return_value = {'error': 'error_msg'}
    comm.send_country_statistics('chat_id_3', 'country_2')

    comm.patterns.error.assert_called_once_with(
        comm.aggregator.get())
    comm.bot.send_message.assert_called_once_with(
        'chat_id_3', comm.patterns.error())


def test_rating_message(comm):
    comm.send_rating('chat_id_4')

    comm.aggregator.get.assert_called_once_with('all')
    comm.aggregator.rating.assert_called_once_with(1, 20)
    comm.patterns.rating.assert_called_once_with(
        comm.aggregator.rating(), comm.aggregator.get())
    comm.bot.send_message.assert_called_once_with(
        'chat_id_4', comm.patterns.rating(), parse_mode="Markdown")
