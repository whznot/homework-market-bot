from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup


def get_create_task_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='создать заявку'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_numeric_task_navigation_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3'), KeyboardButton(text='4'),
                KeyboardButton(text='5'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
