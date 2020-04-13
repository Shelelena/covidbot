from typing import Dict, Union
import httpx
from pathlib import Path
from datetime import timedelta, datetime
import pandas as pd

from exceptions import CountryNotFound
from ..sources import Source
from ..dictionary import CompatibilityDictionary
from .datapreparer import GithibDataPreparer
from .graph import GithubGraph


class GithubSource(Source):
    def __init__(
        self,
        dictionary: CompatibilityDictionary = None
    ):
        self.data: pd.DataFrame = None
        self.last_updated: datetime = None
        self.graph_ids: Dict[str, str] = {}
        self.graph_file_paths: Dict[str, Path] = {}
        self.expire_time = timedelta(hours=3)

        self._dictionary = dictionary
        if self._dictionary is None:
            self._dictionary = CompatibilityDictionary()

    def graph(self, name: 'str') -> Union[Path, str, None]:
        key = self._dictionary.name_to_key(name)
        if key in self.graph_ids:
            return self.graph_ids[key]
        elif key in self.graph_file_paths:
            return self.graph_file_paths[key]
        elif key in self.data.index:
            path = self._create_graph(key)
            self.graph_file_paths[key] = path
            return path
        else:
            raise CountryNotFound(f'No country: {key}')

    def save_graph_id(self, key: str, id: str) -> None:
        self.graph_ids[key] = id

    async def load_data(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://raw.githubusercontent.com/CSSEGISandData/COVID-19"
                "/master/csse_covid_19_data/csse_covid_19_time_series"
                "/time_series_covid19_confirmed_global.csv")
        return response.text

    def prepare_data(self, data: str) -> pd.DataFrame:
        data = GithibDataPreparer.prepare(data, self._dictionary)
        if self._new_data(data):
            self._drop_graphs()
        return data

    def _new_data(self, data: pd.DataFrame) -> bool:
        return (
            self.data is None
            or self.data.columns[-1] < data.columns[-1]
        )

    def _drop_graphs(self) -> None:
        GithubGraph.drop_all()
        self.graph_ids = {}
        self.graph_file_paths = {}

    def _create_graph(self, key: str) -> Path:
        country_name: str = self._dictionary.key_to_name(key)
        data: pd.Series = self.data.loc[key]
        file_name = f'{key}_total'
        path = GithubGraph.draw_and_save(data, country_name, file_name)
        return path
