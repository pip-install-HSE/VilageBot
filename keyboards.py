from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

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

