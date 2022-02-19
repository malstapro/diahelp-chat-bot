from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ParseMode
from loguru import logger

from modules import credentials
from modules import database as db
from modules import keyboards as kb


bot = Bot(token=credentials.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
user = db.DataBase('users', 'users', credentials.MONGO_TOKEN, '_id')
sugar = db.DataBase('sugars', 'sugars', credentials.MONGO_TOKEN, '_id')
food = db.DataBase('food', 'food', credentials.MONGO_TOKEN, '_id')
logger.add("diahelpbot.log", format="[{time}] ({level}) - {message}", level="INFO")
dt_format = "%m/%d/%Y/%H/%M/%S"
defaultSugar = {
    'sugars': []
}


async def finish_state(state: FSMContext):
    try:
        async with state.proxy() as data:
            if 'add-sugar-last-time' in data.keys() and 'chart-last-time' in data.keys():
                tmp = [data['add-sugar-last-time'], data['chart-last-time']]
                await state.finish()
                async with state.proxy() as new_data:
                    new_data['add-sugar-last-time'] = tmp[0]
                    new_data['chart-last-time'] = tmp[1]
            elif 'add-sugar-last-time' in data.keys() or 'chart-last-time' in data.keys():
                tmp = data['add-sugar-last-time'] if 'add-sugar-last-time' in data.keys() else data['chart-last-time']
                await state.finish()
                async with state.proxy() as new_data:
                    if 'add-sugar-last-time' in data.keys():
                        new_data['add-sugar-last-time'] = tmp
                    elif 'chart-last-time' in data.keys():
                        new_data['chart-last-time'] = tmp
            else:
                await state.finish()
    except Exception as e:
        logger.error(e.__class__.__name__ + ': ' + str(e))
        await state.finish()


@dp.message_handler(text='🔙 Назад')
async def back_to_menu(m: types.Message):
    await bot.send_message(m.from_user.id, 'Меню', reply_markup=kb.main_keyboard_admin if user[m.from_user.id][
        'is_admin'] else kb.main_keyboard)
