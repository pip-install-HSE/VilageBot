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


# Моё лучшее творение - Вывод состояния и внутренних параметров
@dp.message_handler(Text(equals="Отладка"))
async def do_magic(message: types.Message):
    await message.answer(
        f"Имя: {User.get(User.tg_id == message.from_user.id).name}\n"
        f"Этап: {get_state(message)}\n"
        f"Номер Машины: {User.get(User.tg_id == message.from_user.id).car}\n"
        f"Создан: {User.get(User.tg_id == message.from_user.id).created_at}\n"
        f"Начало: {User.get(User.tg_id == message.from_user.id).pass_start}\n"
        f"Конец: {User.get(User.tg_id == message.from_user.id).pass_end}"
    )


# Обработка команды \start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user, _ = User.get_or_create(tg_id=message.from_user.id)
    set_state("start", message)
    await message.answer(f"Добро пожаловать в бота! Выберите: {get_state(message)}",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Разовый пропуск"))
                         .add(KeyboardButton("Сообщить о проблеме"))
                         .add(KeyboardButton("Другое"))
                         )


@dp.callback_query_handler(text='help_pass')
async def inline_kb_answer_car(query: types.CallbackQuery):
    await query.answer('Формат ввода: Иван Иванов')


@dp.callback_query_handler(text='help_car')
async def inline_kb_answer_car(query: types.CallbackQuery):
    await query.answer('Формат ввода: a000aa00')


@dp.message_handler(Text(equals="Разовый пропуск") | Text(equals="Разовый"),
                    lambda message: get_state(message) in ("start", "pass_type"))
async def process_one_time_pass(message: types.Message):
    set_state("one_time_pass", message)
    await message.answer(f"Введите номер машины {get_state(message)}",
                         reply_markup=InlineKeyboardMarkup()
                         .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                         )


@dp.message_handler(lambda message: get_state(message) == "one_time_pass")
async def process_one_time_pass_name(message: types.Message):
    car = message.text.replace(' ', '').upper()
    result = re.match(r'[А-Я]\d{3}[А-Я][А-Я]\d{2,3}', car)
    if result:
        User.update(car=car).where(User.tg_id == message.from_user.id).execute()
        set_state("one_time_pass_name", message)
        await message.answer(f"Назовите пропуск:",
                             reply_markup=InlineKeyboardMarkup()
                             .add(InlineKeyboardButton("Подсказка", callback_data='help_pass'))
                             )
    else:
        await message.answer(f"Введите номер машины в соответствии с шаблоном",
                             reply_markup=InlineKeyboardMarkup()
                             .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                             )


@dp.message_handler(lambda message: get_state(message) == "one_time_pass_name")
async def process_one_time_pass_end(message: types.Message):
    # Занесение в бд пропуска

    set_state("start", message)
    await message.answer(
        f"Создан пропуска для: \n {User.get(User.tg_id == message.from_user.id).car}\nНа сегодня")
    await message.answer(f"Добро пожаловать в бота! Выберите: ",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Разовый пропуск"))
                         .add(KeyboardButton("Сообщить о проблеме"))
                         .add(KeyboardButton("Другое"))
                         )


@dp.message_handler(lambda message: get_state(message) == "start",
                    Text(equals="Сообщить о проблеме")
                    )
async def process_problem(message: types.Message):
    set_state("problem", message)
    await message.answer(f"Введите описание проблемы: ")


@dp.message_handler(lambda message: get_state(message) == "start",
                    Text(equals="Другое"))
async def process_other(message: types.Message):
    set_state("other", message)
    await message.answer(f"Другое:{get_state(message)}",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Выпустить пропуск")))


@dp.message_handler(lambda message: get_state(message) == "start")
async def process_start_incorrect_input(message: types.Message):
    await message.answer(f"Пожалуйста, выберите из списка {get_state(message)}",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Разовый пропуск"))
                         .add(KeyboardButton("Сообщить о проблеме"))
                         .add(KeyboardButton("Другое"))
                         )


@dp.message_handler(lambda message: get_state(message) == "other",
                    Text(equals="Выпустить пропуск"))
async def process_issue_a_pass(message: types.Message):
    set_state("issue_a_pass", message)
    await message.answer(f"Пропуск для:{get_state(message)}",
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
    await message.answer(f"Введите номер авто: {get_state(message)}",
                         reply_markup=InlineKeyboardMarkup()
                         .add(InlineKeyboardButton("Подсказка!", callback_data='help_car'))
                         )


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass_car")
async def process_issue_a_pass_type(message: types.Message):
    User.update(car=message.text.upper()).where(User.tg_id == message.from_user.id).execute()
    set_state("pass_type", message)
    await message.answer("Тип пропуска",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Временный"))
                         .add(KeyboardButton("Постоянный"))
                         .add(KeyboardButton("Разовый"))
                         )


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass",
                    Text(equals="Человека"))
async def process_human_pass(message: types.Message):
    set_state("issue_a_pass_human", message)
    await message.answer(f"Введите имя и фамилию:")


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass_human")
async def process_issue_a_pass_type(message: types.Message):
    User.update(name=message.text).where(User.tg_id == message.from_user.id).execute()
    set_state("pass_type", message)
    await message.answer("Тип пропуска",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Временный")).
                         add(KeyboardButton("Постоянный")).
                         add(KeyboardButton("Разовый"))
                         )


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass")
async def process_issue_a_pass_incorrect_input(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка",
                         reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                         .add(KeyboardButton("Автомобиля"))
                         .add(KeyboardButton("Человека"))
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


@dp.message_handler(lambda message: get_state(message) == "time_pass",
                    Text(equals="Сегодня") or Text(equals="Завтра"))
async def process_time_pass_today_or_tomorrow(message: types.Message):
    if message.text == "Сегодня":
        set_state("today_time_pass", message)
        day = date.today()
        User.update(pass_start=day).where(User.tg_id == message.from_user.id).execute()
        await message.answer("Выберите дату окончания:",
                             reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                             .add(KeyboardButton("Сегодня"))
                             .add(KeyboardButton("Завтра"))
                             .add(KeyboardButton("Другая дата"))
                             )
    else:
        set_state("tomorrow_time_pass", message)
        day = date.today()  # Следующий день надо поставить
        User.update(pass_start=day).where(User.tg_id == message.from_user.id).execute()
        await message.answer("Выберите дату окончания:",
                             reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                             .add(KeyboardButton("Сегодня"))
                             .add(KeyboardButton("Завтра"))
                             .add(KeyboardButton("Другая дата"))
                             )


@dp.message_handler(lambda message: get_state(message) in ("issue_a_pass_human", "issue_a_pass_car"),
                    Text(equals="Постоянный"))
async def process_full_time_pass(message: types.Message):
    await message.answer(f"Создан пропуск для:")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
