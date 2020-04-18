import pandas as pd
from bs4 import BeautifulSoup
from transliterate import translit


class StopcoronaDataPreparer:

    @classmethod
    def prepare(cls, data: str) -> pd.DataFrame:
        data = cls._html_to_dataframe(data)
        data = cls._set_column_names_and_types(data)
        data = cls._set_keys(data)
        data = cls._sort_and_enumerate(data)
        print(data.loc[0])
        return data

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

    @staticmethod
    def _set_keys(data) -> pd.DataFrame:
        data = data.copy()
        data['key'] = data.name.map(
            lambda name: translit(name, 'ru', reversed=True))
        data.key = data.key.str.lower()
        data.key = data.key.str.replace(r"[' \-\(\)]", '')
        data.key = data.key.str.replace('oblast', '')
        data.key = data.key.str.replace('respublika', '')
        data.key = data.key.str.replace('avtonomnyjokrug', '')

        return data

    @staticmethod
    def _sort_and_enumerate(data) -> pd.DataFrame:
        data = data.sort_values('total_cases', ascending=False)
        data = data.reset_index(drop=True)
        data['number'] = list(range(len(data)))
        return data
