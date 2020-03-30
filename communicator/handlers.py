import re


def register_handlers(communicator):
    bot = communicator.bot

    @bot.message_handler(commands=['start'])
    def greeting(message):
        communicator.send_greeting(
            message.chat.id
        )

    @bot.message_handler(commands=['all'])
    def world(message):
        communicator.send_country_statistics(
            message.chat.id, 'all'
        )

    @bot.message_handler(commands=['rating'])
    def rating(message):
        communicator.send_rating(
            message.chat.id
        )

    @bot.message_handler(regexp=communicator.patterns.country_command)
    def country_link(message):
        pattern = communicator.patterns.country_command
        country = re.search(pattern, message.text).group(1)
        communicator.send_country_statistics(
            message.chat.id,
            country=country
        )

    @bot.message_handler(content_types=['text'])
    def country_statistics(message):
        communicator.send_country_statistics(
            message.chat.id,
            country=message.text
        )
