import pytest
from unittest.mock import MagicMock, AsyncMock

from communicator import Communicator


@pytest.fixture
def comm():
    communicator = Communicator(aggregator=MagicMock())
    communicator.patterns = MagicMock()
    communicator.keyboard = MagicMock()
    return communicator


@pytest.mark.asyncio
async def test_greeting(comm):
    message = AsyncMock()
    await comm.send_greeting(message)

    comm.patterns.greeting.assert_called_once()
    message.answer.assert_called_once_with(comm.patterns.greeting())


@pytest.mark.asyncio
async def test_help(comm):
    message = AsyncMock()
    await comm.send_help(message)

    comm.patterns.help.assert_called_once()
    message.answer.assert_called_once_with(
        comm.patterns.help(),
        disable_web_page_preview=True)


@pytest.mark.asyncio
async def test_country(comm):
    message = AsyncMock()
    await comm.send_country(message, 'country_1')

    comm.aggregator.country.assert_called_once_with('country_1')
    info = comm.aggregator.country()

    comm.aggregator.rating.assert_called_once_with(1, 5, parent=info['key'])
    comm.aggregator.graph.assert_called_once_with('country_1')
    comm.patterns.country.assert_called_once_with(
        comm.aggregator.country(), comm.aggregator.rating())
    message.answer_photo.assert_called_once_with(
        photo=comm.aggregator.graph(),
        caption=comm.patterns.country(),
        parse_mode="Markdown",
        reply_markup=None)


@pytest.mark.asyncio
async def test_country_with_no_graph(comm):
    comm.aggregator.graph.return_value = None
    message = AsyncMock()
    await comm.send_country(message, 'country_5')

    message.answer.assert_called_once_with(
        text=comm.patterns.country(),
        parse_mode="Markdown",
        reply_markup=None)


@pytest.mark.asyncio
async def test_country_with_graph_sent_first_time(comm, tmp_path):
    (tmp_path / 'file.png').touch()
    comm.aggregator.graph.return_valtmp_path / 'file.png'
    comm.aggregator.graph.return_value = tmp_path / 'file.png'
    message = AsyncMock()
    await comm.send_country(message, 'country_5')

    comm.aggregator.save_graph_id.assert_called_once()


@pytest.mark.asyncio
async def test_country_statistics_with_error(comm):
    comm.aggregator.country.return_value = {'error': 'error_msg'}
    message = AsyncMock()
    await comm.send_country(message, 'country_2')

    comm.patterns.error.assert_called_once_with(
        comm.aggregator.country())
    message.answer.assert_called_once_with(comm.patterns.error())


@pytest.mark.asyncio
async def test_rating_message(comm):
    message = AsyncMock()
    await comm.send_rating(message, parent='russia')

    comm.aggregator.country.assert_called_once_with('russia')
    comm.aggregator.rating.assert_called_once_with(1, 20, parent='russia')
    comm.aggregator.rating_length.assert_called_once_with('russia')
    comm.patterns.rating.assert_called_once_with(
        comm.aggregator.rating(), comm.aggregator.country())

    rating_length = comm.aggregator.rating_length()
    comm.keyboard.create.assert_called_once_with(
        current_page=1,
        max_pages=-(-rating_length//comm._max_countries_on_rating_page),
        parent='russia'
    )

    message.answer.assert_called_once_with(
        comm.patterns.rating(),
        parse_mode="Markdown",
        reply_markup=comm.keyboard.create()
    )


@pytest.mark.asyncio
async def test_rating_turn_page(comm):
    query = AsyncMock()
    await comm.turn_rating_page(
        query,
        callback=dict(page='3', max_pages='10', parent='all')
    )

    comm.aggregator.country.assert_called_once_with('all')
    comm.aggregator.rating.assert_called_once_with(41, 60, parent='all')
    comm.patterns.rating.assert_called_once_with(
        comm.aggregator.rating(), comm.aggregator.country())
    comm.keyboard.create.assert_called_once_with(3, 10, 'all')
    query.message.edit_text.assert_called_once_with(
        text=comm.patterns.rating(),
        parse_mode="Markdown",
        reply_markup=comm.keyboard.create()
    )

    assert not comm.aggregator.rating_length.called
