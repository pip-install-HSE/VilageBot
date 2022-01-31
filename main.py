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
start_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)\
    .add(one_time_pass).add(report_an_issue).add(other)

help_car_button = InlineKeyboardButton("Подсказка!", callback_data='help_car')
help_car_keyboard = InlineKeyboardMarkup().add(help_car_button)

help_passname_button = InlineKeyboardButton("Подсказка", callback_data='help_human')
help_passname_keyboard = InlineKeyboardMarkup().add(help_passname_button)

help_address_button = InlineKeyboardButton("Подсказка", callback_data='help_address')

car_button = KeyboardButton("Автомобиля")
human_button = KeyboardButton("Человека")
pass_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)\
    .add(car_button).add(human_button)

issue_a_pass_button = KeyboardButton("Выпустить пропуск")
other_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)\
    .add(issue_a_pass_button)

time_pass_button = KeyboardButton("Временный")
full_time_pass_button = KeyboardButton("Постоянный")
one_time_pass_button = KeyboardButton("Разовый")
do_pass_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)\
    .add(time_pass_button).add(full_time_pass_button).add(one_time_pass_button)

today_button = KeyboardButton("Сегодня")
tomorrow_button = KeyboardButton("Завтра")
other_date_button = KeyboardButton("Другая дата")
date_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)\
    .add(today_button).add(tomorrow_button).add(other_date_button)

my_house = KeyboardButton("Мой дом")
other_address = KeyboardButton("Другой Адрес")
address_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)\
    .add(my_house).add(other_address)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user, _ = User.get_or_create(tg_id=message.from_user.id)
    User.update(state=0).where(User.tg_id == user.tg_id).execute()
    await message.answer((f"НЕДобро пожаловать в бота! Выберите:{User.get(User.tg_id == message.from_user.id).tg_id}"), reply_markup=start_keyboard)


@dp.message_handler(Text(equals="Разовый пропуск"))
async def process_one_time_pass(message: types.Message):
    await message.answer("Введите номер машины", reply_markup=help_car_keyboard)


@dp.message_handler(Text(equals="Сообщить о проблеме"))
async def process_problem(message: types.Message):
    await message.answer("Введите описание проблемы:")


@dp.message_handler()
async def process_problem(message: types.Message):
    await message.answer("Введите адрес:", reply_markup=address_keyboard)


@dp.message_handler(Text(equals="Другое"))
async def process_other(message: types.Message):
    await message.answer("Другое:", reply_markup=other_keyboard)


@dp.message_handler()
async def process_other(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка", reply_markup=start_keyboard)


@dp.message_handler(Text(equals="Выпустить пропуск"))
async def process_issue_a_pass(message: types.Message):
    await message.answer("Пропуск для:", reply_markup=pass_keyboard)


@dp.message_handler()
async def process_other(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка", reply_markup=other_keyboard)


@dp.message_handler(Text(equals="Автомобиля"))
async def process_car_pass(message: types.Message):
    await message.answer("Введите номер авто:", reply_markup=help_car_keyboard)


@dp.message_handler(Text(equals="Человека"))
async def process_human_pass(message: types.Message):
    await message.answer("Введите имя и фамилию:")


@dp.message_handler()
async def process_other(message: types.Message):
    await message.answer("Пожалуйста, выберите из списка", reply_markup=pass_keyboard)


@dp.message_handler(Text(equals="Временный"))
async def process_time_pass(message: types.Message):
    await message.answer("Выбор даты начала:", reply_markup=date_keyboard)


@dp.message_handler(Text(equals="Постоянный"))
async def process_full_time_pass(message: types.Message):
    await message.answer(f"Создан пропуск для: {message.from_user.first_name}")


@dp.message_handler()
async def process_one_time_pass_name(message: types.Message):
    await message.answer("Назовите пропуск", reply_markup=help_passname_keyboard)


@dp.message_handler()
async def process_type_of_pass(message: types.Message):
    await message.answer("Тип пропуска", reply_markup=do_pass_keyboard)


@dp.message_handler()
async def process_enter_address(message: types.Message):
    await message.answer("Введите адрес:", reply_markup=address_keyboard)


@dp.message_handler(Text(equals="Другой адрес"))
async def process_full_time_pass(message: types.Message):
    await message.answer("Введите адрес")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)