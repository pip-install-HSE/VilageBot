import datetime
import os
import re
from peewee import *
from database import User, Problem
from dotenv import load_dotenv
from datetime import date
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
storage = MemoryStorage()

car_region = ["01", "02", "102", "70", "203", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15",
              "16", "116", "716", "17", "18", "19", "21", "121", "22", "23", "93", "123", "193", "24", "124", "25",
              "125", "26", "126", "27", "28", "29", "30", "31", "32", "33", "34", "134", "35", "36", "136", "37", "38",
              "138", "39", "40", "41", "42", "142", "43", "44", "45", "46", "47", "147", "48", "49", "50", "90", "150",
              "190", "750", "51", "52", "152", "53", "54", "154", "55", "56", "156", "57", "58", "59", "159", "60",
              "61", "161", "761", "62", "63", "163", "763", "64", "164", "65", "66", "96", "196", "67", "68", "69",
              "70", "71", "72", "73", "173", "74", "174", "75", "76", "77", "97", "99", "177", "197", "199", "777",
              "797", "799", "78", "98", "178", "198", "79", "82", "83", "86", "186", "87", "89", "92", "95"]

# Подключение к боту
bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=storage)

# Подключение к БД
db = PostgresqlDatabase(os.getenv('POSTGRES_DB'), port=5432,
                        host=os.getenv('POSTGRES_HOST'),
                        user=os.getenv('POSTGRES_USER'),
                        password=os.getenv('POSTGRES_PASSWORD'))
db.connect()
db.create_tables([User, Problem])


# Функция получения текущего состояния: Return <string>
def get_state(msg):
    return User.get(User.tg_id == msg.from_user.id).state


# Функция задающая состояние
def set_state(state_, msg):
    User.update(state=state_).where(User.tg_id == msg.from_user.id).execute()


def validate_license(car):
    try:
        if len(car) > 9:
            return False
        result = re.search(r'[АВЕКМНОРСТУХABEKMHOPCTYX]'
                           r'\d{3}'
                           r'[АВЕКМНОРСТУХABEKMHOPCTYX]{2}'
                           r'\d{2,3}',
                           car)
        if result:
            result = result.group()
            if result[6:] in car_region:
                if int(result[1:4]) > 0:
                    return True
        return False
    except:
        return False


# Задаём основные коман ды
async def set_default_commands(dpd):
    await dpd.bot.set_my_commands([
        types.BotCommand("start", "Приветственное сообщение"),
        types.BotCommand("other", "Другое"),
        types.BotCommand("one_time_pass", "Разовый пропуск"),
        types.BotCommand("problem", "Сообщить о проблеме"),
    ])


# Моё лучшее творение - Вывод состояния и внутренних параметров
@dp.message_handler(Text(equals="Отладка"))
async def do_magic(message: types.Message):
    await message.answer(
        f"Имя Разового пропуска: {User.get(User.tg_id == message.from_user.id).time_pass_name}\n"
        f"Этап: {get_state(message)}\n"
        f"Номер Машины: {User.get(User.tg_id == message.from_user.id).time_pass_car}\n"
        f"Ветка временного пропуска:\n"
        f"Начало: {User.get(User.tg_id == message.from_user.id).pass_start}\n"
        f"Конец: {User.get(User.tg_id == message.from_user.id).pass_end}\n"
        f"Кому пропуск: {User.get(User.tg_id == message.from_user.id).pass_who_show}\n"
        f"Название пропуска: {User.get(User.tg_id == message.from_user.id).pass_name}"
    )


# Обработка команды \start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user, _ = User.get_or_create(tg_id=message.from_user.id)
    set_state("start", message)
    await set_default_commands(dp)
    await message.answer(f"Добро пожаловать в бота!",
                         reply_markup=types.ReplyKeyboardRemove()
                         )


@dp.callback_query_handler(text='help_pass')
async def inline_kb_answer_car(query: types.CallbackQuery):
    await query.answer('Формат ввода: Машина для друга')


