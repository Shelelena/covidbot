from abc import ABC, abstractmethod
import requests
import json
from datetime import datetime, timedelta
import pandas as pd

from exceptions import CountryNotFound, NoRapidapiKey
from .dictionary import Dictionary


class Source(ABC):
    def load(self):
        data = self._load()
        self._data = self._prepare_data(data)
        self._last_updated = datetime.now()

    @abstractmethod
    def _load(self):
        pass

    @abstractmethod
    def _prepare_data(self):
        pass

    def is_expired(self):
        time_since_last_update = datetime.now() - self._last_updated
        return time_since_last_update > self._expire_time


class Rapidapi(Source):
    def __init__(self, key=None):
        self._key = key
        self._data = None
        self._last_updated = None
        self._expire_time = timedelta(minutes=10)
        self._dictionary = Dictionary()

    def _load(self):
        if self._key is None:
            raise NoRapidapiKey
        response = requests.request(
            "GET",
            "https://covid-193.p.rapidapi.com/statistics",
            headers={
                'x-rapidapi-host': "covid-193.p.rapidapi.com",
                'x-rapidapi-key': self._key,
            }
        )
        return response.text

    def _prepare_data(self, data):
        data = json.loads(data)
        data = data['response']
        data = pd.DataFrame(data)
        data = self._unwrap_column(data, 'cases')
        data = self._unwrap_column(data, 'deaths')
        data = data.sort_values('total_cases', ascending=False)
        data = data.reset_index(drop=True)
        data['key'] = data.country.str.lower()
        data['country'] = data.key.map(self._dictionary.key_to_name())
        data['number'] = list(range(len(data)))
        return data

    def _unwrap_column(self, data, colname):
        unwrapped_data = pd.DataFrame(list(data[colname]))
        unwrapped_data.columns = [
            name + '_' + colname
            for name in unwrapped_data.columns
        ]
        data = data.join(unwrapped_data)
        del(data[colname])
        return data

    def get_info(self, country=None):
        if country is None:
            country = 'all'
        country = self._dictionary.name_to_key(country)
        row = self._data[self._data.key == country]
        row = row.to_dict(orient='records')
        if len(row) == 0:
            raise CountryNotFound(f'No such country: {country}')
        row = row[0]
        return row

    def range(self, start=1, end=10):
        range_data = self._data.loc[start: end]
        range_data = range_data.to_dict(orient='records')
        return range_data
