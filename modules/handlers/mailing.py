from datetime import datetime

import aiogram.utils.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from modules import keyboards as kb
from modules import messages
from modules.callbacks import bot, dp, user, finish_state, scheduler, mailing_time
from modules.states import Mailing


@dp.message_handler(text='📬 Розсилання')
async def check_admin(m: types.Message):
    if user[m.from_user.id]['is_admin']:
        await bot.send_message(m.from_user.id, messages.mailing_choice, reply_markup=kb.mailing_time)
        await Mailing.mailing.set()
    else:
        return


@dp.callback_query_handler(state=Mailing.mailing,)
async def choice_mailing(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    if q.data == 'now':
        await bot.send_message(q.message.chat.id, messages.send_mailing_msg)
        await Mailing.now.set()
    elif q.data == 'later':
        await bot.send_message(q.message.chat.id, messages.mailing_time_choice)
        await Mailing.later_set_time.set()


@dp.message_handler(state=Mailing.later_set_time)
async def mailing_time_set(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        mailing_time[m.text] = {'sent': False}
        mailing_time[m.text].commit()
        data['time'] = m.text.split(':')
    await m.answer(messages.send_mailing_msg)
    await Mailing.later.set()


async def do_mailing_later(m: types.Message, state: FSMContext):
    users = user[m.from_user.id].load()
    for i in range(len(users)):
        try:
            user_id = users[i]['_id']
            await m.send_copy(user_id)
        except aiogram.utils.exceptions.BotBlocked:
            await finish_state(state)
    await finish_state(state)


@dp.message_handler(state=Mailing.later, content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.AUDIO, ContentType.VOICE])
async def mailing_later(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        scheduler.add_job(do_mailing_later, 'cron', start_date=datetime.now(), day=data['time'][0], hour=data['time'][1], minute=data['time'][2], args=(m, state,))
    await finish_state(state)


@dp.message_handler(state=Mailing.now, content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.AUDIO, ContentType.VOICE])
async def mailing(m: types.Message, state: FSMContext):
    users = user[m.from_user.id].load()
    for i in range(len(users)):
        try:
            user_id = users[i]['_id']
            await m.send_copy(user_id)
        except aiogram.utils.exceptions.BotBlocked:
            await finish_state(state)
    await finish_state(state)
