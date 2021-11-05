import asyncio

from aiogram.utils import executor

from modules.callbacks import dp
from modules.registration import dp
from modules.settings import dp
from modules.mailing import dp


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(60, repeat, coro, loop)


if __name__ == "__main__":
    # logging.info("BotStarted")
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True, loop=loop)
