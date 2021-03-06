from typing import TypedDict, List, Optional, Literal


class CountryInfo(TypedDict):
    key: str
    name: str
    number: int
    type: Literal['country']

    total_cases: int
    new_cases: Optional[str]
    recovered_cases: int
    total_deaths: int
    new_deaths: Optional[str]


class RegionInfo(TypedDict):
    key: str
    name: str
    number: int
    type: Literal['region']

    total_cases: int
    new_cases: int
    recovered_cases: int
    total_deaths: int
    new_deaths: int


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


class StopcoronaResponseItems(TypedDict):
    title: str
    code: str
    is_city: bool
    coord_x: str
    coord_y: str
    sick: int
    healed: int
    died: int
    sick_incr: int
    healed_incr: int
    died_incr: int
