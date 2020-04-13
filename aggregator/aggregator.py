import asyncio
from typing import Union, Dict, List
import httpx
import logging
from pathlib import Path

from .rapidapisource import RapidapiSource
from .rapidapisource.schemas import RapidapiCountryInfo
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

    async def update_periodically(self) -> None:
        while True:
            await self.update()
            await asyncio.sleep(self._update_interval)

    async def update(self) -> None:
        try:
            await self.load_sources()
        except httpx._exceptions.ReadTimeout:
            logging.error('ReadTimeout in source update')
        except httpx._exceptions.ConnectTimeout:
            logging.error('ConnectTimeout in source update')
        except Exception:
            logging.exception('Exception in source update')

    async def load_sources(self) -> None:
        for source in self._sources:
            if source.is_expired():
                await source.update()

    def country(
        self,
        country: str = 'all'
    ) -> Union[RapidapiCountryInfo, Dict[str, str]]:

        try:
            return self._rapidapi.single_country(country)
        except CountryNotFound:
            return {'error': 'Страна не найдена'}

    def rating(
        self,
        start: int = 1,
        end: int = 10
    ) -> List[RapidapiCountryInfo]:

        rating = self._rapidapi.countries_by_range(start, end)
        return rating

    def graph(self, country: str = 'all') -> Union[Path, str, None]:
        try:
            return self._github.graph(country)
        except CountryNotFound:
            return None

    def save_graph_id(self, key: str, id: str) -> None:
        self._github.save_graph_id(key, id)
