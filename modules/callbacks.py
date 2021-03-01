from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
import logging
import asyncio
from datetime import datetime

from modules import keyboards as kb
from modules import database as db
from modules import credentials
from modules import messages

bot = Bot(token=credentials.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
user = db.DataBase('users', 'users', credentials.MONGO_TOKEN, '_id')
sugar = db.DataBase('sugars', 'sugars', credentials.MONGO_TOKEN, '_id')
logging.basicConfig(filename='diahelpbot.log', format='%(levelname)s : %(asctime)s | %(name)s : %(message)s')


class Sugar(StatesGroup):
    add_to_db = State()


@dp.message_handler(commands=['del'])
async def delete_user(m: types.Message):
    try:
        user[m.from_user.id].delete()
        sugar[m.from_user.id].delete()
        await bot.send_message(m.from_user.id, "Користувач успішно видален з бази даних!", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logging.error(e)


@dp.message_handler(lambda d: d.text == "Відміна" or d.text == 'відміна' or 'cancel' in d.text, state="*")
async def cancel(m: types.Message, state: FSMContext):
    """
    Ця функція закінчує будь-який діалог з користувачем
    """
    if m.text == "Відміна" or m.text == 'відміна' or 'skip' in m.text:
        await state.finish()
        await bot.send_message(m.from_user.id, messages.canceled)
    else:
        pass


@dp.message_handler(text='🆘 Допомога', state='*')
async def send_help(m: types.Message, state: FSMContext):
    await bot.send_message(m.from_user.id, messages._help, reply_markup=kb.author, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['about'], state='*')
async def send_about(m: types.Message, state: FSMContext):
    await bot.send_message(m.from_user.id, messages.about)


@dp.message_handler(commands=['menu'])
async def menu(m: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(m.from_user.id, 'Меню', reply_markup=kb.main_keyboard)


@dp.message_handler(text='🔙 Назад')
async def back_to_menu(m: types.Message):
    await bot.send_message(m.from_user.id, 'Меню', reply_markup=kb.main_keyboard)


@dp.message_handler(text='📊 Статистика')
async def statistics(m: types.Message):
    try:
        units = "мг/дл" if user[m.from_user.id]['units'] == 'units_mg' else "ммоль/л"
        maxsug = 0
        midsug = 0
        minsug = 630.63
        try:
            for i in sugar[m.from_user.id]['sugars']:
                for key in i:
                    if float(key) > maxsug:
                        maxsug = float(key)
                    if float(key) < minsug:
                        minsug = float(key)
            if maxsug == 0:
                maxsug = messages.not_found
            if minsug == 630.63:
                minsug = messages.not_found
            lst = []
            result = 0
            for i in sugar[m.from_user.id]['sugars']:
                for key in i:
                    lst.append(float(key))
            for j in lst:
                result += j
            midsug = '{:.1f}'.format(result / len(lst))
        except ZeroDivisionError or TypeError:
            midsug = messages.not_found
        await bot.send_message(m.from_user.id, messages.statistics.format(units, maxsug, midsug, minsug),
                               parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🍬 Цукор')
async def sugar_processing(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible, reply_markup=kb.sugar)


@dp.message_handler(text='➕ Додати показник')
async def save_index(m: types.Message):
    await Sugar.add_to_db.set()
    _min = "63.06" if user[m.from_user.id]['units'] == 'units_mg' else "3.5"
    await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Sugar.add_to_db)
async def add_to_db(m: types.Message, state: FSMContext):
    try:
        await state.finish()
        index = float(m.text)
        _max = 0
        _min = 0
        units = True if user[m.from_user.id]['units'] == 'units_mg' else False
        '''
        Якщо істина, значить одиниці вимірювання користувача - мг/дл, якщо ж брехня - ммоль/л
        '''
        if units:
            _max = 630.63
            _min = 18.02
        elif not units:
            _max = 35
            _min = 1
        if (index >= _min) and (index <= _max):
            _all = sugar[m.from_user.id]['sugars']
            _all.append({str(index):datetime.now().strftime("%m-%d-%Y, %H:%M:%S")})
            sugar[m.from_user.id]['sugars'] = _all
            sugar[m.from_user.id].save()
            await bot.send_message(m.from_user.id, messages.index_saved)
        else:
            hint = "_Мінімальний показник для одиниць вимірювання_ *мг/дл* - _18.02, максимальний показник - 630.63_" if user[m.from_user.id]['units'] == 'units_mg' \
                else "_Мінімальний показник для одиниць вимірювання_ *ммоль/л* - _1.0, максимальний показник - 35.0_"
            await bot.send_message(m.from_user.id, messages.to_big_value.format(hint), parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)
            _min = "63.06" if user[m.from_user.id]['units'] == 'units_mg' else "3.5"
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(e.__class__.__name__ + ': ' + str(e))
        await state.finish()
        if e.__class__.__name__ == ValueError and (m.text == "Відміна" or m.text == 'відміна' or 'cancel' in m.text):
            await state.finish()
            await bot.send_message(m.from_user.id, messages.canceled)
        else:
            await Sugar.add_to_db.set()
            _min = "63.06" if user[m.from_user.id]['units'] == 'units_mg' else "3.5"
            await bot.send_message(m.from_user.id, messages.value_error, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
