from .sources import Rapidapi
from exceptions import CountryNotFound
from .dictionary import Dictionary


class Aggregator:
    def __init__(self):
        self._rapidapi = Rapidapi()
        self._rapidapi.load()
        self._sources = [self._rapidapi]
        self._dictionary = Dictionary()

    def get(self, country=None):
        self._load_sources_if_expired()
        return self._combine_data(country)

    def _load_sources_if_expired(self):
        for source in self._sources:
            if source.is_expired():
                source.load()

    def _combine_data(self, country=None):
        country = self._dictionary.name_to_key(country)
        try:
            current_info = self._rapidapi.get_info(country)
            current_info['country'] = self._dictionary.key_to_name(country)
        except CountryNotFound:
            current_info = {'error': 'Country not found'}
        return current_info
