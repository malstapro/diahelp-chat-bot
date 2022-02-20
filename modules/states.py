from aiogram.dispatcher.filters.state import StatesGroup, State


class Sugar(StatesGroup):
    add_to_db = State()
    mid_sugar = State()
    all_sugar = State()


class Settings(StatesGroup):
    clear_sugar_confirm = State()
    change_units_confirm = State()
    change_units = State()


class Rating(StatesGroup):
    send_rating = State()


class Convert(StatesGroup):
    mg_to_moll_state = State()
    moll_to_mg_state = State()


class FoodSearch(StatesGroup):
    search = State()


class Mailing(StatesGroup):
    mailing = State()
    now = State()
    later = State()
    later_set_time = State()
