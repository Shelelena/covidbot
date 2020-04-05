class Patterns:

    def __init__(self):
        self.country_command = r'^/c_(\S+)$'

    def _link(self, info):
        if info['key'] == 'all':
            return '/all'
        return '/c\\_' + str(info['key'])

    def greeting(self):
        return (
            'Привет, я помогаю отслеживать обстановку '
            'по COVID-19.\n\n'
            'Чтобы получить текущую информацию, введите название страны.\n\n'
            'Либо можно нажимать на ссылки:\n'
            + self._go_to_all()
            + self._go_to_russia()
            + self._go_to_rating()
            + self._go_to_help()
        )

    def help(self):
        return (
            '/all - статистика по миру\n'
            '/rating - рейтинг стран по заболеваемости\n'
            '/c_russia - статистика по России\n'
            '/help - эта справка\n\n'
            'Чтобы получить текущую информацию по любой стране, введите '
            'название страны. Для получения информации по миру, введите '
            '"мир" или "все".\n\n'
            'Источник данных - https://rapidapi.com/api-sports/api/covid-193. '
            'Данные обновляются раз в 15 минут.\n'
            'Баг репорт - @shel_elena'
        )

    def country(self, info):
        return (
            self._country_details(info)
            + '\n' + self._reload(info)
            + self._go_to_all()
            + self._go_to_rating()
        )

    def _country_details(self, info):
        return (
            f"*{info['country']}*\n\n"
            + self._detailed([
                ('Всего подтвержденных случаев', 'total_cases'),
                ('Новые случаи за сегодня', 'new_cases'),
                ('Всего погибших', 'total_deaths'),
                ('Погибших за сегодня', 'new_deaths'),
                ('Выздоровевшие', 'recovered_cases'),
            ], info)
        )

    def world(self, info, rating):
        return (
            self._country_details(info)
            + '\n\n*Топ 5 стран*\n\n'
            + self.rating(rating)
            + '\n' + self._reload(info)
            + self._go_to_rating()
        )

    def rating(self, rating, world=None):
        pattern = self._in_one_line(rating, code=True, number=True)
        if world is not None:
            world_pattern = self._in_one_line(world, bald=True)
            pattern = world_pattern + '\n\n' + pattern
        return pattern

    def error(self, info):
        return (
            info['error'] + '\n'
            + self._go_to_all()
            + self._go_to_rating()
            + self._go_to_help()
        )

    def _vectorize(function):
        def wrapped(self, argument, *args, **kwargs):
            if type(argument) == list:
                return '\n'.join(
                    [function(self, i, *args, **kwargs)for i in argument]
                )
            else:
                return function(self, argument, *args, **kwargs)
        return wrapped

    @_vectorize
    def _detailed(self, format, info):
        label, name = format
        data = info[name]
        if data is None:
            data = 'Нет'
        return f'{label}:\n`{data}`'

    @_vectorize
    def _in_one_line(self, info, number=False, code=False, bald=False):
        line = str(info['total_cases'])
        if code:
            line = '`' + line + '`'
        line = line + ' ' + str(info['country'])
        if bald:
            line = '*' + line + '*'
        line += '    -> ' + self._link(info)
        if number:
            line = str(info['number']) + '. ' + line
        return line

    def _reload(self, info):
        return f'\n{self._link(info)} - обновить данные'

    def _go_to_rating(self):
        return '\n/rating - рейтинг стран'

    def _go_to_all(self):
        return '\n/all - статистика по миру'

    def _go_to_russia(self):
        return '\n/c_russia - статистика по России'

    def _go_to_help(self):
        return '\n/help - справка'
