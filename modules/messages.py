canceled = 'Дія успішно скасована!'
sos = '''Якщо у вас є питання ви можете написати [творцеві](https://t.me/tesla33io) бота

Для відкриття меню: напишіть /menu
📊 Статистика - покаже вам основні дані які зберігає бот.
    
🍬 Цукор - дозволить вам провести різноманітні оперцаіі з показником рівня цукру в крові (збереження, середній показник і т.д.)
    
⚙ Налаштування - деякі налаштування аккаунта в боті
    
ℹ Інформація - тут ви можете побачити деяку інформацію про бота, автора, оцінити роботу бота або звернутися за допомогою.'''
_help = '''Голові команди:
_Деякі команди можна писати без \'/\'(слешу)_

`1` /menu - головне меню бота
`2` /about - деяка інформація про бота
`3` /help - виводить це повідомлення
`4 відміна(Відміна)` - ця команда може закінчити будьякий процес роботи з ботом(Наприклад:  якщо ви передумали змінювати одиниці вмірювання, ви можете написати *відміна*, і процес зміни одиниць вімірювання буде закінчено)

Детальну інформацію про кнопки головного меню, можна дізнатися в меню *ℹ Інформація > 🆘 Допомога*

Якщо у вас виникли якісь труднощі, або бот, на вашу думку, пряцює не правильно (або, якщо ви знайшли помилки в теексті), будьласка зверніться до [твроця](https://t.me/tesla33io)

Якщо у вас є якісь ідеї для покращення бота, ви також можете написати про це [творцю бота](https://t.me/tesla33io)
'''
about = 'Цей бот створений для допомги людям хворим на цукровий діабет у повсяк-дневному житті\n\nCopyright © @tesla33IO 2020 - 2021'
welcome = 'Вітаємо! Я бот помічник для людей які хворіють на цукровий діабет\n\n*САМОЛІКУВАННЯ МОЖЕ ЗАШКОДИТИ ВАШОМУ ЗДОРОВ\'Ю!*'
reg = 'Для початку потрібно пройти просту реєстрацію.\n\nВиберіть зручні для вас одиниці вимірювання рівня цукру в крові:'
choice_units = 'Виберіть зручні для вас одиниці вимірювання рівня цукру в крові:'
end_reg = 'Реєстрація успішно закінчена!'
accessible = 'Доступні команди:'
accessible_sugar = '''Доступні команди:

*➕ Додати показник* - зберігає показник рівня цукру в крові в базі даних

*🔘 Середній показник* - показує середній показник цукру за день або місяць

*🔘 Усі показники* - показує усі показники цукру за день або місяць

*мг/дл ➡ ммоль/л* - переводить рівень цукру в крові з одних одиниць вімірювання до інших
*ммоль/л ➡ мг/дл* - теж саме, тільки навпаки
'''
accessible_info = '''Доступні команди:

*👤 Творець* - коротка інформація про творця

*⭐ Оцінити бота* - ця кнопка дає змогу оцінити роботу бота

*🆘 Допомога* - деяка інформація про роботу з ботом
'''
accessible_settings = '''Доступні команди:

*🗑 Видалити показники цукру* - видаляє усі показники цукру записані в базі даних

*🔄 Змінити одиниці вимірювання* - зміна одиниць вимірювання

_Відновити показники неможливо!_
'''
statistics = '''Статистика за сьогодняшній день:

🔸Максимальний показник цукру: _{0}_
🔸Середній показник цукру: _{1}_
🔸Мінімальний показник цукру: _{2}_


Статистика за цей місяць:

🔸Максимальний показник цукру: _{3}_
🔸Середній показник цукру: _{4}_
🔸Мінімальний показник цукру: _{5}_
'''
not_found = 'Ви ще не маєте показників цукру'
send_sugar = 'Вкажіть рівень цукру в крові (Наприклад: {0}). Для скасування дії, напишіть *відміна*\n\n_Зверніть увагу, дробові числа пишуться через крапку, а не кому_'
value_error = 'Ви допустили помилку. Перевірте чи правильно ви ввели показник цукру. \n\n*Будьте уважні що дробове число потрібно вказувати через крапку, а не кому*'
to_big_value = 'Ви вказали за виский, або за низький показник. \n\n{0}'
index_saved = 'Показник збережено!'
if_too_low_index = 'Показник цукру нижче норми. Вам потрібно перекусити, щоб підвищити рівень цукру до нормального значення. ' \
                   'Я рекомендую вам випити соку, а потім через 15-20 хвилин додатково перекусити бутербродом або яблуком / бананом.'
if_too_high_index = 'Показник цукру вище норми. Вам потрібно знизити рівень цукру в крові. ' \
                    'Якщо ви не знаетет як це зробити в даній ситуації, вам обов\'язково потрібно проконсультуватися з вашим лікарем.'
mid_sug_choice = 'Будь ласка, виберіть період для визначення середнього показника:'
all_sug_choice = 'Будь ласка, виберіть період для виведеня даних:'
mid_sug_day = 'За сьогодні середній показник вашого рівня цукру: _{0}_'
mid_sug_month = 'За цей місяць середній показник вашого рівня цукру: _{0}_'
all_sug_day = 'Усі ваші показники за сьогодні:\n\n{0}'
all_sug_month = 'Усі ваші показники за цей місяць:\n\n{0}'
settings_main = 'Налаштування користувача:'
settings_clear_sug_conf = 'Ви дійсно бажаєте видалити всі показники цукру з бази дани?\n\n_Увага! Відновити показники НЕМОЖЛИВО!_'
data_deleted = 'Дані успішно видалені!'
units_identical_error = 'Помилка! Ці одиниці вімірювання є вашими основними.'
units_changed = 'Одиниці вимірювання успішно змінені!'
author = 'Мене створив [файний хлопець!](https://t.me/tesla33io)'
rating_choice = 'Як би ви оцінили роботу цього бота?'
rating_to_developer = 'Користувач *@{0}* оцінив роботу бота у *{1}* ⭐, о _{2}_'
rating_ty = 'Дуже дякую за ваш відгук, він допоможе мені покращити бота!'
units_change_warn = 'При зміні одиниць вимірювання, всі показники цукру будуть видалені!\nВи діясно бажаєте змінити одиниці вимірювання?\n\n_Увага! Відновити показники НЕМОЖЛИВО!_'
mg_to_moll_get = 'Вкажіть показник в мг/дл'
moll_to_mg_get = 'Вкажіть показник в ммоль/л'
mg_to_moll_result = '{} мг/дл ≈ {} ммоль/л'
moll_to_mg_result = '{} ммоль/л ≈ {} мг/дл'
waite_add_sugar = 'Зачекайте ще {0} {1}. Або ви можете купити платну підписку і користуватися ботом без обмежень'
select_food = 'Пришліть назву їжі, а я скажу вам скільки вона містить жирів, білків і вуглеводів'
