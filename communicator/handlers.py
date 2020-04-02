import re
from .logger import log


def register_handlers(communicator):
    bot = communicator.bot

    @bot.message_handler(commands=['start'])
    @log
    def greeting(message):
        communicator.send_greeting(
            message.chat.id
        )

    @bot.message_handler(commands=['help'])
    @log
    def help(message):
        communicator.send_help(
            message.chat.id
        )

    @bot.message_handler(commands=['all'])
    @log
    def world(message):
        communicator.send_country(
            message.chat.id, 'all'
        )

    @bot.message_handler(commands=['rating'])
    @log
    def rating(message):
        communicator.send_rating(
            message.chat.id
        )

    @bot.callback_query_handler(func=lambda call: True)
    @log
    def turn_rating_page(call):
        communicator.turn_rating_page(
            call_id=call.id,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            page_id=call.data
        )

    @bot.message_handler(regexp=communicator.patterns.country_command)
    @log
    def country_link(message):
        pattern = communicator.patterns.country_command
        country = re.search(pattern, message.text).group(1)
        communicator.send_country(
            message.chat.id,
            country=country
        )

    @bot.message_handler(content_types=['text'])
    @log
    def country_statistics(message):
        communicator.send_country(
            message.chat.id,
            country=message.text
        )
