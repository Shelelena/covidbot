import httpx
from datetime import timedelta

from exceptions import CountryNotFound
from ..sources import Source
from ..dictionary import CompatibilityDictionary
from .datapreparer import GithibDataPreparer
from .graph import GithubGraph


class GithubSource(Source):
    def __init__(self, dictionary=None):
        self.data = None
        self.last_updated = None
        self.graph_ids = {}
        self.graph_files = {}
        self.expire_time = timedelta(hours=3)
        self._dictionary = dictionary
        if self._dictionary is None:
            self._dictionary = CompatibilityDictionary()

    def graph(self, key):
        if key in self.graph_ids:
            return self.graph_ids[key]
        elif key in self.graph_files:
            return self.graph_files[key]
        elif key in self.data.index:
            path = self._create_graph(key)
            self.graph_ids[key] = path
            return path
        else:
            raise CountryNotFound(f'No country: {key}')

    def save_graph_id(self, key, id):
        self.graph_ids[key] = id

    async def load_data(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://raw.githubusercontent.com/CSSEGISandData/COVID-19"
                "/master/csse_covid_19_data/csse_covid_19_time_series"
                "/time_series_covid19_confirmed_global.csv")
        return response.text

    def prepare_data(self, data):
        data = GithibDataPreparer.prepare(data, self._dictionary)
        if self._new_data(data):
            self._drop_graphs()
        return data

    def _new_data(self, data):
        return (
            self.data is None
            or self.data.columns[-1] != data.columns[-1]
        )

    def _drop_graphs(self):
        GithubGraph.drop_all()
        self.graph_ids = {}
        self.graph_files = {}

    def _create_graph(self, key):
        country_name = self._dictionary.key_to_name(key)
        data = self.data.loc[self.data.index == key]
        path = GithubGraph.draw_and_save(data, key, country_name)
        return path
