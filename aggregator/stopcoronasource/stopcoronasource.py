import httpx
from datetime import datetime, timedelta
import pandas as pd

from aggregator.sources import Source
from aggregator.matcher import CountryNameMatcher


class StopcoronaSource(Source):
    def __init__(self, matcher: CountryNameMatcher = None):
        self.data: pd.DataFrame = None
        self.last_updated: datetime = None
        self.expire_time = timedelta(minutes=30)

        self._matcher = matcher
        if self._matcher is None:
            self._matcher = CountryNameMatcher()

    async def load_data(self) -> str:
        async with httpx.AsyncClient() as client:
            result = await client.get(
                "https://стопкоронавирус.рф/",
            )
        return result.text

    def prepare_data(self, data: str) -> pd.DataFrame:
        pass
