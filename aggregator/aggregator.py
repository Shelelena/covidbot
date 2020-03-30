from .sources import Rapidapi
from exceptions import CountryNotFound
from .dictionary import Dictionary


class Aggregator:
    def __init__(self, rapidapi_key=None):
        self._rapidapi = Rapidapi(rapidapi_key)
        self._rapidapi.load()
        self._sources = [self._rapidapi]
        self._dictionary = Dictionary()

    def get(self, country=None):
        self._load_sources_if_expired()
        return self._combine_country_data(country)

    def rating(self, start=1, end=10):
        self._load_sources_if_expired()
        return self._combine_rating_data(start, end)

    def _load_sources_if_expired(self):
        for source in self._sources:
            if source.is_expired():
                source.load()

    def _combine_country_data(self, country=None):
        try:
            current_info = self._rapidapi.get_info(country)
        except CountryNotFound:
            current_info = {'error': 'Страна не найдена'}
        return current_info

    def _combine_rating_data(self, start=1, end=10):
        rating = self._rapidapi.range(start, end)
        return rating
