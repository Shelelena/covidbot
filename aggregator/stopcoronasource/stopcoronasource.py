from typing import List
import httpx
from datetime import datetime, timedelta
import pandas as pd

from aggregator.sources import Source
from aggregator.matcher import CountryNameMatcher
from .datapreparer import StopcoronaDataPreparer
from aggregator.schemas import RegionInfo
from exceptions import CountryNotFound


class StopcoronaSource(Source):
    def __init__(self, matcher: CountryNameMatcher = None):
        self.data: pd.DataFrame = None
        self.last_updated: datetime = None
        self.expire_time = timedelta(minutes=30)

        self._matcher = matcher
        if self._matcher is None:
            self._matcher = CountryNameMatcher()

    def single_region(self, name) -> RegionInfo:
        key = StopcoronaDataPreparer.translit_name(name)
        region: list = self.regions_by_keys(key)
        if len(region) == 0:
            raise CountryNotFound(f'No such region: {region}')
        region: dict = region[0]
        return region

    def regions_by_keys(
        self,
        *keys: List[str]
    ) -> List[RegionInfo]:

        selected_regions = self.data[self.data.key.isin(keys)]
        region_dicts: list = selected_regions.to_dict(orient='records')
        return region_dicts

    def regions_by_range(
        self,
        start=1,
        end=10
    ) -> List[RegionInfo]:

        range_data = self.data.loc[start:end]
        range_data = range_data.to_dict(orient='records')
        return range_data

    async def load_data(self) -> str:
        async with httpx.AsyncClient() as client:
            result = await client.get(
                "https://стопкоронавирус.рф/information/",
            )
        return result.text

    def prepare_data(self, data: str) -> pd.DataFrame:
        data = StopcoronaDataPreparer.prepare(data)
        return data
