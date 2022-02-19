from modules.callbacks import dp, bot, logger, sugar, user, types, FSMContext, ParseMode, finish_state
import pytz
from datetime import datetime, timedelta
from modules import messages
from modules import keyboards as kb
from modules.states import Sugar, Convert
import asyncio


@dp.message_handler(text='🍬 Цукор')
async def sugar_processing(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible_sugar, reply_markup=kb.sugar,
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text='➕ Додати показник')
async def save_index(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            if (timedelta(minutes=5) - (
                    datetime.now(tz=pytz.timezone("Europe/Kiev")) - data['add-sugar-last-time'])) <= timedelta(minutes=0, seconds=0):
                await Sugar.add_to_db.set()
                _min = "81.08" if user[m.from_user.id]['units'] == 'units_mg' else "4.5"
                await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
            else:
                wait_time = timedelta(minutes=5) - (
                        datetime.now(tz=pytz.timezone("Europe/Kiev")) - data['add-sugar-last-time'])
                await bot.send_message(m.from_user.id, messages.waite_add_sugar.format(
                    f'{str(wait_time).split(":")[1]}:{str(wait_time).split(":")[2].split(".")[0]}',
                    'хвилини' if wait_time > timedelta(minutes=2) else 'хвилину' if wait_time > timedelta(
                        minutes=1) else 'секунд'), parse_mode=ParseMode.MARKDOWN)
        except KeyError:
            await Sugar.add_to_db.set()
            _min = "81.08" if user[m.from_user.id]['units'] == 'units_mg' else "4.5"
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Sugar.add_to_db)
async def add_to_db(m: types.Message, state: FSMContext):
    try:
        await finish_state(state)
        index = float(m.text.replace(',', '.'))
        _max = 0
        _min = 0
        # global units
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
            try:
                sugar[m.from_user.id]['sugars'][f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).year}'][
                    f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).month}'][
                    f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).day}'][
                    f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).hour}-{datetime.now(tz=pytz.timezone("Europe/Kiev")).minute}'] = str(
                    index)
                sugar[m.from_user.id].commit()
            except:
                try:
                    sugar[m.from_user.id]['sugars'][f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).year}'][
                        f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).month}'].update({
                        f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).day}': {
                            f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).hour}-{datetime.now(tz=pytz.timezone("Europe/Kiev")).minute}': str(
                                index)}})
                    sugar[m.from_user.id].commit()
                except:
                    try:
                        sugar[m.from_user.id]['sugars'][f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).year}'].update(
                            {f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).month}': {
                                f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).day}': {
                                    f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).hour}-{datetime.now(tz=pytz.timezone("Europe/Kiev")).minute}': str(
                                        index)}}})
                        sugar[m.from_user.id].commit()
                    except:
                        sugar[m.from_user.id]['sugars'].update({
                            f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).year}': {
                                f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).month}': {
                                    f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).day}': {
                                        f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).hour}-{datetime.now(tz=pytz.timezone("Europe/Kiev")).minute}': str(
                                            index)}}}})
                        sugar[m.from_user.id].commit()
            await bot.send_message(m.from_user.id, messages.index_saved)
            if units and index <= 72.07:
                await bot.send_message(m.from_user.id, messages.if_too_low_index)
            elif units and index >= 234.23:
                await bot.send_message(m.from_user.id, messages.if_too_high_index)
            if not units and index <= 4.0:
                await bot.send_message(m.from_user.id, messages.if_too_low_index)
            elif not units and index >= 11.0:
                await bot.send_message(m.from_user.id, messages.if_too_high_index)
            async with state.proxy() as data:
                data['add-sugar-last-time'] = datetime.now(tz=pytz.timezone("Europe/Kiev"))
        else:
            hint = "_Мінімальний показник для одиниць вимірювання_ *мг/дл* - _18.02, максимальний показник - 630.63_" if \
                user[m.from_user.id]['units'] == 'units_mg' \
                else "_Мінімальний показник для одиниць вимірювання_ *ммоль/л* - _1.0, максимальний показник - 35.0_"
            await bot.send_message(m.from_user.id, messages.to_big_value.format(hint), parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)
            _min = "63.06" if user[m.from_user.id]['units'] == 'units_mg' else "3.5"
            await bot.send_message(m.from_user.id, messages.send_sugar.format(_min), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(e.__class__.__name__ + ': ' + str(e))
        await finish_state(state)
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


@dp.message_handler(text='🔘 Середній показник')
async def middle_sugar_choice(m: types.Message):
    await Sugar.mid_sugar.set()
    await bot.send_message(m.from_user.id, messages.mid_sug_choice, reply_markup=kb.period_sug_choice)


@dp.callback_query_handler(state=Sugar.mid_sugar)
async def middle_sugar_processing(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    if q.data == 'midsug_day' or q.data == 'midsug_month':
        try:
            now_day = datetime.now(tz=pytz.timezone("Europe/Kiev")).day
            now_month = datetime.now(tz=pytz.timezone("Europe/Kiev")).month
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
                await bot.send_message(q.from_user.id, messages.mid_sug_day.format(middle_sugar_day),
                                       parse_mode=ParseMode.MARKDOWN)
            elif q.data == 'midsug_month':
                middle_sugar_all_month = 0
                for i in result:
                    middle_sugar_all_month += i
                middle_sugar_month = '{:.1f}'.format(middle_sugar_all_month / len(result))
                await bot.send_message(q.from_user.id, messages.mid_sug_day.format(middle_sugar_month),
                                       parse_mode=ParseMode.MARKDOWN)
            await finish_state(state)
        except Exception as e:
            await finish_state(state)
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
        now_day = datetime.now(tz=pytz.timezone("Europe/Kiev")).day
        now_month = datetime.now(tz=pytz.timezone("Europe/Kiev")).month
        now_year = datetime.now(tz=pytz.timezone("Europe/Kiev")).year
        _all = sugar[q.from_user.id]['sugars']
        if q.data == 'midsug_day':
            day_sugars = sugar[q.from_user.id]['sugars'][f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).year}'][
                f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).month}'][
                f'{datetime.now(tz=pytz.timezone("Europe/Kiev")).day}']
            for sug in day_sugars:
                result.append(f'🔸 {str(sug).replace("-", ":")} - {day_sugars[sug]}')
            async with state.proxy() as data:
                await bot.edit_message_text(messages.all_sug.format(
                    f'сьогодні ({now_day if len(str(now_day)) > 1 else "0" + str(now_day)}.{now_month if len(str(now_month)) > 1 else "0" + str(now_month)})',
                    '\n'.join(str(a) for a in result)), q.from_user.id, data['all_sug_msg'])
            await finish_state(state)
        elif q.data == 'midsug_month':
            mon_sugars = sugar[q.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}']
            for day in mon_sugars:
                for sug in mon_sugars[str(day)]:
                    result.append(
                        f'🔸 {datetime.now(tz=pytz.timezone("Europe/Kiev")).month}.{day} - {str(sug).replace("-", ":")} - {mon_sugars[str(day)][sug]}')
            async with state.proxy() as data:
                await bot.edit_message_text(messages.all_sug.format(
                    f'цей місяць ({now_month if len(str(now_month)) > 1 else "0" + str(now_month)}.{now_year})',
                    '\n'.join(str(a) for a in result)), q.from_user.id, data['all_sug_msg'])
            await finish_state(state)
    except Exception as e:
        await finish_state(state)
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
    await finish_state(state)


@dp.message_handler(text='ммоль/л ➡ мг/дл')
async def moll_to_mg_get(m: types.Message, state: FSMContext):
    await Convert.moll_to_mg_state.set()
    await bot.send_message(m.from_user.id, messages.moll_to_mg_get)


@dp.message_handler(state=Convert.moll_to_mg_state)
async def moll_to_mg_result(m: types.Message, state: FSMContext):
    moll = float(m.text)
    r = moll * 18
    await bot.send_message(m.from_user.id, messages.moll_to_mg_result.format(moll, '{:.1f}'.format(r)))
    await finish_state(state)
