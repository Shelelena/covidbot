class CovidBotException(Exception):
    pass


class CountryNotFound(CovidBotException):
    pass


class NoRapidapiKey(CovidBotException):
    pass
