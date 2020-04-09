import pathlib
from config import RAPIDAPI_KEY
from aggregator import Aggregator


async def update_mocks():
    directory = pathlib.Path(__file__).parent
    aggr = Aggregator(rapidapi_key=RAPIDAPI_KEY)

    for source in aggr._sources:
        source_name = type(source).__name__
        file_path = directory / f'mock_response_{source_name}.txt'
        response = await source.load_data()
        with file_path.open('w') as file:
            file.write(response)
