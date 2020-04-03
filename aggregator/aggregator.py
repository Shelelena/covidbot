import asyncio
from .rapidapisource import RapidapiSource
from exceptions import CountryNotFound
from .dictionary import Dictionary


class Aggregator:
    def __init__(self, rapidapi_key=None):
        self._rapidapi = RapidapiSource(rapidapi_key)
        self._sources = [self._rapidapi]
        self._dictionary = Dictionary()

    async def update(self):
        while True:
            await self.load_sources()
            await asyncio.sleep(60)

    async def load_sources(self):
        for source in self._sources:
            if source.is_expired():
                await source.update()

    def country(self, country='all'):
        return self._combine_country_data(country)

    def rating(self, start=1, end=10):
        return self._combine_rating_data(start, end)

    def _combine_country_data(self, country='all'):
        try:
            current_info = self._rapidapi.single_country(country)
        except CountryNotFound:
            current_info = {'error': 'Страна не найдена'}
        return current_info

    def _combine_rating_data(self, start=1, end=10):
        rating = self._rapidapi.countries_by_range(start, end)
        return rating
