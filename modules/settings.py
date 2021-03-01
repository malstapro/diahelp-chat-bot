from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from modules.database import DataBase
from datetime import datetime
from modules import credentials
from modules.callbacks import bot, dp


class Settings(StatesGroup):
    clear_sugar = State()


# @dp.message_handler(state=Settings.clear_sugar)
# async def clear_sugar(m: types.Message):

