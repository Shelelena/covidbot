from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import logging


class Source(ABC):
    async def update(self) -> None:
        data: str = await self.load_data()
        data: pd.DataFrame = self.prepare_data(data)
        self.data = data
        self.last_updated = datetime.now()
        self.log_update()

    @abstractmethod
    async def load_data(self) -> str:
        pass

    @abstractmethod
    def prepare_data(self, data: str) -> pd.DataFrame:
        pass

    def is_expired(self):
        if self.last_updated is None:
            return True
        time_since_last_update = datetime.now() - self.last_updated
        return time_since_last_update > self.expire_time

    def log_update(self):
        logging.info(f'Source updated: {type(self).__name__}')
