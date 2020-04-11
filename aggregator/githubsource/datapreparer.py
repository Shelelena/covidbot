import io
import pandas as pd
from datetime import datetime

from aggregator.dictionary import CompatibilityDictionary


class GithibDataPreparer:

    @classmethod
    def prepare(
        cls,
        data: str,
        dictionary: CompatibilityDictionary
    ) -> pd.DataFrame:

        data: pd.DataFrame = cls._csv_to_dataframe(data)
        data = cls._colnames_to_datetime(data)
        data = cls._country_and_region_names_to_keys(data, dictionary)
        data = cls._collapse_regions_to_countries(data, dictionary)
        data = cls._summarize_countries(data)
        data = cls._add_world(data)
        return data

    @staticmethod
    def _csv_to_dataframe(data) -> pd.DataFrame:
        data = io.StringIO(data)
        data = pd.read_csv(data)
        return data

    @staticmethod
    def _colnames_to_datetime(initial_data) -> pd.DataFrame:
        data = initial_data.filter(regex=r'^\d+/\d+/\d+$').copy()
        data.columns = data.columns.map(
            lambda day: datetime.strptime(day, '%m/%d/%y'))
        data['country'] = initial_data['Country/Region']
        data['region'] = initial_data['Province/State']
        return data

    @staticmethod
    def _country_and_region_names_to_keys(data, dictionary) -> pd.DataFrame:
        data = data.copy()
        for colname in ('country', 'region'):
            data[colname] = data[colname].str.lower()
            data[colname] = data[colname].str.replace(
                r"[ \(\)\*\'\.\,\-\&\;]", '')
            data[colname] = data[colname].map(dictionary.name_to_key())
        return data

    @classmethod
    def _collapse_regions_to_countries(cls, data, dictionary) -> pd.DataFrame:
        data = data.copy()
        data.country = data.apply(
            lambda row:
                row.region
                if row.region in dictionary.keys()
                else row.country,
            axis=1
        )
        del(data['region'])
        return data

    @staticmethod
    def _summarize_countries(initial_data) -> pd.DataFrame:
        data = initial_data.groupby('country').transform(sum)
        data.index = initial_data.country
        data = data.drop_duplicates()
        return data

    @staticmethod
    def _add_world(data) -> pd.DataFrame:
        data = data.copy()
        data.loc['all'] = data.apply(sum)
        return data
