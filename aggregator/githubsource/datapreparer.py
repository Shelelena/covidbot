import io
import pandas as pd
from datetime import datetime


class GithibDataPreparer:
    @classmethod
    def prepare(cls, data, dictionary):
        data = cls._csv_to_dataframe(data)
        data = cls._select_columns(data)
        data = cls._transform_keys(data, dictionary)
        data = cls._make_compatible(data, dictionary)
        data = cls._summarize_countries(data)
        data = cls._add_world(data)
        return data

    @staticmethod
    def _csv_to_dataframe(data):
        data = io.StringIO(data)
        data = pd.read_csv(data)
        return data

    @staticmethod
    def _select_columns(data):
        days_data = data.filter(regex=r'^\d+/\d+/\d+$')
        days_data = days_data[days_data.columns[:]]
        days_data.columns = days_data.columns.map(
            lambda day: datetime.strptime(day, '%m/%d/%y'))
        days_data['country'] = data['Country/Region']
        days_data['state'] = data['Province/State']
        return days_data

    @staticmethod
    def _transform_keys(data, dictionary):
        data = data.copy()
        data.country = data.country.str.lower()
        data.country = data.country.str.replace(r"[ \(\)\*\'\.\,\-\&\;]", '')
        data.country = data.country.map(dictionary.name_to_key())
        data.state = data.state.str.lower()
        data.state = data.state.str.replace(r"[ \(\)\*\'\.\,\-\&\;]", '')
        data.state = data.state.map(dictionary.name_to_key())
        return data

    @classmethod
    def _make_compatible(cls, data, dictionary):
        data = data.copy()
        data.state = data.state.map(dictionary.name_to_key())
        data.country = data.country.map(dictionary.name_to_key())
        data.country = data.apply(
            lambda row:
                row.state
                if row.state in dictionary.key_to_name()
                else row.country,
            axis=1
        )
        del(data['state'])
        return data

    @staticmethod
    def _state_is_country(row, dictionary):
        keys = set(dictionary.key_to_name())
        if row.state in keys:
            return row.state
        else:
            return row.country

    @staticmethod
    def _summarize_countries(data):
        result_data = data.groupby('country').transform(sum)
        result_data.index = data.country
        result_data = result_data.drop_duplicates()
        return result_data

    @staticmethod
    def _add_world(data):
        data = data.copy()
        data.loc['all'] = data.apply(sum)
        return data
