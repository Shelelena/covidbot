from abc import ABC, abstractmethod
from datetime import datetime
import logging


class Source(ABC):
    def update(self):
        data = self.load_data()
        self.data = self.prepare_data(data)
        self.last_updated = datetime.now()
        logging.info(f'Source updated: {type(self).__name__}')

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def prepare_data(self):
        pass

    def is_expired(self):
        if self.last_updated is None:
            return True
        time_since_last_update = datetime.now() - self.last_updated
        return time_since_last_update > self.expire_time
