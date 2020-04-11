import asyncio
import httpx
import logging
from .rapidapisource import RapidapiSource
from .githubsource import GithubSource
from exceptions import CountryNotFound
from .dictionary import CompatibilityDictionary


class Aggregator:
    def __init__(self, rapidapi_key=None):
        dictionary = CompatibilityDictionary()
        self._rapidapi = RapidapiSource(rapidapi_key, dictionary)
        self._github = GithubSource(dictionary)
        self._sources = [self._rapidapi, self._github]
        self._update_interval = 60

    async def update_periodically(self):
        while True:
            try:
                await self.load_sources()
            except httpx._exceptions.ReadTimeout:
                logging.error('ReadTimeout in source update')
            except httpx._exceptions.ConnectTimeout:
                logging.error('ConnectTimeout in source update')
            except Exception:
                logging.exception('Exception in source update')
            await asyncio.sleep(self._update_interval)

    async def load_sources(self):
        for source in self._sources:
            if source.is_expired():
                await source.update()

    def country(self, country='all'):
        try:
            return self._rapidapi.single_country(country)
        except CountryNotFound:
            return {'error': 'Страна не найдена'}

    def rating(self, start=1, end=10):
        rating = self._rapidapi.countries_by_range(start, end)
        return rating

    def graph(self, country='all'):
        try:
            return self._github.graph(country)
        except CountryNotFound:
            return None

    def save_graph_id(self, key, id):
        self._github.save_graph_id(key, id)
