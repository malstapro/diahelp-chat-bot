from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton


main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(KeyboardButton('📊 Статистика'), KeyboardButton('🍬 Цукор'))
main_keyboard.row(KeyboardButton('⚙ Налаштування'), KeyboardButton('ℹ Інформація'))


sugar = ReplyKeyboardMarkup(resize_keyboard=True)
sugar.row(KeyboardButton('➕ Додати показник'))
sugar.row(KeyboardButton('🔘 Середній показник'), KeyboardButton('🔘 Усі показники'))
sugar.row(KeyboardButton('➡️ З мг/дл до ммоль/л'), KeyboardButton('➡️ З ммоль/л до мг/дл'))
sugar.row(KeyboardButton('🔙 Назад'))


info = ReplyKeyboardMarkup(resize_keyboard=True)
info.row(KeyboardButton('👤 Творець'), KeyboardButton('⭐ Оцінити бота'))
info.row(KeyboardButton('🆘 Допомога'))
info.row(KeyboardButton('🔙 Назад'))


settings = ReplyKeyboardMarkup(resize_keyboard=True)
settings.row(KeyboardButton('🗑 Видалити показники цукру'))
settings.row(KeyboardButton('🔄 Змінити одиниці вимірювання'))
settings.row(KeyboardButton('🔙 Назад'))


author = InlineKeyboardMarkup()
author.add(InlineKeyboardButton('Творець', url='https://t.me/tesla33io'))


reg = InlineKeyboardMarkup()
reg.add(InlineKeyboardButton('ммоль/л', callback_data='units_mol'))
reg.add(InlineKeyboardButton('мг/дл', callback_data='units_mg'))


period_sug_choice = InlineKeyboardMarkup()
period_sug_choice.add(InlineKeyboardButton('День', callback_data='midsug_day'))
period_sug_choice.add(InlineKeyboardButton('Місяць', callback_data='midsug_month'))


confirm = InlineKeyboardMarkup()
confirm.add(InlineKeyboardButton('Так', callback_data='yes'))
confirm.add(InlineKeyboardButton('Ні', callback_data='no'))


rating = InlineKeyboardMarkup()
rating.add(InlineKeyboardButton('⭐️⭐️⭐️⭐️⭐️', callback_data='5'))
rating.add(InlineKeyboardButton('⭐️⭐️⭐️⭐', callback_data='4'))
rating.add(InlineKeyboardButton('⭐️⭐️⭐', callback_data='3'))
rating.add(InlineKeyboardButton('⭐️⭐', callback_data='2'))
rating.add(InlineKeyboardButton('⭐', callback_data='1'))

