import httpx
import json
from datetime import timedelta
import pandas as pd
import logging

from .sources import Source
from exceptions import CountryNotFound, NoRapidapiKey
from .dictionary import Dictionary


class RapidapiSource(Source):
    def __init__(self, key=None):
        self._key = key
        self.data = None
        self.last_updated = None
        self.expire_time = timedelta(minutes=10)
        self._dictionary = Dictionary()

    def single_country(self, name='all'):
        key = self._dictionary.name_to_key(name)
        country: list = self.countries_by_keys(key)
        if len(country) == 0:
            raise CountryNotFound(f'No such country: {country}')
        country: dict = country[0]
        return country

    def countries_by_keys(self, *keys) -> list:
        selected_countries = self.data[self.data.key.isin(keys)]
        country_dicts: list = selected_countries.to_dict(orient='records')
        return country_dicts

    def countries_by_range(self, start=1, end=10):
        range_data = self.data.loc[start: end]
        range_data = range_data.to_dict(orient='records')
        return range_data

    async def load_data(self):
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
        data = self._json_to_dataframe(data)
        data = self._unwrap_columns(data)
        data = self._set_country_keys_and_names(data)
        data = self._sort_and_enumerate(data)
        self._check_new_countries
        return data

    def _json_to_dataframe(self, data: str) -> pd.DataFrame:
        data = json.loads(data)
        data = data['response']
        data = pd.DataFrame(data)
        return data

    def _unwrap_columns(self, data):
        for colname in ('cases', 'deaths'):
            data = self._unwrap_dict_column(data, colname)
        return data

    def _unwrap_dict_column(self, data, colname: str):
        unwrapped_data = pd.DataFrame(list(data[colname]))
        unwrapped_data.columns = [
            name + '_' + colname
            for name in unwrapped_data.columns
        ]
        data = data.join(unwrapped_data)
        del(data[colname])
        return data

    def _set_country_keys_and_names(self, data):
        data['key'] = data.country.str.lower()
        data.key = data.key.str.replace(r'[\.\-\&\;]', '')
        data.key = data.key.map(self._dictionary.name_to_key())
        data = data.drop_duplicates(subset=['key'])
        data.country = data.key.map(self._dictionary.key_to_name())
        return data

    def _sort_and_enumerate(self, data):
        data = data.sort_values('total_cases', ascending=False)
        data = data.reset_index(drop=True)
        data['number'] = list(range(len(data)))
        return data

    def _check_new_countries(self, data):
        new_countries = set(data.key)
        old_countries = set(self._dictionary.key_to_name())
        difference = new_countries - old_countries
        if len(difference) > 0:
            logging.warning(
                f' New countries: {str(difference)}')
