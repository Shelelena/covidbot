from .patterns import Patterns


class Communicator:
    def __init__(self, bot, aggregator):
        self.bot = bot
        self.aggregator = aggregator
        self.patterns = Patterns()

    def run_bot(self):
        self.bot.polling(none_stop=True)

    def send_greeting(self, chat_id):
        self.bot.send_message(
            chat_id,
            self.patterns.greeting()
        )

    def send_country_statistics(self, chat_id, country):
        info = self.aggregator.get(country)
        if 'error' in info:
            self.bot.send_message(chat_id, str(info['error']))
            return
        self.bot.send_message(
            chat_id,
            self.patterns.country(info),
            parse_mode="Markdown"
        )

    def send_rating(self, chat_id):
        world = self.aggregator.get('all')
        rating = self.aggregator.rating(1, 20)
        self.bot.send_message(
            chat_id,
            self.patterns.rating(rating, world),
            parse_mode="Markdown"
        )
