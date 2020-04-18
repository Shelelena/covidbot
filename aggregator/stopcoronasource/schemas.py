from typing import TypedDict


class StopcoronaRegionInfo(TypedDict):
    key: str
    name: str
    number: int

    total_cases: int
    recovered_cases: int
    total_deaths: int
