from .patterns import country_pattern, rating_pattern


class Communicator:
    def __init__(self, bot, aggregator):
        self.bot = bot
        self.aggregator = aggregator

    def run_bot(self):
        self.bot.polling(none_stop=True)

    def send_greeting(self, chat_id):
        self.bot.send_message(
            chat_id,
            (
                'Привет, я помогаю отслеживать текущую обстановку '
                'по COVID-19.\n\n'
                'Чтобы получить текущую информацию, введите название страны '
                'или "Мир".\n\n'
                '/rating - рейтинг стран по заболеваемости.'
            )
        )

    def send_country_statistics(self, chat_id, country):
        info = self.aggregator.get(country)
        if 'error' in info:
            self.bot.send_message(chat_id, str(info['error']))
            return
        self.bot.send_message(
            chat_id,
            country_pattern(info),
            parse_mode="Markdown"
        )

    def send_rating(self, chat_id):
        world = self.aggregator.get('all')
        rating = self.aggregator.rating(1, 10)
        self.bot.send_message(
            chat_id,
            rating_pattern(world, rating),
            parse_mode="Markdown"
        )
