from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import DataBase
import config
from datetime import datetime

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    sex = State()
    typ = State()
    insulins = State()
    units = State()
    addsug = State()
    sug = State()
    clearsug = State()
    deluser = State()
    settings = State()
    rate = State()
    question = State()
    answer = State()
    answersend = State()
    mgtomol = State()
    moltomg = State()


class Mailing(StatesGroup):
    do = State()
    all = State()
    insulins = State()
    sex = State()
    type = State()
    units = State()
    age = State()


user = DataBase('users', 'users', config.MONGO_TOKEN, '_id')
defaltUser = {
    'sex': None,
    'type': None,
    'weight': None,
    'height': None,
    'age': None,
    'insulins': [None, None],
    'units': None
}
sug = DataBase('sugars', 'sugars', config.MONGO_TOKEN, '_id')
defaltSug = {
    'sugers': []
}

@dp.message_handler(commands=['del'])
async def delete_user(message: types.Message):
    user[message.from_user.id].delete_user()
    sug[message.from_user.id].delete_user()
    await message.answer("Пользователь успешно удален из базы данных!")


@dp.message_handler(commands=['menu','меню'])
async def menu(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer('Меню',
                         reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                             [types.KeyboardButton(text="📊 Статистика")],
                             [types.KeyboardButton(text="🍬 Сахар")],
                             [types.KeyboardButton(text="⚙ Настройки")],
                             [types.KeyboardButton(text="ℹ Информация")]
                         ]))


@dp.message_handler(commands=['mailing'])
async def mailing(msg: types.Message):
    if (msg.from_user.id in config.ADMINS):
        await Mailing.do.set()
        await msg.answer('Выбирите тип рассылки',
                         reply_markup=types.InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [types.InlineKeyboardButton('Все', callback_data='all')],
                                 [types.InlineKeyboardButton('Инсулин', callback_data='insulin')],
                                 [types.InlineKeyboardButton('Пол', callback_data='sex')],
                                 [types.InlineKeyboardButton('Тип', callback_data='type')],
                                 [types.InlineKeyboardButton('Еденицы', callback_data='units')],
                                 [types.InlineKeyboardButton('Возраст', callback_data='age')],
                             ]
                         ))


@dp.callback_query_handler(state=Mailing.do)
async def mailing_do(q: types.InlineQueryResult, state: FSMContext):
    usrs = user[q.from_user.id].find()
    if q.data == 'all':
        for id in usrs:
            await bot.send_message(chat_id=id['_id'], text=f'ALL TEST {str(datetime.now())}')
    elif q.data == 'insulin':
        ids = []
        for i in usrs:
            if 'Insu' in i['insulins'] or 'Insul' in i['insulins']:
                ids.append(i['_id'])
        for id in ids:
            await bot.send_message(chat_id=id, text=f'INSULIN TEST {str(datetime.now())}')
    await state.finish()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await Form.sex.set()
    await message.answer("Здравствуйте!\n"
                         "Я бот помощник для людей болеющих сахарным диабетом\n"
                         "Я могу предоставить вам разнообразную полезную информацию"
                         "\nЧтобы узнать подробней, нажмите на кнопку *Помощь*."
                         "\n\n*САМОЛЕЧЕНИЕ МОЖЕТ НАВРЕДИТЬ ВАШЕМУ ЗДОРОВЬЮ!*", parse_mode="Markdown")

    reg_btns = [
        [types.InlineKeyboardButton('Мужчина', callback_data='male')],
        [types.InlineKeyboardButton('Женщина', callback_data='female')]
    ]
    reg_kb = types.InlineKeyboardMarkup(inline_keyboard=reg_btns)

    await message.answer("Для начала нужно пройти простую регистрацию\n\n"
                         "Выберите ваш пол:", reply_markup=reg_kb)
    user[message.from_user.id] = defaltUser
    user[message.from_user.id].save()
    sug[message.from_user.id] = defaltSug
    sug[message.from_user.id].save()


