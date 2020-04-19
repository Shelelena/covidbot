import pandas as pd
from bs4 import BeautifulSoup
from transliterate import translit
import re


class StopcoronaDataPreparer:

    @classmethod
    def prepare(cls, data: str) -> pd.DataFrame:
        data = cls._html_to_dataframe(data)
        data = cls._set_column_names_and_types(data)
        data = cls._set_keys(data)
        data = cls._sort_and_enumerate(data)
        return data

    @staticmethod
    def translit_name(name: str) -> str:
        key = translit(name, 'ru', reversed=True)
        key = key.lower()
        key = re.sub(r"[' \-\(\)]", '', key)
        key = key.replace('oblast', '')
        key = key.replace('respublika', '')
        key = key.replace('avtonomnyjokrug', '')
        key = key.replace('kraj', '')
        return key

    @staticmethod
    def _html_to_dataframe(data: str) -> pd.DataFrame:
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('div', class_='d-map__list')
        rows = table.find_all('tr')
        rows = [row.find_all(['th', 'td']) for row in rows]
        rows = [[value.text for value in row] for row in rows]
        data = pd.DataFrame(rows)
        return data

    @staticmethod
    def _set_column_names_and_types(data) -> pd.DataFrame:
        data = data.copy()
        data.columns = [
            'name', 'total_cases', 'recovered_cases', 'total_deaths']
        data.total_cases = data.total_cases.astype(int)
        data.recovered_cases = data.recovered_cases.astype(int)
        data.total_deaths = data.total_deaths.astype(int)
        data.name = data.name.str.replace('—', '-')
        return data

    @classmethod
    def _set_keys(cls, data) -> pd.DataFrame:
        data = data.copy()
        data['key'] = data.name.map(cls.translit_name)
        return data

    @staticmethod
    def _sort_and_enumerate(data) -> pd.DataFrame:
        data = data.sort_values('total_cases', ascending=False)
        data['number'] = list(range(1, len(data)+1))
        data.index = data.number
        data['type'] = ['region'] * len(data)
        return data