@dp.callback_query_handler(text='help_car')
async def inline_kb_answer_car(query: types.CallbackQuery):
    await query.answer('Формат ввода: a000aa00')


@dp.callback_query_handler(text='problem_help')
async def inline_kb_answer_car(query: types.CallbackQuery):
    await query.answer('Вода хлещет на потолок кухни')


@dp.callback_query_handler(text='skip')
async def inline_kb_answer_car(query: types.CallbackQuery):
    set_state("start", query)
    await query.message.answer(f"Создан пропуск для: \n "
                               f"{User.get(User.tg_id == query.from_user.id).time_pass_car}\n"
                               f"На сегодня")
    await query.message.answer(f"Выберите пункт меню",
                               reply_markup=types.ReplyKeyboardRemove()
                               )


@dp.message_handler(commands=['one_time_pass'])
async def process_one_time_pass(message: types.Message):
    set_state("one_time_pass", message)
    await message.answer(f"Введите номер машины",
                         reply_markup=InlineKeyboardMarkup()
                         .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                         )


@dp.message_handler(Text(equals="Разовый"),
                    lambda message: get_state(message) == "pass_type")
async def process_one_time_pass_2(message: types.Message):
    set_state("one_time_pass", message)

    await message.answer(f"Введите номер машины",
                         reply_markup=InlineKeyboardMarkup()
                         .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                         )


@dp.message_handler(lambda message: get_state(message) == "one_time_pass")
async def process_one_time_pass_name(message: types.Message):
    car = message.text.replace(' ', '').upper()
    if validate_license(car):
        User.update(time_pass_car=car).where(User.tg_id == message.from_user.id).execute()
        set_state("one_time_pass_name", message)

        msg = await message.answer(f"Назовите пропуск:",
                                   reply_markup=InlineKeyboardMarkup()
                                   .add(InlineKeyboardButton("Подсказка", callback_data='help_pass'))
                                   .add(InlineKeyboardButton("Пропустить", callback_data='skip'))
                                   )
        User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()
    else:
        msg = await message.answer(f"Введите номер машины в соответствии с шаблоном",
                                   reply_markup=InlineKeyboardMarkup()
                                   .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                                   )
        User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()


@dp.message_handler(lambda message: get_state(message) == "one_time_pass_name")
async def process_one_time_pass_end(message: types.Message):
    set_state("start", message)
    User.update(time_pass_name=message.text).where(User.tg_id == message.from_user.id).execute()
    await message.answer(f"Создан пропуск: \n"
                         f"{User.get(User.tg_id == message.from_user.id).time_pass_name}\n"
                         f"Для: \n "
                         f"{User.get(User.tg_id == message.from_user.id).time_pass_car}\n"
                         f"На сегодня")
    await message.answer(f"Выберите пункт меню",
                         reply_markup=types.ReplyKeyboardRemove()
                         )


@dp.message_handler(lambda message: get_state(message) == "start",
                    Text(equals="Сообщить о проблеме")
                    )
async def process_problem(message: types.Message):
    set_state("problem", message)
    await message.answer(f"Введите описание проблемы: ",
                         reply_markup=types.ReplyKeyboardRemove()
                         )


@dp.message_handler(commands=['other'])
async def process_other(message: types.Message):
    set_state("other", message)
    await message.answer(f"Другое:",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Выпустить пропуск")))


@dp.message_handler(lambda message: get_state(message) == "other",
                    Text(equals="Выпустить пропуск"))
async def process_issue_a_pass(message: types.Message):
    set_state("issue_a_pass", message)
    await message.answer(f"Пропуск для:",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Автомобиля"))
                         .add(KeyboardButton("Человека"))
                         )


@dp.message_handler(lambda message: get_state(message) == "other")
async def process_other_incorrect_input(message: types.Message):
    await message.answer(f"Пожалуйста, выберите из списка",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Выпустить пропуск"))
                         )


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass",
                    Text(equals="Автомобиля"))