@dp.message_handler(content_types=['text'])
async def send_help(message: types.Message):
    if message.text == "📊 Статистика":
        usr = user[message.from_user.id]
        sex = "👨" if usr['sex'] == 'male' else "👧"
        typ = "Сахарный диабет 1 типа" if usr['type'] == 'type1' else "Сахарный диабет 2 типа"
        units = "мг/дл" if usr['units'] == 'mg' else "ммоль/л"
        maxsug = 0
        midsug = 0
        minsug = 630.63
        try:
            for i in sug[message.from_user.id]['sugers']:
                if i > maxsug:
                    maxsug = i
                if i < minsug:
                    minsug = i
            if maxsug == 0:
                maxsug = 'У вас еще нет показателей.'
            if minsug == 630.63:
                minsug = 'У вас еще нет показателей.'
            lst = []
            result = 0
            for i in sug[message.from_user.id]['sugers']:
                lst.append(float(i))
            for j in lst:
                result += j
            midsug = '{:.1f}'.format(result / len(lst))
        except ZeroDivisionError or TypeError:
            midsug = 'У вас еще нет показателей.'
        await message.answer(f"""
🔸 Пол: {sex}
🔸 {typ}
🔸 Возраст: _{usr['age']}_
🔸 Вес: _{usr['weight']} кг_
🔸 Рост: _{usr['height']} см_

🔸 Инсулины:
_{' | '.join(usr['insulins'])}_

🔸 Еденицы измерения:
_{units}_

🔸 Максимальный уровень сахара в крови:
_{maxsug}_

🔸 Средний уровень сахара в крови:
_{midsug}_

🔸 Минимальный уровень сахара в крови:
_{minsug}_
        """, parse_mode='Markdown')
    elif message.text == "🍬 Сахар":
        await Form.sug.set()
        await message.answer("Доступные команды", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔘 Средний показатель')],
                [types.KeyboardButton('🔘 Все показатели')],
                [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))
    elif message.text == "ℹ Информация":
        await message.answer("""Бот создан для ознакомления людей больных сахарным диабетом(далее пользователей)
с полезной информацией собранной из разных источников. 
                             
Создатели не несут отвественности
за любый действия пользователей. Информация не является 100% достоверной. 
                             
                             
САМОЛЕЧЕНИЕ МОЖЕТ НАВРЕДИТЬ ВАШЕМУ ЗДОРОВЬЮ!""",
                             reply_markup=types.ReplyKeyboardMarkup(
                                            keyboard=[
                                                [types.KeyboardButton('👤 Создатель')],
                                                [types.KeyboardButton('❓ Задать вопрос')],
                                                [types.KeyboardButton('⭐ Оставить отзыв')],
                                                [types.KeyboardButton('🔙 Назад')],
                                            ]
                                        ))
    elif message.text == "⚙ Настройки":
        await Form.settings.set()
        await message.answer("Настройки пользователя",
                             reply_markup=types.ReplyKeyboardMarkup(
                                 keyboard=[
                                     [types.KeyboardButton('Очистить показатели уровня сахара в крови')],
                                     [types.KeyboardButton('Удалить аккаунт пользователя')],
                                     [types.KeyboardButton('Назад')],
                                 ]
                             ))
    elif message.text == '👤 Создатель':
        await message.answer('Меня создал великолепный человек!'
                             '\nhttps://t.me/tesla33IO')
    elif message.text == '❓ Задать вопрос':
        await Form.question.set()
        await message.answer('Задайте любые интересующие вас вопросы в одном сообщение.')
    elif message.text == '⭐ Оставить отзыв':
        await message.answer('На сколько вы бы оценили работу бота?',
                             reply_markup=types.InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [types.InlineKeyboardButton('⭐', callback_data='rate1')],
                                     [types.InlineKeyboardButton('⭐⭐', callback_data='rate2')],
                                     [types.InlineKeyboardButton('⭐⭐⭐', callback_data='rate3')],
                                     [types.InlineKeyboardButton('⭐⭐⭐⭐', callback_data='rate4')],
                                     [types.InlineKeyboardButton('⭐⭐⭐⭐⭐', callback_data='rate5')],
                                 ]
                             ))
    elif message.text == '🔙 Назад':
        await message.answer('Меню',
                         reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                             [types.KeyboardButton(text="📊 Статистика")],
                             [types.KeyboardButton(text="🍬 Сахар")],
                             [types.KeyboardButton(text="⚙ Настройки")],
                             [types.KeyboardButton(text="ℹ Информация")]
                         ]))


