import json
import pandas as pd
import logging

from aggregator.schemas import RapidapiResponse
from aggregator.matcher import CountryNameMatcher


class RapidapiDataPreparer:

    @classmethod
    def prepare(
        cls,
        data: str,
        matcher: CountryNameMatcher
    ) -> pd.DataFrame:

        data: pd.DataFrame = cls._json_to_dataframe(data)
        data = cls._unwrap_columns(data)
        data = cls._choose_columns(data)
        data = cls._convert_types(data)
        data = cls._set_country_keys_and_names(data, matcher)
        data = cls._remove_non_countries(data)
        data = cls._sort_and_enumerate(data)
        cls._check_new_countries(data, matcher)
        return data

    @staticmethod
    def _json_to_dataframe(data: str) -> pd.DataFrame:
        data: RapidapiResponse = json.loads(data)
        data = data['response']
        data = pd.DataFrame(data)
        return data

    @classmethod
    def _unwrap_columns(cls, data) -> pd.DataFrame:
        for colname in ('cases', 'deaths'):
            data = cls._unwrap_one_column(data, colname)
        return data

    @staticmethod
    def _unwrap_one_column(data, colname: str) -> pd.DataFrame:
        data = data.copy()
        unwrapped_data = pd.DataFrame(list(data[colname]))
        unwrapped_data.columns = [
            name + '_' + colname
            for name in unwrapped_data.columns
        ]
        data = data.join(unwrapped_data)
        del(data[colname])
        return data

    @staticmethod
    def _choose_columns(data) -> pd.DataFrame:
        columns = [
            'country', 'total_cases', 'new_cases',
            'recovered_cases', 'total_deaths', 'new_deaths']
        data = data[data.columns.intersection(columns)]
        return data

    @staticmethod
    def _convert_types(data) -> pd.DataFrame:
        data = data.copy()
        data.total_cases = data.total_cases.astype(object)
        data.recovered_cases = data.recovered_cases.astype(object)
        data.total_deaths = data.total_deaths.astype(object)
        return data

    @staticmethod
    def _set_country_keys_and_names(data, matcher) -> pd.DataFrame:
        data = data.copy()
        data['key'] = data.country.str.lower()
        del data['country']
        data.key = data.key.str.replace(r'[\.\-\&\;]', '')
        data.key = data.key.map(matcher.name_to_key())
        data = data.drop_duplicates(subset=['key'])
        data['name'] = data.key.map(matcher.key_to_name())
        return data

    @staticmethod
    def _remove_non_countries(data) -> pd.DataFrame:
        exceptions = [
            'europe', 'northamerica', 'asia',
            'southamerica', 'africa', 'oceania',
            ''
        ]
        data = data.where(~data.key.isin(exceptions))
        data = data.dropna(subset=['key'])
        return data

    @staticmethod
    def _sort_and_enumerate(data) -> pd.DataFrame:
        data = data.sort_values('total_cases', ascending=False)
        data = data.reset_index(drop=True)
        data['number'] = list(range(len(data)))
        data['type'] = ['country'] * len(data)
        return data

    @staticmethod
    def _check_new_countries(data, matcher) -> None:
        new_countries = set(data.key)
        old_countries = matcher.keys()
        difference = new_countries - old_countries
        if len(difference) > 0:
            logging.warning(
                f' New countries: {str(difference)}')
