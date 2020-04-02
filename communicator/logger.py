import logging
from datetime import datetime


def log(function):
    exceptions = [206980992]

    def wrapped(query):
        if hasattr(query, 'text'):
            text = query.text
            chat_id = query.chat.id
        elif hasattr(query, 'message'):
            text = query.data
            chat_id = query.message.chat.id

        if chat_id in exceptions:
            return function(query)

        if text == '/start':
            logging.info(' !new greeting!')
        logging.info(
            f' query: {text}, '
            f'chat_id: {chat_id}, '
            f'{str(datetime.now())}'
        )
        return function(query)
    return wrapped