@dp.message_handler(state=Form.question)
async def question(msg: types.Message, state: FSMContext):
    question = msg.text
    await bot.send_message(chat_id=-1001388451272, text=f'{question}'
                                                   f'\n\nID: {msg.from_user.id}\n'
                                                   f'Имя пользователя: {msg.from_user.username}\n'
                                                   f'Время: {datetime.now()}', reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton('Ответить', callback_data='answer')],
            [types.InlineKeyboardButton('Закрыть', callback_data='close')],
        ]
    ))
    await msg.answer('Ваш вопрос доставлен моим администраторам, они его рассмотрят и постараются дать ответ.'
                     'Будьте терпеливыми.')
    await state.finish()


@dp.callback_query_handler()
async def answer(q, state: FSMContext):
    if q.data == 'answer':
        await Form.answersend.set()
        await bot.send_message(chat_id=-1001388451272, text='Пришлите ответ одним сообщением.'
                                                            'Например:')
        await bot.send_message(chat_id=-1001388451272, text='123401234|В сообщение нужно указать таким образом: ID пользователя'
                                                            'задавшего вопрос и сам ответ')
    elif q.data == 'close':
        await state.finish()
        await bot.send_message(chat_id=-1001388451272, text='Вопрос был закрыт.')
    elif q.data == 'rate1' or q.data == 'rate2' or q.data == 'rate3' or q.data == 'rate4' or q.data == 'rate5':
        await bot.send_message(chat_id=-1001388451272, text=f'Оценка: {q.data[-1]}'
                                                       f'\n\nID: {q.from_user.id}\n'
                                                       f'Имя пользователя: {q.from_user.username}\n'
                                                       f'Время: {datetime.now()}')
        await bot.send_message(chat_id=q.from_user.id, text='Спасибо за отзыв!')
        await state.finish()


@dp.message_handler(state=Form.answersend)
async def sendans(msg: types.Message, state: FSMContext):
    try:
        uid = msg.text.split('|')
        await bot.send_message(chat_id=uid[0], text='На ваш вопрос был дан следующий ответ: '+uid[1])
        await state.finish()
    except Exception as e:
        await bot.send_message(chat_id=-1001388451272, text=str(e) + '\n\nПопробуйте еще раз')


@dp.message_handler(state=Form.settings)
async def settings(msg: types.Message, state: FSMContext):
    txt = msg.text
    if txt == 'Очистить показатели уровня сахара в крови':
        await Form.clearsug.set()
        await msg.answer(
            'Вы действительно хотите удалить все показатели?\n\nВсе данные будут потеряны без возможности восстановления!',
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton('Да, я уверенн(а)', callback_data='yes')],
                    [types.InlineKeyboardButton('Нет, я передумал(а)', callback_data='no')],
                ]
            ))
    elif txt == 'Удалить аккаунт пользователя':
        await Form.deluser.set()
        await msg.answer('Вы действительно хотите удалить аккаунт пользователя?\n\nВсе данные будут потеряны без возможности восстановления!',
                         reply_markup=types.InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [types.InlineKeyboardButton('Да, я уверенн(а)', callback_data='yes')],
                                 [types.InlineKeyboardButton('Нет, я передумал(а)', callback_data='no')],
                             ]
                         ))
    elif txt == 'Назад':
        await state.finish()
        await msg.answer('Меню',
                               reply_markup=types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🍬 Сахар")],
        [types.KeyboardButton(text="⚙ Настройки")],
        [types.KeyboardButton(text="ℹ Информация")]
    ]))


