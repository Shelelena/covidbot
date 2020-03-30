from .patterns import country_pattern, rating_pattern


def register_handlers(bot, aggregator):

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(
            message.chat.id,
            (
                'Привет, я помогаю отслеживать текущую обстановку '
                'по COVID-19.\n\n'
                'Чтобы получить текущую информацию, введите название страны '
                'или "Мир".\n\n'
                '/rating - рейтинг стран по заболеваемости.'
            )
        )

    @bot.message_handler(commands=['rating'])
    def get_rating(message):
        world = aggregator.get('all')
        rating = aggregator.rating(1, 10)
        bot.send_message(
            message.chat.id,
            rating_pattern(world, rating),
            parse_mode="Markdown"
        )

    @bot.message_handler(content_types=['text'])
    def return_country_statistics(message):
        info = aggregator.get(message.text)
        if 'error' in info:
            bot.send_message(message.chat.id, str(info['error']))
            return
        bot.send_message(
            message.chat.id,
            country_pattern(info),
            parse_mode="Markdown"
        )
