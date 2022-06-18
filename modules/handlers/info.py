from modules.callbacks import dp, bot, types, FSMContext, ParseMode, finish_state, logger
from datetime import datetime
from modules import messages
from modules import keyboards as kb
from modules.states import Rating


@dp.message_handler(text='ℹ Інформація')
async def information(m: types.Message):
    await bot.send_message(m.from_user.id, messages.accessible_info, reply_markup=kb.info,
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text='👤 Творець')
async def author(m: types.Message):
    await bot.send_message(m.from_user.id, messages.author, parse_mode=ParseMode.MARKDOWN,
                           disable_web_page_preview=True)


@dp.message_handler(text='⭐ Оцінити бота')
async def rating(m: types.Message):
    await Rating.send_rating.set()
    await bot.send_message(m.from_user.id, messages.rating_choice, reply_markup=kb.rating)


@dp.callback_query_handler(state=Rating.send_rating)
async def send_rating(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    try:
        id = 111
        await bot.send_message(id,
                               messages.rating_to_developer.format(q.from_user.username, q.data, str(datetime.now())),
                               parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(q.from_user.id, messages.rating_ty)
        await finish_state(state)
    except Exception as e:
        await finish_state(state)
        logger.error(e.__class__.__name__ + ': ' + str(e))


@dp.message_handler(text='🆘 Допомога')
async def send_help(m: types.Message):
    await bot.send_message(m.from_user.id, messages.sos, reply_markup=kb.author, parse_mode=ParseMode.MARKDOWN,
                           disable_web_page_preview=True)
