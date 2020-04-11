import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import pathlib
import logging


class GithubGraph:
    directory = 'temp_graphs'

    @classmethod
    def drop_all(cls):
        dir_path = pathlib.Path().cwd() / cls.directory
        if not dir_path.exists():
            dir_path.mkdir()
        for file in dir_path.glob('*.png'):
            logging.warning(f'removing {file.name}')
            file.unlink()

    @classmethod
    def draw_and_save(cls, data, key, name):
        fig = cls.draw(data, name)
        file_path = cls.save(fig, key)
        return file_path

    @classmethod
    def save(cls, fig, key):
        file_path = pathlib.Path.cwd() / cls.directory / f'{key}_total.png'
        fig.savefig(file_path, dpi=fig.dpi)
        return file_path

    @classmethod
    def draw(cls, data, name):
        logging.info(f'drawing: {name}')

        fig, ax = plt.subplots()

        ax.plot(data, marker='.')

        ax.set_title(name)
        ax.title.set_size(20)

        ax.set_xlim(left=data.index[0])
        ax.set_ylim(bottom=0)
        ax.grid(which='major', linestyle=':')

        ax.yaxis.set_major_formatter(ticker.FuncFormatter(
            cls._reformat_large_tick_values))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))

        return fig

    @staticmethod
    def _reformat_large_tick_values(value, pos):
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
