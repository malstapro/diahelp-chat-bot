from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import DataBase
import config

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    insulins = State()
    units = State()


user = DataBase('test', 'users', config.MONGO_TOKEN, '_id')
defaltUser = {
    'sex': None,
    'type': None,
    'weight': None,
    'height': None,
    'age': None,
    'insulins': [None, None],
    'units': None
}
sug = DataBase('test', 'sugars', config.MONGO_TOKEN, '_id')
defaltSug = {
    'sugers': []
}
"""
'sex': None,   -- пол
'type': None,   -- тип диабета
'weight': None,   -- вес
'height': None,   -- рост
'age': None,   -- возраст
'insulins': [None, None],   -- список инсулинов
'units': None   -- еденицы измерения сахара мг/дл или ммоль/л.
"""


@dp.message_handler(commands=['del'])
async def delete_user(message: types.Message):
    user[message.from_user.id].delete_user()
    sug[message.from_user.id].delete_user()
    await message.answer("Пользователь успешно удален из базы данных!")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="Помощь")],
        [types.KeyboardButton(text="Статистика")],
        [types.KeyboardButton(text="Настройки")],
        [types.KeyboardButton(text="Информация")]
    ])

    await message.answer("Здравствуйте!\n"
                         "Я бот помощник для людей болеющих сахарным диабетом\n"
                         "Я могу предоставить вам разнообразную полезную информацию"
                         "\nЧтобы узнать подробней, нажмите на кнопку *Помощь*."
                         "\n\n*САМОЛЕЧЕНИЕ МОЖЕТ НАВРЕДИТЬ ВАШЕМУ ЗДОРОВЬЮ!*", parse_mode="Markdown", reply_markup=kb)

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

@dp.message_handler(commands=['sug'])
async def add_sug(message: types.Message):
    suger = message.get_args()
    sug[message.from_user.id]['sugers'] += suger
    sug[message.from_user.id].save()
    await message.answer("Показатель сохранен!")
@dp.message_handler(commands=['sugmid'])
async def show_sug(message: types.Message):
    lst = []
    result = 0
    for i in sug[message.from_user.id]['sugers']:
        lst.append(int(i))
    for j in lst:
        result += j
    await message.answer(result/len(lst))


@dp.message_handler(content_types=['text'])
async def send_help(message: types.Message):
    if message.text == "Помощь":
        kb = types.inline_keyboard.InlineKeyboardMarkup(inline_keyboard=[[types.inline_keyboard.InlineKeyboardButton("Таблица ХЕ", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Термины", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Ситуации", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Симптомы", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Контроль сахара", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Питание", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Инсулин", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Физ. нагрузка", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Повседневная жизнь", callback_data='test')],
                [types.inline_keyboard.InlineKeyboardButton("Графики", callback_data='test')]])
        await message.answer("КОМАНДЫ", reply_markup=kb)
    elif message.text == "Статистика":
        usr = user[message.from_user.id]
        sex = "Мужчина" if usr['sex'] == 'male' else "Женщина"
        typ = "Сахарный диабет 1 типа" if usr['type'] == 'type1' else "Сахарный диабет 2 типа"
        units = "мг/дл" if usr['units'] == 'mg' else "ммоль/л"
        await message.answer(f"""
Пол: {sex}
{typ}
Возраст: {usr['age']}
Вес: {usr['weight']}
Рост: {usr['height']}
Инсулины: {','.join(usr['insulins'])}
Еденицы измерения: {units}
        """)


@dp.callback_query_handler(lambda query: query.data == "test")
async def process_callback_1(query):
    await bot.answer_callback_query(callback_query_id=query.id, text="Coming soon...")
    pass


@dp.callback_query_handler(lambda query: query.data == "male" or query.data == "female")
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

    await bot.send_message(chat_id=query.from_user.id, text="Какой у вас тип диабета?", reply_markup=kb)


@dp.callback_query_handler(lambda query: query.data == "type1" or query.data == "type2")
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
    await bot.send_message(chat_id=query.from_user.id, text="Ваш вес?")


@dp.callback_query_handler(lambda query: query.data == "units_mg" or query.data == "units_mol", state=Form.units)
async def set_units(query):
    print("set units b")
    if query.data == "units_mg":
        user[query.from_user.id]['units'] = 'mg'
        user[query.from_user.id].save()
    elif query.data == "units_mol":
        user[query.from_user.id]['units'] = 'mol'
        user[query.from_user.id].save()
    else:
        print("Error -- setunits -- query!")
    await bot.send_message(chat_id=query.from_user.id, text="Регистрация успешно завершена!")


@dp.message_handler(state=Form.weight)
async def set_weight(message: types.Message, state: FSMContext):
    user[message.from_user.id]['weight'] = message.text
    user[message.from_user.id].save()
    await Form.height.set()
    await message.answer("Ваш рост?")


@dp.message_handler(state=Form.height)
async def set_weight(message: types.Message, state: FSMContext):
    user[message.from_user.id]['height'] = message.text
    user[message.from_user.id].save()
    await Form.age.set()
    await message.answer("Сколько вам лет?")


@dp.message_handler(state=Form.age)
async def set_weight(message: types.Message, state: FSMContext):
    user[message.from_user.id]['age'] = message.text
    user[message.from_user.id].save()
    await Form.insulins.set()
    await message.answer("Укажите ваши инсулины (через запятую)")


@dp.message_handler(state=Form.insulins)
async def set_weight(message: types.Message, state: FSMContext):
    user[message.from_user.id]['insulins'] = message.text.split(',')
    user[message.from_user.id].save()
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton('мг/дл', callback_data='units_mg')],
        [types.InlineKeyboardButton('ммоль/л', callback_data='units_mol')]
    ])
    await Form.units.set()
    await message.answer("Выбирите еденицы измерения уровня сахара в крови", reply_markup=kb)
    print("set weight")


executor.start_polling(dp, skip_updates=True)
