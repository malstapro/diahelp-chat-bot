import json

from thefuzz import fuzz

from modules import messages
from modules.callbacks import dp, bot, finish_state, FSMContext, types, logger
from modules.states import FoodSearch


@dp.message_handler(text='🍎 Їжа')
async def food(m: types.Message, state: FSMContext):
    await FoodSearch.search.set()
    await bot.send_message(m.from_user.id, messages.select_food)


@dp.message_handler(state=FoodSearch.search)
async def food_search(m: types.Message, state: FSMContext):
    food_name = m.text
    maybe_result = []
    find = False
    try:
        with open('./data/food_data.json', 'r') as json_file:
            data = json.load(json_file)
            food_list = data['data']
        for food in food_list:
            # print(str(fuzz.token_sort_ratio(food_name, food)) + " - " + food)
            if fuzz.token_sort_ratio(food_name, food) >= 90:
                find = True
                nl = '\n'
                await m.answer(f'{food}\n{("Кількість на 1 ХО - " + food_list[food][0] + nl) if food_list[food][0] != "" else ""}Вага, об\'єм на 1 ХО - {food_list[food][1]}')
                await finish_state(state)
            elif fuzz.token_sort_ratio(food_name, food) >= 60:
                maybe_result.append(food)
            elif fuzz.token_sort_ratio(food_name, food.split(' ')[0]) >= 75:
                maybe_result.append(food)
        if not find:
            if len(maybe_result) > 0:
                nl = '\n'
                result = ''.join([f'{food}\n{("Кількість на 1 ХО - " + food_list[food][0] + nl) if food_list[food][0] != "" else ""}Вага, об\'єм на 1 ХО - {food_list[food][1]}\n\n'for food in food_list if food in maybe_result])
                await m.answer(result)
            else:
                await m.answer(messages.food_not_matched)
            await finish_state(state)
    except Exception as e:
        await finish_state(state)
        logger.error(e.__class__.__name__ + ': ' + str(e))
