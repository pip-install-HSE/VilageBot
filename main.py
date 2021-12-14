import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import keyboards as kb
import messages as ms
import utils

load_dotenv()

bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(ms.start, reply_markup=kb.start_keyboard)


@dp.message_handler(Text(equals="Разовый пропуск"))
async def process_one_time_pass(message: types.Message):
    await message.answer(ms.one_time_pass, reply_markup=kb.help_car_keyboard)


@dp.message_handler(Text(equals="Сообщить о проблеме"))
async def process_problem(message: types.Message):
    await message.answer(ms.problem)


@dp.message_handler(Text(equals="Другое"))
async def process_other(message: types.Message):

    await message.answer(ms.other, reply_markup=kb.other_keyboard)


@dp.message_handler(Text(equals="Выпустить пропуск"))
async def process_issue_a_pass(message: types.Message):
    await message.answer(ms.issue_a_pass, reply_markup=kb.pass_keyboard)


@dp.message_handler(Text(equals="Автомобиля"))
async def process_car_pass(message: types.Message):
    await message.answer(ms.car_pass, reply_markup=kb.help_car_keyboard)


@dp.message_handler(Text(equals="Человека"))
async def process_human_pass(message: types.Message):
    await message.answer(ms.human_pass)


@dp.message_handler(Text(equals="Временный"))
async def process_time_pass(message: types.Message):
    await message.answer(ms.time_pass, reply_markup=kb.date_keyboard)


@dp.message_handler(Text(equals="Постоянный"))
async def process_full_time_pass(message: types.Message):
    await message.answer(f"Создан пропуск для: {message.from_user.first_name}")


@dp.message_handler()
async def process_one_time_pass_name(message: types.Message):
    await message.answer(ms.one_time_pass_name, reply_markup=kb.help_passname_keyboard)


@dp.message_handler()
async def process_type_of_pass(message: types.Message):
    await message.answer(ms.type_of_pass, reply_markup=kb.do_pass_keyboard)


@dp.message_handler()
async def process_enter_address(message: types.Message):
    await message.answer(ms.address_msg, reply_markup=kb.address_keyboard)


@dp.message_handler(Text(equals="Другой адрес"))
async def process_full_time_pass(message: types.Message):
    await message.answer("Введите адрес")


if __name__ == '__main__':
    executor.start_polling(dp)
