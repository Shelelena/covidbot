from typing import List
import httpx
from datetime import timedelta, datetime
import pandas as pd

from aggregator.sources import Source
from aggregator.matcher import CountryNameMatcher
from .datapreparer import RapidapiDataPreparer
from aggregator.schemas import CountryInfo
from exceptions import CountryNotFound, NoRapidapiKey


class RapidapiSource(Source):
    def __init__(
        self,
        key: str = None,
        matcher: CountryNameMatcher = None
    ):
        self._key: str = key
        self.data: pd.DataFrame = None
        self.last_updated: datetime = None
        self.expire_time = timedelta(minutes=10)

        self._matcher = matcher
        if self._matcher is None:
            self._matcher = CountryNameMatcher()

    def single_country(self, name='all') -> CountryInfo:
        key = self._matcher.name_to_key(name)
        country: list = self.countries_by_keys(key)
        if len(country) == 0:
            raise CountryNotFound(f'No such country: {country}')
        country: dict = country[0]
        return country

    def countries_by_keys(self, *keys: List[str]) -> List[CountryInfo]:
        selected_countries = self.data[self.data.key.isin(keys)]
        country_dicts: list = selected_countries.to_dict(orient='records')
        return country_dicts

    def countries_by_range(self, start=1, end=10) -> List[CountryInfo]:
        range_data = self.data.loc[start:end]
        range_data = range_data.to_dict(orient='records')
        return range_data

    async def load_data(self) -> str:
        if self._key is None:
            raise NoRapidapiKey

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://covid-193.p.rapidapi.com/statistics",
                headers={
                    'x-rapidapi-host': "covid-193.p.rapidapi.com",
                    'x-rapidapi-key': self._key,
                }
            )
        return response.text

    def prepare_data(self, data: str) -> pd.DataFrame:
        data = RapidapiDataPreparer.prepare(data, self._matcher)
        return data
