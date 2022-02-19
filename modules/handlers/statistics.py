from modules.callbacks import dp, bot, types, FSMContext, sugar, logger, ParseMode
from datetime import datetime, timedelta
import pytz
import io
import matplotlib.pyplot as plt
from modules import messages

cooldown_h = 2
cooldown_m = 0


def generate_info(indexs):
    _min = 999
    _max = 0
    for index in indexs:
        if index > _max: _max = index
        if index < _min: _min = index
        mid = round(sum(indexs) / len(indexs), 1)
    return [_min, mid, _max]


@dp.message_handler(text='📊 Статистика')
async def statistics(m: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            try:
                if (timedelta(hours=cooldown_h, minutes=cooldown_m) - (
                        datetime.now(tz=pytz.timezone("Europe/Kiev")) - data['chart-last-time'])) <= timedelta(hours=0, minutes=0, seconds=0):
                    sugars = sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][
                        f'{datetime.now().day}']
                    time_list = []
                    index_list = []

                    for item in sugars:
                        time_list.append(str(item).replace('-', ':'))
                        index_list.append(float(str(sugars[item])))
                    with io.BytesIO() as buf:
                        buf.flush()
                        plt.plot(time_list, index_list)
                        plt.savefig(buf, format='png')
                        plt.clf()
                        buf.seek(0)
                        await bot.send_photo(m.chat.id, buf, caption=f"{datetime.now().date()}")
                        buf.close()
                    data['chart-last-time'] = datetime.now(tz=pytz.timezone("Europe/Kiev"))
                else:
                    wait_time = timedelta(hours=cooldown_h, minutes=cooldown_m) - (
                            datetime.now(tz=pytz.timezone("Europe/Kiev")) - data['chart-last-time'])
                    await bot.send_message(m.from_user.id, messages.waite_add_sugar.format(
                        f'{str(wait_time).split(":")[0]}:{str(wait_time).split(":")[1]}:{str(wait_time).split(":")[2].split(".")[0]}',
                        'годину' if timedelta(hours=2) > wait_time > timedelta(
                            hours=1) else 'хвилин' if wait_time >= timedelta(minutes=4) else "хвилини"),
                                           parse_mode=ParseMode.MARKDOWN)
            except KeyError:
                sugars = sugar[m.from_user.id]['sugars'][f'{datetime.now().year}'][f'{datetime.now().month}'][
                    f'{datetime.now().day}']
                time_list = []
                index_list = []
                for item in sugars:
                    time_list.append(str(item).replace('-', ':'))
                    index_list.append(float(str(sugars[item])))
                with io.BytesIO() as buf:
                    buf.flush()
                    plt.plot(time_list, index_list)
                    plt.savefig(buf, format='png')
                    plt.clf()
                    buf.seek(0)
                    info = generate_info(indexs=index_list)
                    await bot.send_photo(m.chat.id, buf, caption=messages.statistics.format(datetime.now().date(), info[2], info[1], info[0]), parse_mode=ParseMode.MARKDOWN)
                    buf.close()
                data['chart-last-time'] = datetime.now(tz=pytz.timezone("Europe/Kiev"))
    except Exception as e:
        logger.error(e.__class__.__name__ + ': ' + str(e))
