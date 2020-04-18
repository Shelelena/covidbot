from typing import Tuple, List, Optional
from aggregator import CountryInfo

from config import MY_TELEGRAM_USERNAME


class Patterns:

    def __init__(self):
        self.country_command = r'^/c_(\S+)$'

    def _link(self, info: CountryInfo) -> str:
        if info['key'] == 'all':
            return '/all'
        return '/c\\_' + str(info['key'])

    def greeting(self) -> str:
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

    def help(self) -> str:
        return (
            '/all - статистика по миру\n'
            '/rating - рейтинг стран по заболеваемости\n'
            '/c_russia - статистика по России\n'
            '/help - эта справка\n\n'
            'Чтобы получить текущую информацию по любой стране, введите '
            'название страны. Для получения информации по миру, введите '
            '"мир" или "все".\n\n'
            'Источники данных: https://rapidapi.com/api-sports/api/covid-193, '
            'https://github.com/CSSEGISandData/COVID-19. '
            'Данные обновляются раз в 15 минут.\n'
            'Баг репорт - ' + MY_TELEGRAM_USERNAME
        )

    def country(self, info: CountryInfo) -> str:
        return (
            self._country_details(info)
            + '\n' + self._reload(info)
            + self._go_to_all()
            + self._go_to_rating()
        )

    def _country_details(self, info: CountryInfo) -> str:
        return (
            f"*{info['name']}*\n\n"
            + self._detailed([
                ('Всего подтвержденных случаев', 'total_cases'),
                ('Новые случаи за сегодня', 'new_cases'),
                ('Всего погибших', 'total_deaths'),
                ('Погибшие за сегодня', 'new_deaths'),
                ('Выздоровевшие', 'recovered_cases'),
            ], info)
        )

    def world(
        self,
        info: CountryInfo,
        rating: List[CountryInfo],
    ) -> str:

        return (
            self._country_details(info)
            + '\n\n*Топ 5 стран*\n\n'
            + self.rating(rating)
            + '\n' + self._reload(info)
            + self._go_to_rating()
        )

    def rating(
        self,
        rating: List[CountryInfo],
        world: Optional[CountryInfo] = None,
    ) -> str:

        pattern = self._in_one_line(rating, number=True)
        if world is not None:
            world_pattern = self._in_one_line(world, bald=True)
            pattern = world_pattern + '\n\n' + pattern
        return pattern

    def error(self, info: CountryInfo) -> str:
        return (
            info['error'] + '\n'
            + self._go_to_all()
            + self._go_to_rating()
            + self._go_to_help()
        )

    def _vectorize(function):
        def wrapped(self, argument, *args, **kwargs) -> str:
            if type(argument) == list:
                return '\n'.join(
                    [function(self, i, *args, **kwargs) for i in argument]
                )
            else:
                return function(self, argument, *args, **kwargs)
        return wrapped

    @_vectorize
    def _detailed(
        self,
        format: Tuple[str, str],
        info: CountryInfo
    ) -> str:

        label, name = format
        data = info[name]
        if data is None:
            data = 'Нет'
        if type(data) == float:
            data = int(data)
        if type(data) == str and data.lstrip('+').isnumeric():
            data = int(data.lstrip('+'))
        if type(data) == int:
            data = self._with_delimiter(data)
        return f'{label}:\n{data}'

    @_vectorize
    def _in_one_line(
        self,
        info: CountryInfo,
        number: bool = False,
        bald: bool = False,
    ) -> str:

        line = self._with_delimiter(int(info['total_cases']))
        line = line + '  ' + str(info['name'])
        if bald:
            line = '*' + line + '*'
        line += '    -> ' + self._link(info)
        if number:
            line = '`' + str(info['number']) + '.`  ' + line
        return line

    def _with_delimiter(self, value: int) -> str:
        return '{:,}'.format(value).replace(',', ' ')

    def _reload(self, info: CountryInfo) -> str:
        return f'\n{self._link(info)} - обновить данные'

    def _go_to_rating(self) -> str:
        return '\n/rating - рейтинг стран'

    def _go_to_all(self) -> str:
        return '\n/all - статистика по миру'

    def _go_to_russia(self) -> str:
        return '\n/c_russia - статистика по России'

    def _go_to_help(self) -> str:
        return '\n/help - справка'
