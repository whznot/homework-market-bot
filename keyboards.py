from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from telebot.types import InlineKeyboardButton


def get_create_task_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='Создать заявку'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_numeric_task_navigation_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3'), KeyboardButton(text='4'),
                KeyboardButton(text='5'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


task_callback = CallbackData("task", "action", "task_id")


def get_task_action_keyboard(task_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="✏️",
            callback_data=task_callback.new(action="edit", task_id=task_id)
        ),
        InlineKeyboardButton(
            text="🗑️",
            callback_data=task_callback.new(action="delete", task_id=task_id)
        )
    )
    return keyboard
