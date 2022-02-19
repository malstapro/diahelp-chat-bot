import asyncio

from aiogram.utils import executor

from modules.handlers.mailing import dp
from modules.handlers.sugar import dp
from modules.handlers.info import dp
from modules.handlers.food import dp
from modules.handlers.statistics import dp
from modules.handlers.settings import dp
from modules.handlers.commands import dp
from modules.handlers.registration import dp


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(60, repeat, coro, loop)


if __name__ == "__main__":
    # logging.info("BotStarted")
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True, loop=loop)
