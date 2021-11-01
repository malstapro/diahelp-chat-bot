from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from loguru import logger
import asyncio
from datetime import datetime
# import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from modules import keyboards as kb
from modules import database as db
from modules import credentials
from modules import messages

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

class Sugar(StatesGroup):
    add_to_db = State()
    mid_sugar = State()
    all_sugar = State()


class Settings(StatesGroup):
    clear_sugar_confirm = State()
    change_units_confirm = State()
    change_units = State()


class Rating(StatesGroup):
    send_rating = State()


class Convert(StatesGroup):
    mg_to_moll_state = State()
    moll_to_mg_state = State()


class FoodSearch(StatesGroup):
    search = State()


@dp.message_handler(commands=['del'])
async def delete_user(m: types.Message):
    try:
        user[m.from_user.id].delete()
        sugar[m.from_user.id].delete()
        await bot.send_message(m.from_user.id, "Користувач успішно видален з бази даних!", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logger.error(e)


@dp.message_handler(lambda d: d.text == "Відміна" or d.text == 'відміна' or d.text == 'cancel' or d.text == '/cancel', state="*")
async def cancel(m: types.Message, state: FSMContext):
    """
    Ця функція закінчує будь-який діалог з користувачем
    """
    if m.text == "Відміна" or m.text == 'відміна' or 'cancel' in m.text:
        await state.finish()
        await bot.send_message(m.from_user.id, messages.canceled, reply_markup=kb.main_keyboard)
    else:
        pass




@dp.message_handler(commands=['about'], state='*')
async def send_about(m: types.Message, state: FSMContext):
    await bot.send_message(m.from_user.id, messages.about)


@dp.message_handler(commands=['help'], state='*')
async def send_help(m: types.Message):
    await bot.send_message(m.from_user.id, messages._help, reply_markup=kb.author, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


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
        await bot.send_message(m.from_user.id, 'Функція виводу статистики зараз не працює. Якщо у вас виникли питання зверниться до розробника @tesla33io')
        # sugars = sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][f'{datetime.now().day}']
        # time_list = []
        # index_list = []
        #
        # for time in sugars:
        #     time_list.append(int(str(time).replace('-', '')))
        #     index_list.append(float(str(sugars[time])))
        # plt.bar(time_list, index_list)
        # plt.show()
    except Exception as e:
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🍬 Цукор')
async def sugar_processing(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible_sugar, reply_markup=kb.sugar, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text='➕ Додати показник')
async def save_index(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            if data['add-sugar-last-time'].day >= datetime.now().day and data['add-sugar-last-time'].hour >= datetime.now().hour and (datetime.now().minute - data['add-sugar-last-time'].minute) >= 5:
                await Sugar.add_to_db.set()
                _min = "81.08" if user[m.from_user.id]['units'] == 'units_mg' else "4.5"
                await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
            else:
                # print(datetime.now().minute - data['add-sugar-last-time'].minute)
                await bot.send_message(m.from_user.id, messages.waite_add_sugar.format(5 - (datetime.now().minute - data['add-sugar-last-time'].minute)), parse_mode=ParseMode.MARKDOWN)
        except KeyError:
            await Sugar.add_to_db.set()
            _min = "81.08" if user[m.from_user.id]['units'] == 'units_mg' else "4.5"
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Sugar.add_to_db)
async def add_to_db(m: types.Message, state: FSMContext):
    global units
    try:
        await state.finish()
        index = float(m.text)
        print(type(index))
        _max = 0
        _min = 0
        global units
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
            # _all = sugar[m.from_user.id]['sugars']
            # _all.append({str(index):datetime.now().strftime(dt_format)})
            # sugar[m.from_user.id]['sugars'] = _all
            sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][f'{datetime.now().day}'][f'{datetime.now().hour}-{datetime.now().minute}'] = str(index)
            sugar[m.from_user.id].save()
            async with state.proxy() as data:
                data['add-sugar-last-time'] = datetime.now()
            # await bot.send_message(m.from_user.id, messages.index_saved)
            # if units and index <= 72.07:
            #     await bot.send_message(m.from_user.id, messages.if_too_low_index)
            # elif units and index >= 234.23:
            #     await bot.send_message(m.from_user.id, messages.if_too_high_index)
            # if not units and index <= 4.0:
            #     await bot.send_message(m.from_user.id, messages.if_too_low_index)
            # elif not units and index >= 11.0:
            #     await bot.send_message(m.from_user.id, messages.if_too_high_index)
        else:
            hint = "_Мінімальний показник для одиниць вимірювання_ *мг/дл* - _18.02, максимальний показник - 630.63_" if user[m.from_user.id]['units'] == 'units_mg' \
                else "_Мінімальний показник для одиниць вимірювання_ *ммоль/л* - _1.0, максимальний показник - 35.0_"
            await bot.send_message(m.from_user.id, messages.to_big_value.format(hint), parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)
            _min = "63.06" if user[m.from_user.id]['units'] == 'units_mg' else "3.5"
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
    except KeyError:
        sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'] = {f'{datetime.now().day}': {f'{datetime.now().hour}-{datetime.now().minute}':str(index)}}
        sugar[m.from_user.id].save()
        # sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][f'{datetime.now().day}'] = [f'{datetime.now().hour}-{datetime.now().minute}']
        # sugar[m.from_user.id].save()
        # sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][f'{datetime.now().day}'][f'{datetime.now().hour}-{datetime.now().minute}'] = str(index)
        # sugar[m.from_user.id].save()
    except Exception as e:
        logger.error(e.__class__.__name__ + ': ' + str(e))
        await state.finish()
        if e.__class__.__name__ == ValueError and (m.text == "Відміна" or m.text == 'відміна' or 'cancel' in m.text):
            await state.finish()
            await bot.send_message(m.from_user.id, messages.canceled)
        elif e.__class__.__name__ == KeyError:
            pass
        else:
            await Sugar.add_to_db.set()
            _min = "63.06" if user[m.from_user.id]['units'] == 'units_mg' else "3.5"
            await bot.send_message(m.from_user.id, messages.value_error, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
    finally:
        await bot.send_message(m.from_user.id, messages.index_saved)
        if units and index <= 72.07:
            await bot.send_message(m.from_user.id, messages.if_too_low_index)
        elif units and index >= 234.23:
            await bot.send_message(m.from_user.id, messages.if_too_high_index)
        if not units and index <= 4.0:
            await bot.send_message(m.from_user.id, messages.if_too_low_index)
        elif not units and index >= 11.0:
            await bot.send_message(m.from_user.id, messages.if_too_high_index)


@dp.message_handler(text='🔘 Середній показник')
async def middle_sugar_choice(m: types.Message):
    await Sugar.mid_sugar.set()
    await bot.send_message(m.from_user.id, messages.mid_sug_choice, reply_markup=kb.period_sug_choice)


@dp.callback_query_handler(state=Sugar.mid_sugar)
async def middle_sugar_processing(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    if q.data == 'midsug_day' or q.data == 'midsug_month':
        try:
            now_day = datetime.now().strftime('%d')
            now_month = datetime.now().strftime('%m')
            _all = sugar[q.from_user.id]['sugars']
            result = []
            for i in _all:
                for j in i:
                    date = i[j].split('/')
                    if q.data == 'midsug_day':
                        if date[1] == now_day:
                            result.append(float(j))
                    elif q.data == 'midsug_month':
                        if date[0] == now_month:
                            result.append(float(j))
            if q.data == 'midsug_day':
                middle_sugar_all_day = 0
                for i in result:
                    middle_sugar_all_day += i
                middle_sugar_day = '{:.1f}'.format(middle_sugar_all_day / len(result))
                await bot.send_message(q.from_user.id, messages.mid_sug_day.format(middle_sugar_day), parse_mode=ParseMode.MARKDOWN)
            elif q.data == 'midsug_month':
                middle_sugar_all_month = 0
                for i in result:
                    middle_sugar_all_month += i
                middle_sugar_month = '{:.1f}'.format(middle_sugar_all_month / len(result))
                await bot.send_message(q.from_user.id, messages.mid_sug_day.format(middle_sugar_month), parse_mode=ParseMode.MARKDOWN)
            await state.finish()
        except Exception as e:
            await state.finish()
            logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🔘 Усі показники')
async def all_sugar_processing(m: types.Message, state: FSMContext):
    await Sugar.all_sugar.set()
    async with state.proxy() as data:
        msg = await bot.send_message(m.from_user.id, messages.all_sug_choice, reply_markup=kb.period_sug_choice)
        data['all_sug_msg'] = msg.message_id


@dp.callback_query_handler(state=Sugar.all_sugar)
async def all_sugar(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        result = []
        # mon_result = []
        now_day = datetime.now().day
        now_month = datetime.now().month
        _all = sugar[q.from_user.id]['sugars']
        # for i in _all:
        #     for j in i:
        #         date = i[j].split('/')
        #         if q.data == 'midsug_day':
        #             if date[1] == now_day:
        #                 result.append(f"{j} - {i[j].split('/')[3]}:{i[j].split('/')[4]}:{i[j].split('/')[5]}")
        #         elif q.data == 'midsug_month':
        #             if date[0] == now_month:
        #                 result.append(f"{j} - {i[j].split('/')[3]}:{i[j].split('/')[4]}:{i[j].split('/')[5]}")
        if q.data == 'midsug_day':
            # await bot.send_message(q.from_user.id, messages.all_sug_day.format('\n'.join('🔹' + str(a) for a in result)))
            day_sugars = sugar[q.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][f'{datetime.now().day}']
            for sug in day_sugars:
                result.append(f'🔸 {str(sug).replace("-",":")} - {day_sugars[sug]}')
            async with state.proxy() as data:
                await bot.edit_message_text(messages.all_sug_day.format('\n'.join(str(a) for a in result)), q.from_user.id, data['all_sug_msg'])
            await state.finish()
        elif q.data == 'midsug_month':
            # await bot.send_message(q.from_user.id, messages.all_sug_month.format('\n'.join('🔹' + str(a) for a in result)))
            mon_sugars = sugar[q.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}']
            for day in mon_sugars:
                for sug in mon_sugars[str(day)]:
                    result.append(f'🔸 {datetime.now().month}.{day} - {str(sug).replace("-",":")} - {mon_sugars[str(day)][sug]}')
            async with state.proxy() as data:
                await bot.edit_message_text(messages.all_sug_month.format('\n'.join(str(a) for a in result)), q.from_user.id, data['all_sug_msg'])
            await state.finish()
    except Exception as e:
        await state.finish()
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='мг/дл ➡ ммоль/л')
async def mg_to_moll_get(m: types.Message, state: FSMContext):
    await Convert.mg_to_moll_state.set()
    await bot.send_message(m.from_user.id, messages.mg_to_moll_get)


@dp.message_handler(state=Convert.mg_to_moll_state)
async def mg_to_moll_result(m: types.Message, state: FSMContext):
    mg = float(m.text)
    r = mg / 18
    await bot.send_message(m.from_user.id, messages.mg_to_moll_result.format(mg, '{:.1f}'.format(r)))
    await state.finish()


@dp.message_handler(text='ммоль/л ➡ мг/дл')
async def moll_to_mg_get(m: types.Message, state: FSMContext):
    await Convert.moll_to_mg_state.set()
    await bot.send_message(m.from_user.id, messages.moll_to_mg_get)


@dp.message_handler(state=Convert.moll_to_mg_state)
async def moll_to_mg_result(m: types.Message, state: FSMContext):
    moll = float(m.text)
    r = moll * 18
    await bot.send_message(m.from_user.id, messages.moll_to_mg_result.format(moll, '{:.1f}'.format(r)))
    await state.finish()


# @dp.message_handler(text='🍎 Їжа')
# async def food(m: types.Message, state: FSMContext):
#     await FoodSearch.search.set()
#     await bot.send_message(m.from_user.id, messages.select_food)


# @dp.message_handler(state=FoodSearch.search)
# async def food_search(m: types.Message, state: FSMContext):
#     name = m.text
#     for i in food[1]:
#


@dp.message_handler(text='⚙ Налаштування')
async def settings_processing(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible_settings, reply_markup=kb.settings, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text='🗑 Видалити показники цукру')
async def clear_sugar_processing(m: types.Message):
    await Settings.clear_sugar_confirm.set()
    await bot.send_message(m.from_user.id, messages.settings_clear_sug_conf, reply_markup=kb.confirm, parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(state=Settings.clear_sugar_confirm)
async def clear_sugar(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        if q.data == 'yes':
            sugar[q.from_user.id].delete()
            sugar[q.from_user.id] = defaultSugar
            sugar[q.from_user.id].save()
            await state.finish()
            await bot.send_message(q.from_user.id, messages.data_deleted, reply_markup=kb.settings)
        elif q.data == 'no':
            await state.finish()
            await bot.send_message(q.from_user.id, messages.canceled, reply_markup=kb.settings)
    except Exception as e:
        await state.finish()
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🔄 Змінити одиниці вимірювання')
async def change_units_processing(m: types.Message):
    await Settings.change_units_confirm.set()
    await bot.send_message(m.from_user.id, messages.units_change_warn, reply_markup=kb.confirm, parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(state=Settings.change_units_confirm)
async def change_units_confirm_processing(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        if q.data == 'yes':
            await Settings.change_units.set()
            await bot.send_message(q.from_user.id, messages.choice_units, reply_markup=kb.reg)
        elif q.data == 'no':
            await state.finish()
            await bot.send_message(q.from_user.id, messages.canceled, reply_markup=kb.settings)
    except Exception as e:
        await state.finish()
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.callback_query_handler(state=Settings.change_units)
async def change_units(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        units = user[q.from_user.id]['units']
        if q.data == units:
            await state.finish()
            await bot.send_message(q.from_user.id, messages.units_identical_error, reply_markup=kb.settings)
        else:
            sugar[q.from_user.id].delete()
            sugar[q.from_user.id] = defaultSugar
            sugar[q.from_user.id].save()
            user[q.from_user.id]['units'] = q.data
            user[q.from_user.id].save()
            await state.finish()
            await bot.send_message(q.from_user.id, messages.units_changed, reply_markup=kb.settings)
    except Exception as e:
        await state.finish()
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='ℹ Інформація')
async def information(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible_info, reply_markup=kb.info, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text='👤 Творець')
async def author(m: types.Message):
    await bot.send_message(m.from_user.id, messages.author, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


@dp.message_handler(text='⭐ Оцінити бота')
async def rating(m: types.Message):
    await Rating.send_rating.set()
    await bot.send_message(m.from_user.id, messages.rating_choice, reply_markup=kb.rating)


@dp.callback_query_handler(state=Rating.send_rating)
async def send_rating(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        id = 614259495
        await bot.send_message(id, messages.rating_to_developer.format(q.from_user.username, q.data, str(datetime.now())), parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(q.from_user.id, messages.rating_ty)
        await state.finish()
    except Exception as e:
        await state.finish()
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🆘 Допомога')
async def send_help(m: types.Message):
    await bot.send_message(m.from_user.id, messages.sos, reply_markup=kb.author, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
