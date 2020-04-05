import httpx
import io
import pandas as pd
from datetime import timedelta

from .sources import Source
from .dictionary import CompatibilityDictionary


class GithubSource(Source):
    def __init__(self, dictionary=None):
        self.data = None
        self.last_updated = None
        self.expire_time = timedelta(hours=3)
        self._dictionary = dictionary
        if self._dictionary is None:
            self._dictionary = CompatibilityDictionary()

    async def load_data(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://raw.githubusercontent.com/CSSEGISandData/COVID-19"
                "/master/csse_covid_19_data/csse_covid_19_time_series"
                "/time_series_covid19_confirmed_global.csv")
        return response.text

    def prepare_data(self, data):
        data = self._csv_to_dataframe(data)
        data = self._transform_keys(data)
        data = self._select_columns(data)
        data = self._make_compatible(data)
        data = self._summarize_countries(data)
        return data

    def _csv_to_dataframe(self, data):
        data = io.StringIO(data)
        data = pd.read_csv(data)
        return data

    def _transform_keys(self, data):
        data = data.copy()
        data['country'] = data['Country/Region'].str.lower()
        data.country = data.country.str.replace(r"[ \(\)\*\'\.\,\-\&\;]", '')
        data.country = data.country.map(self._dictionary.name_to_key())
        data['state'] = data['Province/State'].str.lower()
        data.state = data.state.str.replace(r"[ \(\)\*\'\.\,\-\&\;]", '')
        data.state = data.state.map(self._dictionary.name_to_key())
        return data

    def _select_columns(self, data):
        days_data = data.filter(regex=r'^\d+/\d+/\d+$')
        days_data = days_data[days_data.columns[-60:]]
        days_data['country'] = data.country
        days_data['state'] = data.state
        return days_data

    def _make_compatible(self, data):
        data = data.copy()
        data.state = data.state.map(self._dictionary.name_to_key())
        data.country = data.country.map(self._dictionary.name_to_key())
        data.country = data.apply(self._state_is_country, axis=1)
        del(data['state'])
        return data

    def _state_is_country(self, row):
        keys = set(self._dictionary.key_to_name())
        if row.state in keys:
            return row.state
        else:
            return row.country

    def _summarize_countries(self, data):
        result_data = data.groupby('country').transform(sum)
        result_data['country'] = data.country
        result_data = result_data.drop_duplicates(subset='country')
        return result_data
