import httpx
from datetime import timedelta
from typing import List
import pandas as pd

from aggregator.sources import Source
from aggregator.dictionary import CompatibilityDictionary
from .datapreparer import RapidapiDataPreparer
from .schemas import RapidapiCountryInfo
from exceptions import CountryNotFound, NoRapidapiKey


class RapidapiSource(Source):
    def __init__(self, key=None, dictionary=None):
        self._key = key
        self.data = None
        self.last_updated = None
        self.expire_time = timedelta(minutes=10)
        self._dictionary = dictionary
        if self._dictionary is None:
            self._dictionary = CompatibilityDictionary()

    def single_country(self, name='all') -> RapidapiCountryInfo:
        key = self._dictionary.name_to_key(name)
        country: list = self.countries_by_keys(key)
        if len(country) == 0:
            raise CountryNotFound(f'No such country: {country}')
        country: dict = country[0]
        return country

    def countries_by_keys(self, *keys: List[str]) -> List[RapidapiCountryInfo]:
        selected_countries = self.data[self.data.key.isin(keys)]
        country_dicts: list = selected_countries.to_dict(orient='records')
        return country_dicts

    def countries_by_range(self, start=1, end=10) -> List[RapidapiCountryInfo]:
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
        data = RapidapiDataPreparer.prepare(data, self._dictionary)
        return data
