from .sources import Rapidapi
from exceptions import CountryNotFound


class Aggregator:
    def __init__(self):
        self._rapidapi = Rapidapi()
        self._rapidapi.load()
        self._sources = [self._rapidapi]

    def get(self, country=None):
        self._load_sources_if_expired()
        return self._combine_data(country)

    def _load_sources_if_expired(self):
        for source in self._sources:
            if source.is_expired():
                source.load()

    def _combine_data(self, country=None):
        try:
            current_info = self._rapidapi.get_info(country)
        except CountryNotFound:
            return {'error': 'Country not found'}
        return current_info
