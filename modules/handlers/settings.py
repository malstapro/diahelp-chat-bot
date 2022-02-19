from modules.callbacks import dp, bot, logger, types, FSMContext, ParseMode, sugar, user, defaultSugar, finish_state
from modules import messages
from modules import keyboards as kb
from modules.states import Settings


@dp.message_handler(text='⚙ Налаштування')
async def settings_processing(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible_settings, reply_markup=kb.settings,
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text='🗑 Видалити показники цукру')
async def clear_sugar_processing(m: types.Message):
    await Settings.clear_sugar_confirm.set()
    await bot.send_message(m.from_user.id, messages.settings_clear_sug_conf, reply_markup=kb.confirm,
                           parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(state=Settings.clear_sugar_confirm)
async def clear_sugar(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        if q.data == 'yes':
            sugar[q.from_user.id].delete()
            sugar[q.from_user.id] = defaultSugar
            sugar[q.from_user.id].commit()
            await finish_state(state)
            await bot.send_message(q.from_user.id, messages.data_deleted, reply_markup=kb.settings)
        elif q.data == 'no':
            await finish_state(state)
            await bot.send_message(q.from_user.id, messages.canceled, reply_markup=kb.settings)
    except Exception as e:
        await finish_state(state)
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🔄 Змінити одиниці вимірювання')
async def change_units_processing(m: types.Message):
    await Settings.change_units_confirm.set()
    await bot.send_message(m.from_user.id, messages.units_change_warn, reply_markup=kb.confirm,
                           parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(state=Settings.change_units_confirm)
async def change_units_confirm_processing(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        if q.data == 'yes':
            await Settings.change_units.set()
            await bot.send_message(q.from_user.id, messages.choice_units, reply_markup=kb.reg)
        elif q.data == 'no':
            await finish_state(state)
            await bot.send_message(q.from_user.id, messages.canceled, reply_markup=kb.settings)
    except Exception as e:
        await finish_state(state)
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.callback_query_handler(state=Settings.change_units)
async def change_units(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        units = user[q.from_user.id]['units']
        if q.data == units:
            await finish_state(state)
            await bot.send_message(q.from_user.id, messages.units_identical_error, reply_markup=kb.settings)
        else:
            sugar[q.from_user.id].delete()
            sugar[q.from_user.id] = defaultSugar
            sugar[q.from_user.id].commit()
            user[q.from_user.id]['units'] = q.data
            user[q.from_user.id].commit()
            await finish_state(state)
            await bot.send_message(q.from_user.id, messages.units_changed, reply_markup=kb.settings)
    except Exception as e:
        await finish_state(state)
        logger.error(e.__class__.__name__ + ': ' + str(e))
