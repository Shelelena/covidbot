import logging


def log(coroutine):
    exceptions = [206980992]

    async def wrapped(query, *args, **kwargs):
        del(kwargs['state'])
        del(kwargs['raw_state'])

        text = None
        message = None
        if hasattr(query, 'text'):
            text = query.text
            message = query
        elif hasattr(query, 'message'):
            text = query.data
            message = query.message

        if text is None and message is None:
            logging.warning(f'Very strange query: {str(query)}')

        elif message.chat.id not in exceptions:
            if text == '/start':
                logging.info('!new greeting!')
            logging.info(
                f'chat_id: {message.chat.id}, '
                f'query: {str(text)}, '
                f'first_name: {str(query["from"].first_name)}, '
                f'username: {str(query["from"].username)}, '
                f'is_bot: {str(query["from"].is_bot)}, '
            )

        return await coroutine(query, *args, **kwargs)
    return wrapped
