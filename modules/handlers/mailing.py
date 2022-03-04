from datetime import datetime
import calendar

import aiogram.utils.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from modules import keyboards as kb
from modules import messages
from modules.callbacks import bot, dp, user, finish_state, scheduler, mailing_time
from modules.states import Mailing


month_names = {1: 'Січень', 2: 'Лютий', 3: 'Березень', 4: 'Квітень', 5: 'Травень', 6: 'Червень', 7: 'Липень', 8: 'Серпень',
               9: 'Вересень', 10: 'Жовтень', 11: 'Листопад', 12: 'Грудень'}


@dp.message_handler(text='📬 Розсилання')
async def check_admin(m: types.Message):
    if user[m.from_user.id]['is_admin']:
        await bot.send_message(m.from_user.id, messages.mailing_choice, reply_markup=kb.mailing_time)
        await Mailing.mailing.set()
    else:
        return


@dp.callback_query_handler(state=Mailing.mailing)
async def choice_mailing(q: types.CallbackQuery, state: FSMContext):
    await q.answer()
    async with state.proxy() as data:
        if q.data == 'now':
            await bot.send_message(q.message.chat.id, messages.send_mailing_msg)
            await Mailing.now.set()
        elif q.data == 'later':
            await finish_state(state)
            month_calendar = calendar.monthcalendar(datetime.now().year, datetime.now().month)
            calendar_kb = types.InlineKeyboardMarkup(row_width=7)
            calendar_kb.row(types.InlineKeyboardButton(month_names[datetime.now().month], callback_data='none'))
            for week in month_calendar:
                calendar_kb.row()
                for day in week:
                    if day == 0:
                        calendar_kb.insert(types.InlineKeyboardButton('*', callback_data='none'))
                        continue
                    calendar_kb.insert(types.InlineKeyboardButton(str(day), callback_data=f'set_day_{str(day)}'))
            msg = await bot.send_message(q.message.chat.id, messages.lms_choice_day, reply_markup=calendar_kb)
            data['lms_msg'] = msg.message_id


@dp.callback_query_handler(lambda q: q.data.startswith('set_day_') or q.data == 'none', state='*')
async def lms_set_hour(q: types.CallbackQuery, state: FSMContext):
    if q.data == 'none':
        await q.answer()
        return
    day = q.data.split('_')[2]
    if int(day) >= int(datetime.now().day):
        await q.answer()
        hour_kb = types.InlineKeyboardMarkup(row_width=6)
        hour_kb.row()
        for hour in range(24):
            hour_kb.insert(types.InlineKeyboardButton(str(hour + 1), callback_data=f'set_hour_{str(hour + 1)}'))
        async with state.proxy() as data:
            data['day'] = day
            await bot.edit_message_text(messages.lms_choice_hour, q.message.chat.id, data['lms_msg'])
            await bot.edit_message_reply_markup(q.message.chat.id, data['lms_msg'], reply_markup=hour_kb)

    else:
        await q.answer(messages.lms_time_warning)


@dp.callback_query_handler(lambda q: q.data.startswith('set_hour_'), state='*')
async def lms_set_minute(q: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        hour = q.data.split('_')[2]
        if (int(data['day']) == int(datetime.now().day) and int(hour) >= int(datetime.now().hour)) or (int(data['day']) > int(datetime.now().day)):
            await q.answer()
            minute_kb = types.InlineKeyboardMarkup(row_width=3)
            minute_kb.row()
            for minute in range(0, 60, 5):
                minute_kb.insert(types.InlineKeyboardButton(str(minute), callback_data=f'set_minute_{str(minute)}'))
            data['hour'] = hour
            await bot.edit_message_text(messages.lms_choice_minute, q.message.chat.id, data['lms_msg'])
            await bot.edit_message_reply_markup(q.message.chat.id, data['lms_msg'], reply_markup=minute_kb)

        else:
            await q.answer(messages.lms_time_warning)


@dp.callback_query_handler(lambda q: q.data.startswith('set_minute_'), state='*')
async def lms(q: types.CallbackQuery, state: FSMContext):
    minute = q.data.split('_')[2]
    async with state.proxy() as data:
        if (int(data['day']) == int(datetime.now().day) and int(data['hour']) == int(datetime.now().hour) and int(minute) > int(datetime.now().minute)) or (int(data['day']) > int(datetime.now().day)):
            await q.answer()
            data['minute'] = minute
            await bot.edit_message_reply_markup(q.message.chat.id, data['lms_msg'], reply_markup=types.InlineKeyboardMarkup())
            await bot.edit_message_text(messages.send_mailing_msg, q.message.chat.id, data['lms_msg'])
            await Mailing.later.set()
        else:
            await q.answer(messages.lms_time_warning)


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
        scheduler.add_job(do_mailing_later, 'cron', start_date=datetime.now(), day=data['day'], hour=data['hour'], minute=data['minute'], args=(m, state,))
        await m.answer(messages.lms_set_time_done.format(data['day'], data['hour'], data['minute']))
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
