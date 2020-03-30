class Patterns:

    def __init__(self):
        self.country_command = r'^/country_(\S+)$'

    def greeting(self):
        return (
            'Привет, я помогаю отслеживать текущую обстановку '
            'по COVID-19.\n\n'
            'Чтобы получить текущую информацию, введите название страны '
            'или "Мир".\n\n'
            '/rating - рейтинг стран по заболеваемости.'
        )

    def country(self, info):
        return (
            self._country(info)
            + '\n' + self._reload(info)
            + self._go_to_rating()
        )

    def _country(self, info):
        return (
            f"*{info['country']}*\n\n"
            + self._detailed([
                ('Всего подтвержденных случаев', 'total_cases'),
                ('Новые случаи за сутки', 'new_cases'),
                ('Всего погибших', 'total_deaths'),
                ('Погибших за последние сутки', 'new_deaths'),
                ('Выздоровевшие', 'recovered_cases'),
            ], info)
        )

    def world(self, info, rating):
        return (
            self._country(info)
            + '\n\n*Топ 5 стран*\n\n'
            + self.rating(rating)
            + '\n' + self._reload(info)
            + self._go_to_rating()
        )

    def rating(self, rating, world=None):
        pattern = self._in_one_line(rating, code=True)
        if world is not None:
            world_pattern = self._in_one_line(world, bald=True)
            pattern = world_pattern + '\n\n' + pattern
        return pattern

    def error(self, info):
        return (
            info['error'] + '\n'
            + self._go_to_all()
            + self._go_to_rating()
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
        return f'{label}:\n`{info[name]}`'

    @_vectorize
    def _in_one_line(self, info, number=False, code=False, bald=False):
        line = str(info['total_cases'])
        if code:
            line = '`' + line + '`'
        line = line + ' ' + info['country']
        if bald:
            line = '*' + line + '*'
        line += '    -> ' + self._link(info)
        if number:
            line = str(info['number']) + '. ' + line
        # line = line + '\n'
        return line

    def _reload(self, info):
        return f'\n{self._link(info)} - обновить данные'

    def _go_to_rating(self):
        return '\n/rating - рейтинг стран'

    def _go_to_all(self):
        return '\n/all - статистика по миру'

    def _link(self, info):
        if info['key'] == 'all':
            return '/all'
        return '/country\\_' + info['key']
