from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


class TaskCallbackFactory(CallbackData, prefix="task"):
    action: str
    task_id: int


def get_create_task_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='Создать заявку'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_numeric_task_navigation_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3'), KeyboardButton(text='4'),
                KeyboardButton(text='5'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_task_action_keyboard(task_id: int) -> InlineKeyboardMarkup:
    task_callback_edit = TaskCallbackFactory(action="edit", task_id=task_id)
    task_callback_delete = TaskCallbackFactory(action="delete", task_id=task_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✏️",
                callback_data=task_callback_edit.pack()
            ),
            InlineKeyboardButton(
                text="🗑️",
                callback_data=task_callback_delete.pack()
            )
        ]
    ])
    return keyboard
