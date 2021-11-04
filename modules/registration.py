from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from modules import keyboards as kb
from modules import database as db
from modules import credentials
from modules import messages
from modules.callbacks import bot, dp, user, sugar
from datetime import datetime


defaultUser = {
    'units': None
}
defaultSugar = {
    'sugars': {
        f'{datetime.now().year}': {
            f'{datetime.now().month}': {
                f'{datetime.now().day}': {

                }
            }
        }
    }
}


class Registration(StatesGroup):
    save_units = State()


@dp.message_handler(commands=['start'])
async def register(m: types.Message, state: FSMContext):
    await state.finish()
    user[m.from_user.id] = defaultUser
    sugar[m.from_user.id] = defaultSugar
    user[m.from_user.id].commit()
    sugar[m.from_user.id].commit()
    await Registration.save_units.set()
    await bot.send_message(m.from_user.id, messages.welcome, parse_mode=ParseMode.MARKDOWN)
    await bot.send_message(m.from_user.id,messages.reg, reply_markup=kb.reg)


@dp.callback_query_handler(state=Registration.save_units)
async def end_registration(q: types.CallbackQuery, state: FSMContext):
    user[q.from_user.id]['units'] = q.data
    user[q.from_user.id].commit()
    await state.finish()
    await bot.send_message(q.from_user.id, messages.end_reg)
    await bot.send_message(q.from_user.id, messages.accessible, reply_markup=kb.main_keyboard)