@dp.callback_query_handler(state=Form.deluser)
async def deluser(q: types.InlineQueryResult, state: FSMContext):
    if q.data == 'yes':
        await state.finish()
        user[q.from_user.id].delete_user()
        sug[q.from_user.id].delete_user()
        await bot.send_message(chat_id=q.from_user.id, text="Пользователь успешно удален из базы данных! Для регистрации напишите /start")
    elif q.data == 'no':
        await state.finish()
        await bot.send_message(chat_id=q.from_user.id, text='Операйия успешно отменена',
                               reply_markup=types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🍬 Сахар")],
        [types.KeyboardButton(text="⚙ Настройки")],
        [types.KeyboardButton(text="ℹ Информация")]
    ]))
    else:
        print("Error --- deluser")


@dp.callback_query_handler(state=Form.clearsug)
async def clearsug(q: types.InlineQueryResult, state: FSMContext):
    if q.data == 'yes':
        await state.finish()
        sug[q.from_user.id]['sugers'] = {}
        sug[q.from_user.id].save()
        await bot.send_message(chat_id=q.from_user.id, text="Показатели успешно удалены",
                               reply_markup=types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🍬 Сахар")],
        [types.KeyboardButton(text="⚙ Настройки")],
        [types.KeyboardButton(text="ℹ Информация")]
    ]))
    elif q.data == 'no':
        await state.finish()
        await bot.send_message(chat_id=q.from_user.id, text='Операйия успешно отменена',
                               reply_markup=types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🍬 Сахар")],
        [types.KeyboardButton(text="⚙ Настройки")],
        [types.KeyboardButton(text="ℹ Информация")]
    ]))
    else:
        print("Error --- clearsug")


@dp.message_handler(state=Form.sug)
async def sugg(msg: types.Message, state: FSMContext):
    if msg.text == '➕ Добавить':
        await Form.addsug.set()
        await msg.answer("Укажите уровень сахара в крови (Например: 3.5). "
                                                            "Для отмены действия, напишите *cancel*", parse_mode="Markdown")
    elif msg.text == "🔘 Средний показатель":
        try:
            lst = []
            result = 0
            for i in sug[msg.from_user.id]['sugers']:
                lst.append(float(i))
            for j in lst:
                result += j
            r = result / len(lst)
            await msg.answer('🔹 '+"{:.1f}".format(r)+' 🔹')
            await Form.sug.set()
            await msg.answer("Доступные команды",
                             reply_markup=types.ReplyKeyboardMarkup(
                                 keyboard=[
                                     [types.KeyboardButton('➕ Добавить')],
                                     [types.KeyboardButton('🔘 Все показатели')],
                                     [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                                     [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                                     [types.KeyboardButton('🔙 Назад')],
                                 ]
                             ))
        except ZeroDivisionError or TypeError:
            await msg.answer("У вас еще нет показателей.")
            await Form.sug.set()
            await msg.answer("Доступные команды", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))
    elif msg.text == "🔘 Все показатели":
        lst = []
        for i in sug[msg.from_user.id]['sugers']:
            lst.append(str(i))
        if len(lst) >= 1:
            await msg.answer('🔹 ' + ' | '.join(lst) + ' 🔹')
            await Form.sug.set()
            await msg.answer("Доступные команды",
                             reply_markup=types.ReplyKeyboardMarkup(
                                 keyboard=[
                                     [types.KeyboardButton('➕ Добавить')],
                                     [types.KeyboardButton('🔘 Средний показатель')],
                                     [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                                     [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                                     [types.KeyboardButton('🔙 Назад')],
                                 ]
                             ))
        elif len(lst) <= 0:
            await msg.answer("У вас еще нет показателей.")
            await Form.sug.set()
            await msg.answer("Доступные команды",
                                   reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))
        else:
            print('Error --- sugg')
            await state.finish()
    elif msg.text == "🔘 Из мг/дл в ммоль/л":
        await Form.mgtomol.set()
        await msg.answer('Укажите показатель в мг/дл:')
    elif msg.text == "🔘 Из ммоль/л в мг/дл":
        await Form.moltomg.set()
        await msg.answer('Укажите показатель в ммоль/л:')
    elif msg.text == "🔙 Назад":
        await state.finish()
        await msg.answer("Меню",
                               reply_markup=types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🍬 Сахар")],
        [types.KeyboardButton(text="⚙ Настройки")],
        [types.KeyboardButton(text="ℹ Информация")]
    ]))


