from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from modules.callbacks import bot, dp, user, finish_state
from modules import messages
from modules.states import Mailing


@dp.message_handler(text='📬 Розсилання')
async def check_admin(m: types.Message):
    if user[m.from_user.id]['is_admin']:
        await bot.send_message(m.from_user.id, messages.admin_check_true)
        await Mailing.mailing.set()
    else:
        return


@dp.message_handler(state=Mailing.mailing, content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.AUDIO, ContentType.VOICE])
async def mailing(m: types.Message, state: FSMContext):
    users = user[m.from_user.id].load()
    for i in range(len(users)):
        user_id = users[i]['_id']
        await m.send_copy(user_id)
    await finish_state(state)
