class Patterns:

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
            f"*{info['country']}*\n\n"
            f"Всего: {info['total_cases']}\n"
            f"Новые случаи: {info['new_cases']}\n"
            f"Погибшие: {info['total_deaths']}\n"
            f"Выздоровевшие: {info['recovered_cases']}"
        )

    def rating(self, rating, world):
        pattern = self._short_line(rating, number=True)
        pattern = '\n'.join(pattern)
        if world is not None:
            world_pattern = self._short_line(world, bald=True)
            pattern = world_pattern + '\n\n' + pattern
        return pattern

    def _vectorize(function):
        def wrapped(self, argument, *args, **kwargs):
            if type(argument) == list:
                return [function(self, i, *args, **kwargs) for i in argument]
            else:
                return function(self, argument, *args, **kwargs)
        return wrapped

    @_vectorize
    def _short_line(self, info, number=False, bald=False):
        line = info['country'] + ': ' + str(info['total_cases'])
        if bald:
            line = '*' + line + '*'
        line += '\n' + self._link(info)
        if number:
            line = str(info['number']) + '. ' + line
        return line

    def _link(self, info):
        return '/country\\_' + info['key']