async def process_car_pass(message: types.Message):
    set_state("issue_a_pass_car", message)
    User.update(pass_who=1).where(User.tg_id == message.from_user.id).execute()
    msg = await message.answer(f"Введите номер авто:",
                               reply_markup=InlineKeyboardMarkup()
                               .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                               )
    User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass_car")
async def process_issue_a_pass_type(message: types.Message):
    car = message.text.replace(' ', '').upper()
    if validate_license(car):
        User.update(pass_who_show=car).where(User.tg_id == message.from_user.id).execute()
        set_state("pass_type", message)
        await message.answer("Тип пропуска",
                             reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                             .add(KeyboardButton("Временный"))
                             .add(KeyboardButton("Постоянный"))
                             .add(KeyboardButton("Разовый"))
                             )
    else:
        msg = await message.answer(f"Введите номер машины в соответствии с шаблоном",
                                   reply_markup=InlineKeyboardMarkup()
                                   .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                                   )
        User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass",
                    Text(equals="Человека"))
async def process_human_pass(message: types.Message):
    set_state("issue_a_pass_human", message)
    await message.answer(f"Введите имя и фамилию:",
                         reply_markup=types.ReplyKeyboardRemove()
                         )


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass_human")
async def process_issue_a_pass_type(message: types.Message):
    User.update(pass_who_show=message.text).where(User.tg_id == message.from_user.id).execute()
    set_state("pass_type", message)
    await message.answer("Тип пропуска",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Временный"))
                         .add(KeyboardButton("Постоянный"))  # куда ведёт не знаем, что делает не понимаем
                         .add(KeyboardButton("Разовый"))
                         )


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass")
async def process_issue_a_pass_incorrect_input(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Автомобиля"))
                         .add(KeyboardButton("Человека"))
                         )


@dp.message_handler(lambda message: get_state(message) == "pass_type",
                    Text(equals="Постоянный"))
async def process_time_pass(message: types.Message):
    set_state("start", message)
    await message.answer("Красная ЗОНА НЕ ПОНИМАЕМ ШО ТВОРИМ")
    await message.answer("Выберите в меню",
                         reply_markup=types.ReplyKeyboardRemove()
                         )


@dp.message_handler(lambda message: get_state(message) == "pass_type",
                    Text(equals="Временный"))
async def process_time_pass(message: types.Message):
    set_state("time_pass", message)
    await message.answer("Выбор даты начала:",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Сегодня"))
                         .add(KeyboardButton("Завтра"))
                         .add(KeyboardButton("Другая дата"))
                         )


@dp.message_handler(lambda message: get_state(message) == "pass_type")
async def process_time_pass(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка:",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Временный"))
                         .add(KeyboardButton("Постоянный"))  # куда ведёт не знаем, что делает не понимаем
                         .add(KeyboardButton("Разовый"))
                         )


@dp.message_handler(lambda message: get_state(message) == "time_pass",
                    Text(equals=("Сегодня", "Завтра")))
async def process_time_pass_today_or_tomorrow(message: types.Message):
    if message.text == "Сегодня":
        set_state("today_time_pass", message)
        day = datetime.datetime.today()
        User.update(pass_start=day).where(User.tg_id == message.from_user.id).execute()
        await message.answer("Выберите дату окончания:",
                             reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                             .add(KeyboardButton("Сегодня"))
                             .add(KeyboardButton("Завтра"))
                             .add(KeyboardButton("Другая дата"))
                             )
    else:
        set_state("tomorrow_time_pass", message)
        day = datetime.datetime.today() + datetime.timedelta(days=1)
        User.update(pass_start=day).where(User.tg_id == message.from_user.id).execute()
        await message.answer("Выберите дату окончания:",
                             reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                             .add(KeyboardButton("Завтра"))
                             .add(KeyboardButton("Другая дата"))
                             )


