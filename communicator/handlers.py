from .logger import log


def register_handlers(communicator, dispatcher):
    dp = dispatcher

    @dp.message_handler(commands=[
        'start', 'help', 'all', 'russia', 'rating', 'countries', 'regions'])
    @log
    async def handle_commands(message, command):
        if command.command == 'start':
            await communicator.send_greeting(message)

        elif command.command == 'help':
            await communicator.send_help(message)

        elif command.command == 'all':
            await communicator.send_country(message, 'all')

        elif command.command == 'russia':
            await communicator.send_country(message, 'russia')

        elif (command.command == 'countries'
                or command.command == 'rating'):
            await communicator.send_rating(message, parent='all')

        elif command.command == 'regions':
            await communicator.send_rating(message, parent='russia')

    @dp.message_handler(regexp=communicator.patterns.country_command)
    @log
    async def handle_country_links(message, regexp):
        country = regexp.group(1)
        await communicator.send_country(
            message,
            country
        )

    @dp.message_handler(content_types=['text'])
    @log
    async def handle_messages(message):
        await communicator.send_country(
            message,
            country=message.text
        )

    @dp.callback_query_handler(communicator.keyboard.callback.filter())
    @log
    async def turn_rating_page(query, callback_data):
        await communicator.turn_rating_page(
            query=query,
            callback=callback_data,
        )
