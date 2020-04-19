from typing import Tuple, List, Optional, Union
from aggregator import CountryInfo, RegionInfo

from config import MY_TELEGRAM_USERNAME


class Patterns:

    CountryOrRegionInfo = Union[CountryInfo, RegionInfo]

    def __init__(self):
        self.country_command = r'^/[[cr]_(\S+)$'

    def _link(self, info: CountryOrRegionInfo) -> str:
        if info['key'] == 'all':
            return '/all'
        if info['key'] == 'russia':
            return '/russia'
        literal = info['type'][0]
        return '/' + literal + '\\_' + str(info['key'])

    def greeting(self) -> str:
        return (
            'Привет, я помогаю отслеживать обстановку '
            'по COVID-19.\n\n'
            'Чтобы получить текущую информацию, введите название страны '
            'или региона России.\n\n'
            'Либо можно нажимать на ссылки:\n'
            + self._go_to_all()
            + self._go_to_russia()
            + self._go_to_country_rating()
            + self._go_to_region_rating()
            + '\n'
            + self._go_to_help()
        )

    def help(self) -> str:
        return (
            '/all - статистика по миру\n'
            '/russia - статистика по России\n'
            '/countries - рейтинг стран по заболеваемости\n'
            '/regions - рейтинг регионов России\n'
            '/help - эта справка\n\n'
            'Чтобы получить текущую информацию по cтране или региону России, '
            'введите название. Для получения информации по миру, введите '
            '"мир" или "все".\n\n'
            'Источники данных: https://rapidapi.com/api-sports/api/covid-193, '
            'https://github.com/CSSEGISandData/COVID-19, '
            'https://стопкоронавирус.рф/.\n\n'
            'Баг репорт - ' + MY_TELEGRAM_USERNAME
        )

    def country(
        self,
        info: CountryOrRegionInfo,
        subrating: List[CountryOrRegionInfo] = None
    ) -> str:

        if info['type'] == 'country':
            pattern = self._country_details(info)
        elif info['type'] == 'region':
            pattern = self._region_details(info)

        if subrating:
            pattern += f'\n\n*Топ {len(subrating)}*\n\n'
            pattern += self.rating(subrating, links=False)
        pattern += self._navigation_links(info)
        return pattern

    def rating(
        self,
        rating: List[CountryOrRegionInfo],
        world: Optional[CountryOrRegionInfo] = None,
        links: bool = True
    ) -> str:

        pattern = self._in_one_line(rating, number=True)
        if world is not None:
            world_pattern = self._in_one_line(world, bald=True, link=False)
            pattern = world_pattern + '\n\n' + pattern
        if links:
            pattern += self._navigation_links()
        return pattern

    def error(self, info: dict) -> str:
        return (
            info['error'] + '\n'
            + self._go_to_all()
            + self._go_to_russia()
            + self._go_to_country_rating()
            + self._go_to_region_rating()
            + '\n'
            + self._go_to_help()
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

    def _region_details(self, info: RegionInfo) -> str:
        return (
            f"*{info['name']}*\n\n"
            + self._detailed([
                ('Подтвержденные случаи', 'total_cases'),
                ('Погибшие', 'total_deaths'),
                ('Выздоровевшие', 'recovered_cases'),
            ], info)
        )

    def _vectorize(function):
        def wrapped(self, argument, *args, **kwargs) -> str:
            if type(argument) == list:
                result = [function(self, i, *args, **kwargs) for i in argument]
                result = list(filter(lambda i: i is not None, result))
                return '\n'.join(result)
            else:
                return function(self, argument, *args, **kwargs)
        return wrapped

    @_vectorize
    def _detailed(
        self,
        format: Tuple[str, str],
        info: CountryOrRegionInfo
    ) -> str:

        label, name = format
        if name not in info:
            return None

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
        info: CountryOrRegionInfo,
        number: bool = False,
        bald: bool = False,
        link: bool = True,
    ) -> str:

        line = self._with_delimiter(int(info['total_cases']))
        line = line + '  ' + str(info['name'])
        if bald:
            line = '*' + line + '*'
        if link:
            line += '    -> ' + self._link(info)
        if number:
            line = '`' + str(info['number']) + '.`  ' + line
        return line

    def _with_delimiter(self, value: int) -> str:
        return '{:,}'.format(value).replace(',', ' ')

    def _navigation_links(self, info: CountryOrRegionInfo = None):
        if info is None:
            return '\n' + self._go_to_all() + self._go_to_russia()

        links = '\n' + self._reload(info) + '\n'
        if info['key'] != 'all':
            links += self._go_to_all()
        if info['key'] != 'russia':
            links += self._go_to_russia()
        links += self._go_to_country_rating()
        links += self._go_to_region_rating()
        return links

    def _reload(self, info: CountryOrRegionInfo) -> str:
        return f'\n{self._link(info)} - обновить данные'

    def _go_to_country_rating(self) -> str:
        return '\n/countries - рейтинг стран'

    def _go_to_region_rating(self) -> str:
        return '\n/regions - рейтинг регионов России'

    def _go_to_all(self) -> str:
        return '\n/all - статистика по миру'

    def _go_to_russia(self) -> str:
        return '\n/russia - статистика по России'

    def _go_to_help(self) -> str:
        return '\n/help - справка'