@dp.message_handler(state=Form.mgtomol)
async def mgtomol(msg: types.Message, state: FSMContext):
    try:
        mg = float(msg.text)
        r = mg / 18
        await Form.sug.set()
        await msg.answer(f"{mg} мг/дл " + "≈ {:.1f} ммоль/л".format(r), reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔘 Средний показатель')],
                [types.KeyboardButton('🔘 Все показатели')],
                [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))
    except Exception as e:
        await Form.sug.set()
        await msg.answer('Вы допустили ошибку!', reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔘 Средний показатель')],
                [types.KeyboardButton('🔘 Все показатели')],
                [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))


@dp.message_handler(state=Form.moltomg)
async def moltomg(msg: types.Message, state: FSMContext):
    try:
        mol = float(msg.text)
        r = mol * 18
        await Form.sug.set()
        await msg.answer(f"{mol} ммоль/л " + "≈ {:.2f} мг/дл".format(r), reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔘 Средний показатель')],
                [types.KeyboardButton('🔘 Все показатели')],
                [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))
    except Exception as e:
        await Form.sug.set()
        await msg.answer('Вы допустили ошибку!', reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton('➕ Добавить')],
                [types.KeyboardButton('🔘 Средний показатель')],
                [types.KeyboardButton('🔘 Все показатели')],
                [types.KeyboardButton('🔘 Из мг/дл в ммоль/л')],
                [types.KeyboardButton('🔘 Из ммоль/л в мг/дл')],
                [types.KeyboardButton('🔙 Назад')],
            ]
        ))



@dp.message_handler(state=Form.addsug)
async def addsug(msg: types.Message, state: FSMContext):
    try:
        suger = float(msg.text)
        max = 0
        min = 0
        if (user[msg.from_user.id]['units'] == 'mol'):
            max = 35
            min = 1
        elif (user[msg.from_user.id]['units'] == 'mg'):
            max = 630.63
            min = 18.02
        if (suger >= min) and (suger <= max):
            s = sug[msg.from_user.id]['sugers']
            s.append(suger)
            sug[msg.from_user.id]['sugers'] = s
            sug[msg.from_user.id].save()
            await msg.answer("Показатель сохранен!")
            await state.finish()
        else:
            await Form.addsug.set()
            await msg.answer("Показатель указан неверно. Попробуйте еще раз")
    except ValueError:
        if msg.text == 'cancel' or msg.text == 'Cancel' or msg.text == 'Отмена' or msg.text == 'отмена':
            await state.finish()
            await msg.answer("Действие отменено")
            pass
        else:
            await Form.addsug.set()
            await msg.answer("Показатель указан неверно! Попробуйте еще раз. Обратите внимание число можно писать дробью, через точку (НЕ запятую)")


@dp.callback_query_handler(lambda query: query.data == "male" or query.data == "female", state=Form.sex)
async def set_sex(query):
    if query.data == "male":
        user[query.from_user.id]['sex'] = 'male'
        user[query.from_user.id].save()
    elif query.data == "female":
        user[query.from_user.id]['sex'] = 'female'
        user[query.from_user.id].save()
    else:
        print("Error -- setsex -- query!")

    btns = [
        [types.InlineKeyboardButton('1', callback_data='type1')],
        [types.InlineKeyboardButton('2', callback_data='type2')]
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=btns)
    await Form.typ.set()
    await bot.send_message(chat_id=query.from_user.id, text="Какой у вас тип диабета?", reply_markup=kb)


