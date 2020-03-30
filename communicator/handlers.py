def register_handlers(communicator):
    bot = communicator.bot

    @bot.message_handler(commands=['start'])
    def greeting(message):
        communicator.send_greeting(
            message.chat.id
        )

    @bot.message_handler(commands=['rating'])
    def rating(message):
        communicator.send_rating(
            message.chat.id
        )

    @bot.message_handler(content_types=['text'])
    def country_statistics(message):
        communicator.send_country_statistics(
            message.chat.id,
            country=message.text
        )
