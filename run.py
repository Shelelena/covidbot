import asyncio
from bot import bot


async def main():
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    bot.polling(none_stop=True)
