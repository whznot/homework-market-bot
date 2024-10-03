from aiogram import Bot, Router, types
from aiogram import Bot, Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import Message
from aiogram import Dispatcher
import asyncio

from config import TOKEN

bot = Bot(token=TOKEN)
router = Router()


class TaskCreation(StatesGroup):
    waiting_for_task_description = State()
    waiting_for_confirmation = State()


@router.message(F.text == "/start")
async def send_welcome(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='создать заявку')]
    ], resize_keyboard=True, one_time_keyboard=True)

    await message.anwer(
        'создай заявку по инструкциям для любого дз, включая проекты и т.п. и желающий выполнит ее за плату',
        reply_markup=markup)


@router.message(F.text == "создать заявку")
async def create_task(message: Message, state: FSMContext):
    await message.answer('напиши тему работы или название предмета')

    await message.answer(message, task_deadline)


async def task_deadline(message: Message, state: FSMContext):
    await message.answer('напиши дату для дэдлайна, при необходимости укажи время')

    bot.register_next_step_handler(message, task_description)


def task_description(message: Message, state: FSMContext):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, 'фото получено')
    elif message.content_type == 'text':
        description = message.text
        bot.send_message(message.chat.id, 'текст получен')
    else:
        bot.send_message(message.chat.id, 'отправь текст или фото')
        return

    bot.register_next_step_handler(message, task_confirmation)


def task_confirmation(message: Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(types.KeyboardButton('да, все верно'))
    markup.row(types.KeyboardButton('создать анкету заново'))

    bot.send_message(message.chat.id,
                     'вот так выглядит твое задание, все верно?',
                     reply_markup=markup)


if __name__ == '__main__':
    import asyncio
    asyncio.run(send_welcome())
