from aiogram import Bot, Dispatcher, executor, types
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Здравствуйте!\n"
                         "Я бот помощник для людей болеющих сахарным диабетом\n"
                         "Я могу предоставить вам разнообразную полезную информацию"
                         "\nЧтобы узнать подробней, используйте команду - /help"
                         "\n\n*САМОЛЕЧЕНИЕ МОЖЕТ НАВРЕДИТЬ ВАШЕМУ ЗДОРОВЬЮ!*", parse_mode="Markdown")
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):

    btns = [[types.inline_keyboard.InlineKeyboardButton("Помощь",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Таблица ХЕ",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Термины",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Ситуации",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Симптомы",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Контроль сахара",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Питание",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Инсулин",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Физ. нагрузка",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Повседневная жизнь",callback_data='test')],
    [types.inline_keyboard.InlineKeyboardButton("Графики",callback_data='test')]]
    kb = types.inline_keyboard.InlineKeyboardMarkup(inline_keyboard=btns)

    await message.answer("КОМАНДЫ", reply_markup=kb)

    # await message.answer("*ПОМОЩЬ*\n"
    #                      "_Команды_:\n"
    #                      "/help\n"
    #                      "/hetable\n"
    #                      "/termin\n"
    #                      "/situation\n"
    #                      "/simptom\n"
    #                      "/suger\n"
    #                      "/food\_advice\n"
    #                      "/insulin\n"
    #                      "/exercises\n"
    #                      "/everyday\n"
    #                      "/get\_graph\n\n"
    #                      "Для более детальной информации про команду напишите"
    #                      "\n`/help [команда]`, где вместо `[команда]` вставьте интересующую вас команду",
    #                      parse_mode="Markdown")



@dp.callback_query_handler(lambda query: query.data == "test")
async def process_callback_1(query):
    await bot.answer_callback_query(callback_query_id=query.id,text="Coming soon...")
    pass

executor.start_polling(dp, skip_updates=True)