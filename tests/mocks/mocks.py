import pathlib


def mock_load(source_name):
    response_path = (
        pathlib.Path(__file__).parent / f'mock_response_{source_name}.txt')
    with response_path.open() as file:
        response = file.read()

    async def _mocked_method(self=None):
        return response

    return _mocked_method
