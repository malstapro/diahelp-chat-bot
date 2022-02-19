from aiogram import types
from modules.callbacks import dp, bot, user, sugar, logger, finish_state, FSMContext, ParseMode
import modules.messages as messages
import modules.keyboards as kb

@dp.message_handler(commands=['del'])
async def delete_user(m: types.Message):
    try:
        user[m.from_user.id].delete()
        sugar[m.from_user.id].delete()
        await bot.send_message(m.from_user.id, "Користувач успішно видален з бази даних!",
                               reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logger.error(e)


@dp.message_handler(lambda d: d.text == "Відміна" or d.text == 'відміна' or d.text == 'cancel' or d.text == '/cancel',
                    state="*")
async def cancel(m: types.Message, state: FSMContext):
    if m.text == "Відміна" or m.text == 'відміна' or 'cancel' in m.text:
        await finish_state(state)
        await bot.send_message(m.from_user.id, messages.canceled,
                               reply_markup=kb.main_keyboard_admin if user[m.from_user.id][
                                   'is_admin'] else kb.main_keyboard)
    else:
        pass


@dp.message_handler(commands=['about'], state='*')
async def send_about(m: types.Message, state: FSMContext):
    await bot.send_message(m.from_user.id, messages.about)


@dp.message_handler(commands=['help'], state='*')
async def send_help(m: types.Message):
    await bot.send_message(m.from_user.id, messages._help, reply_markup=kb.author, parse_mode=ParseMode.MARKDOWN,
                           disable_web_page_preview=True)


@dp.message_handler(commands=['menu'])
async def menu(m: types.Message, state: FSMContext):
    await finish_state(state)
    await bot.send_message(m.from_user.id, 'Меню', reply_markup=kb.main_keyboard_admin if user[m.from_user.id][
        'is_admin'] else kb.main_keyboard)
