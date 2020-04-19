from typing import TypedDict, List, Optional


class CountryInfo(TypedDict):
    key: str
    name: str
    number: int

    total_cases: int
    new_cases: Optional[str]
    recovered_cases: int
    total_deaths: int
    new_deaths: Optional[str]


class RapidapiResponse(TypedDict):

    class ResponseItemSchema(TypedDict):

        class CasesSchema(TypedDict):
            total: int
            new: Optional[str]
            critical: int
            active: int
            recovered: int

        class DeathsSchema(TypedDict):
            total: int
            new: Optional[str]

        class TestsSchema(TypedDict):
            total: str

        country: str
        cases: CasesSchema
        deaths: DeathsSchema
        tests: dict
        day: str
        time: str

    errors: list
    get: str
    parameters: list
    results: int
    response: List[ResponseItemSchema]