@dp.callback_query_handler(lambda query: query.data == "type1" or query.data == "type2", state=Form.typ)
async def set_type(query):
    if query.data == "type1":
        user[query.from_user.id]['type'] = 'type1'
        user[query.from_user.id].save()
    elif query.data == "type2":
        user[query.from_user.id]['type'] = 'type2'
        user[query.from_user.id].save()
    else:
        print("Error -- settype -- query!")

    await Form.weight.set()
    await bot.send_message(chat_id=query.from_user.id, text="Ваш вес? (кг)")


@dp.callback_query_handler(lambda query: query.data == "units_mg" or query.data == "units_mol", state=Form.units)
async def set_units(query, state: FSMContext):
    if query.data == "units_mg":
        user[query.from_user.id]['units'] = 'mg'
        user[query.from_user.id].save()
    elif query.data == "units_mol":
        user[query.from_user.id]['units'] = 'mol'
        user[query.from_user.id].save()
    else:
        print("Error -- setunits -- query!")
    await state.finish()
    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🍬 Сахар")],
        [types.KeyboardButton(text="⚙ Настройки")],
        [types.KeyboardButton(text="ℹ Информация")]
    ])
    await bot.send_message(chat_id=query.from_user.id, text="Регистрация успешно завершена!", reply_markup=kb)


@dp.message_handler(state=Form.weight)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        w = int(message.text)
        if (w <= 150) and (w >= 30):
            user[message.from_user.id]['weight'] = message.text
            user[message.from_user.id].save()
            await Form.height.set()
            await message.answer("Ваш рост? (см)")
        else:
            await message.answer("Вы допустили ошибку. Вес доолжен быть не менее 30 и не более 150 кг."
                                 " Если ваш вес меньше 30 или больше 150,"
                                 " настоятельно рекомендую вам обратиться"
                                 "к врачу.")
            await Form.weight.set()
    except ValueError:
        await Form.weight.set()
        await message.answer("Вес нужно указывать цифрами!")


@dp.message_handler(state=Form.height)
async def set_height(message: types.Message, state: FSMContext):
    try:
        h = int(message.text)
        if (h <= 250) and (h >= 40):
            user[message.from_user.id]['height'] = message.text
            user[message.from_user.id].save()
            await Form.age.set()
            await message.answer("Сколько вам лет?")
        else:
            await Form.height.set()
            await message.answer("Вы допустили ошибку. Рост должен находиться в пределах от 40 см до 250 см.")
    except ValueError:
        await Form.height.set()
        await message.answer("Рост нужно указывать цифрами!")


@dp.message_handler(state=Form.age)
async def set_age(message: types.Message, state: FSMContext):
    try:
        a = int(message.text)
        if (a <= 13):
            await message.answer("Использование бота доступно с 14 лет. Обратитесь к вашим родителям за помощью.")
            user[message.from_user.id].delete_user()
            sug[message.from_user.id].delete_user()
            await state.finish()
        elif (a > 100):
            await message.answer("Конечно, люди могуть жить и больше ста лет. Но это бывает очень редко. "
                                 "Обратитесь за помощью к Администратору(@tesla33IO)")
            user[message.from_user.id].delete_user()
            sug[message.from_user.id].delete_user()
            await state.finish()
        elif (a >= 14) and (a <= 100):
            user[message.from_user.id]['age'] = message.text
            user[message.from_user.id].save()
            await Form.insulins.set()
            await message.answer("Укажите ваши инсулины (через запятую)")
    except ValueError:
        await Form.age.set()
        await message.answer("Возраст нужно указывать цифрами!")


@dp.message_handler(state=Form.insulins)
async def set_insulins(message: types.Message, state: FSMContext):
    user[message.from_user.id]['insulins'] = message.text.split(',')
    user[message.from_user.id].save()
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton('мг/дл', callback_data='units_mg')],
        [types.InlineKeyboardButton('ммоль/л', callback_data='units_mol')]
    ])
    await Form.units.set()
    await message.answer("Выбирите еденицы измерения уровня сахара в крови", reply_markup=kb)


async def startup(dispatcher):
    print("== " + str(datetime.now()) + " ==")
    print(str(bot.id) + " :ID")

async def shutdown(dispatcher):
    print("== " + str(datetime.now()) + " ==")


executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
