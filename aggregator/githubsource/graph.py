from pathlib import Path
import logging
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


class GithubGraph:
    directory = 'temp_graphs'

    @classmethod
    def drop_all(cls) -> None:
        dir_path = Path().cwd() / cls.directory
        if not dir_path.exists():
            dir_path.mkdir()
        for file in dir_path.glob('*.png'):
            logging.warning(f'removing {file.name}')
            file.unlink()

    @classmethod
    def draw_and_save(
        cls,
        data: pd.Series,
        country_name: str,
        file_name: str,
    ) -> Path:

        fig = cls.draw(data, country_name)
        file_path = cls.save(fig, file_name)
        return file_path

    @classmethod
    def save(cls, fig: mpl.figure.Figure, file_name: str) -> Path:
        file_path = Path.cwd() / cls.directory / f'{file_name}.png'
        fig.savefig(file_path, dpi=fig.dpi)
        return file_path

    @classmethod
    def draw(cls, data: pd.Series, name: str) -> mpl.figure.Figure:
        logging.info(f'drawing: {name}')

        fig, ax = plt.subplots()

        ax.plot(data, marker='.')

        ax.set_title(name)
        ax.title.set_size(20)

        ax.set_xlim(left=data.index[0])
        ax.set_ylim(bottom=0)
        ax.grid(which='major', linestyle=':')

        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(
            cls._reformat_large_tick_values))
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%d.%m"))

        return fig

    @staticmethod
    def _reformat_large_tick_values(value: int, pos=None) -> str:
        if value >= 1000_000_000:
            result = round(value/1000_000_000, 1)
            result = f'{result}B'
        elif value >= 1000_000:
            result = round(value/1000_000, 1)
            result = f'{result}M'
        elif value >= 1000:
            result = round(value/1000, 1)
            result = f'{result}k'
        else:
            result = str(round(value, 1))
        result = result.replace('.0', '')
        return result
