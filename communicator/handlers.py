from .logger import log


def register_handlers(communicator, dispatcher):
    dp = dispatcher

    @dp.message_handler(commands=['start', 'help', 'all', 'rating'])
    @log
    async def handle_commands(message, command):
        if command.command == 'start':
            await communicator.send_greeting(message)

        elif command.command == 'help':
            await communicator.send_help(message)

        elif command.command == 'all':
            await communicator.send_country(message, 'all')

        elif command.command == 'rating':
            await communicator.send_rating(message)

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
        if message.text.lower() in ('rating', 'рейтинг'):
            await communicator.send_rating(message)
        else:
            await communicator.send_country(
                message,
                country=message.text
            )

    @dp.callback_query_handler(communicator.keyboard.callback.filter())
    @log
    async def turn_rating_page(query, callback_data):
        await communicator.turn_rating_page(
            query=query,
            page=callback_data['page']
        )