@dp.message_handler(lambda message: get_state(message) in ("today_time_pass", "tomorrow_time_pass"),
                    Text(equals="Завтра"))
async def process_time_pass_tomorrow_end(message: types.Message):
    set_state("finishing_time_pass", message)
    day = datetime.datetime.today() + datetime.timedelta(days=1)
    User.update(pass_end=day).where(User.tg_id == message.from_user.id).execute()
    msg = await message.answer("Введите название для пропуска",
                               reply_markup=InlineKeyboardMarkup()
                               .add(InlineKeyboardButton("Подсказка!", callback_data='help_pass'))
                               )
    User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()


@dp.message_handler(lambda message: get_state(message) == "today_time_pass",
                    Text(equals="Сегодня"))
async def process_time_pass_today_end(message: types.Message):
    set_state("finishing_time_pass", message)
    day = datetime.datetime.today()
    User.update(pass_end=day).where(User.tg_id == message.from_user.id).execute()
    msg = await message.answer("Введите название для пропуска",
                               reply_markup=InlineKeyboardMarkup()
                               .add(InlineKeyboardButton("Подсказка!", callback_data='help_pass'))
                               )
    User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()


@dp.message_handler(lambda message: get_state(message) == "finishing_time_pass")
async def process_time_pass_finishing(message: types.Message):
    set_state("start", message)
    User.update(pass_name=message.text).where(User.tg_id == message.from_user.id).execute()
    await message.answer(f"Создан пропуск:\n"
                         f"{message.text}\n"
                         f"Для: {User.get(User.tg_id == message.from_user.id).pass_who_show}\n"
                         f"C: {User.get(User.tg_id == message.from_user.id).pass_start}\n"
                         f"По: {User.get(User.tg_id == message.from_user.id).pass_end}")
    await message.answer(f"Выберите пункт меню",
                         reply_markup=types.ReplyKeyboardRemove()
                         )


@dp.message_handler(lambda message: get_state(message) in ("time_pass", "today_time_pass", "tomorrow_time_pass"),
                    Text(equals="Другая дата"))
async def process_other_date(message: types.Message):
    await message.answer("Раздел в разработке, выберите сегодня или завтра.")


# Ветка проблемы
@dp.message_handler(commands="problem")
async def process_problem(message: types.Message):
    set_state("problem", message)
    msg = await message.answer("Введите описание проблемы",
                               reply_markup=InlineKeyboardMarkup()
                               .add(InlineKeyboardButton("Пример", callback_data='problem_help'))
                               )
    User.update(last_inline_message=msg.message_id).where(User.tg_id == message.from_user.id).execute()


@dp.message_handler(lambda message: get_state(message) == "problem")
async def process_set_problem(message: types.Message):
    set_state("choose_address", message)
    await message.answer("Выберете адрес\nНажмите скрепку 📎 и выберите \n\"Геопозиция\"",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Мой дом"))
                         .add(KeyboardButton("Моё местоположение"))
                         .add(KeyboardButton("Другой адрес"))
                         )


@dp.message_handler(lambda message: get_state(message) == "choose_address")
async def process_problem(message: types.Message):
    await message.answer("Выберете адрес\nНажмите скрепку 📎 и выберите \n\"Геопозиция\"",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Мой дом"))
                         .add(KeyboardButton("Моё местоположение"))
                         .add(KeyboardButton("Другой адрес"))
                         )


@dp.message_handler(lambda message: get_state(message) == "time_pass")
async def process_time_pass_incorrect_input(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка:",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Сегодня"))
                         .add(KeyboardButton("Завтра"))
                         .add(KeyboardButton("Другая дата"))
                         )


@dp.message_handler(lambda message: get_state(message) in ("today_time_pass", "tomorrow_time_pass"))
async def process_incorrect_input(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка:")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
