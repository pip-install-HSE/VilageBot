import os
import logging
import re
import asyncio
import requests
from peewee import *
from database import User, Problem
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

storage = MemoryStorage()

bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=storage)
db = PostgresqlDatabase(os.getenv('POSTGRES_DB'), port=5432,
                        host=os.getenv('POSTGRES_HOST'),
                        user=os.getenv('POSTGRES_USER'),
                        password=os.getenv('POSTGRES_PASSWORD'))
db.connect()
db.create_tables([User, Problem])

one_time_pass = KeyboardButton("Разовый пропуск")
report_an_issue = KeyboardButton("Сообщить о проблеме")
other = KeyboardButton("Другое")
start_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) \
                .add(one_time_pass).add(report_an_issue).add(other)

time_pass_button = KeyboardButton("Временный")
full_time_pass_button = KeyboardButton("Постоянный")
one_time_pass_button = KeyboardButton("Разовый")
do_pass_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) \
    .add(time_pass_button).add(full_time_pass_button).add(one_time_pass_button)

car_button = KeyboardButton("Автомобиля")
human_button = KeyboardButton("Человека")
pass_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) \
    .add(car_button).add(human_button)

help_car_button = InlineKeyboardButton("Подсказка!", callback_data='help_car')
help_car_keyboard = InlineKeyboardMarkup().add(help_car_button)

help_passname_button = InlineKeyboardButton("Подсказка", callback_data='help_pass')
help_passname_keyboard = InlineKeyboardMarkup().add(help_passname_button)

help_address_button = InlineKeyboardButton("Подсказка", callback_data='help_address')

issue_a_pass_button = KeyboardButton("Выпустить пропуск")
other_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) \
    .add(issue_a_pass_button)

today_button = KeyboardButton("Сегодня")
tomorrow_button = KeyboardButton("Завтра")
other_date_button = KeyboardButton("Другая дата")
date_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) \
    .add(today_button).add(tomorrow_button).add(other_date_button)

my_house = KeyboardButton("Мой дом")
other_address = KeyboardButton("Другой Адрес")
address_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) \
    .add(my_house).add(other_address)


def get_state(msg):
    return User.get(User.tg_id == msg.from_user.id).state


def set_state(state_, msg):
    User.update(state=state_).where(User.tg_id == msg.from_user.id).execute()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user, _ = User.get_or_create(tg_id=message.from_user.id)
    set_state("start", message)
    await message.answer(f"Добро пожаловать в бота! Выберите: {get_state(message)}",
                         reply_markup=start_keyboard)


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
                         reply_markup=help_car_keyboard)



@dp.message_handler(lambda message:   get_state(message) == "one_time_pass")
async def process_one_time_pass_name(message: types.Message):
    car = message.text.replace(' ', '').upper()
    result = re.match(r'[А-Я]\d{3}[А-Я][А-Я]\d{2,3}', car)
    if result:
        User.update(car=car).where(User.tg_id == message.from_user.id).execute()
        set_state("one_time_pass_name", message)
        await message.answer(
            f"{car}Назовите пропуск: {get_state(message)} {User.get(User.tg_id == message.from_user.id).car}",
            reply_markup=help_passname_keyboard)
    else:
        await message.answer(f"Введите номер машины в соответствии с шаблоном {get_state(message)}",
                             reply_markup=help_car_keyboard)


@dp.message_handler(lambda message: get_state(message) == "one_time_pass_name")
async def process_one_time_pass_end(message: types.Message):
    # Занесение в бд пропуска

    set_state("start", message)
    await message.answer(
        f"Создан пропуска для: \n {User.get(User.tg_id == message.from_user.id).car}\nНа сегодня")
    await message.answer(f"Добро пожаловать в бота! Выберите: {get_state(message)}",
                         reply_markup=start_keyboard)


@dp.message_handler(Text(equals="Сообщить о проблеме"),
                    lambda message: get_state(message) == "start")
async def process_problem(message: types.Message):
    set_state("problem", message)
    await message.answer(f"Введите описание проблемы: {get_state(message)}")


@dp.message_handler(Text(equals="Другое"),
                    lambda message: get_state(message) == "start")
async def process_other(message: types.Message):
    set_state("other", message)
    await message.answer(f"Другое:{get_state(message)}",
                         reply_markup=other_keyboard)


@dp.message_handler(lambda message: get_state(message) == "start")
async def process_start_incorrect_input(message: types.Message):
    await message.answer(f"Пожалуйста, выберите из списка {get_state(message)}",
                         reply_markup=start_keyboard)


@dp.message_handler(Text(equals="Выпустить пропуск"),
                    lambda message: get_state(message) == "other")
async def process_issue_a_pass(message: types.Message):
    set_state("issue_a_pass", message)
    await message.answer(f"Пропуск для:{get_state(message)}",
                         reply_markup=pass_keyboard)


@dp.message_handler(lambda message: get_state(message) == "other")
async def process_other_incorrect_input(message: types.Message):
    await message.answer(f"Пожалуйста, выберите из списка {get_state(message)}",
                         reply_markup=other_keyboard)


@dp.message_handler(Text(equals="Автомобиля"),
                    lambda message: get_state(message) == "issue_a_pass")
async def process_car_pass(message: types.Message):
    set_state("issue_a_pass_car", message)
    await message.answer(f"Введите номер авто: {get_state(message)}",
                         reply_markup=help_car_keyboard)


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass_car")
async def process_issue_a_pass_type(message: types.Message):
    User.update(car=message.text.upper()).where(User.tg_id == message.from_user.id).execute()
    set_state("pass_type", message)
    await message.answer(
        f"Тип пропуска {get_state(message)} {User.get(User.tg_id == message.from_user.id).car}",
        reply_markup=do_pass_keyboard)


@dp.message_handler(Text(equals="Человека"),
                    lambda message: get_state(message) == "issue_a_pass")
async def process_human_pass(message: types.Message):
    set_state("issue_a_pass_human", message)
    await message.answer(f"Введите имя и фамилию: {get_state(message)}")


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass_human")
async def process_issue_a_pass_type(message: types.Message):
    User.update(name=message.text).where(User.tg_id == message.from_user.id).execute()
    set_state("pass_type", message)
    await message.answer(
        f"Тип пропуска {get_state(message)} {User.get(User.tg_id == message.from_user.id).name}",
        reply_markup=do_pass_keyboard)


@dp.message_handler(lambda message: get_state(message) == "issue_a_pass")
async def process_issue_a_pass_incorrect_input(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка",
                         reply_markup=pass_keyboard)


@dp.message_handler(Text(equals="Временный"),
                    lambda message: get_state(message) in ("issue_a_pass_human", "issue_a_pass_car"))
async def process_time_pass(message: types.Message):
    set_state("time_pass", message)
    await message.answer("Выбор даты начала:",
                         reply_markup=date_keyboard)


@dp.message_handler(Text(equals="Постоянный"),
                    lambda message: get_state(message) in ("issue_a_pass_human", "issue_a_pass_car"))
async def process_full_time_pass(message: types.Message):
    await message.answer(f"Создан пропуск для: {message.from_user.first_name}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
