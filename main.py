import aiosqlite
from aiogram import Bot, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder
from aiogram.types import Message
from aiogram import Dispatcher

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATABASE_PATH = 'tasks.db'


class RequestStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_deadline = State()
    waiting_for_description = State()
    waiting_for_confirmation = State()


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                deadline TEXT NOT NULL,
                description TEXT
            )
        ''')
        await db.commit()


@dp.message(CommandStart())
async def send_welcome(message: Message):
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text='создать заявку'))

    keyboard = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        'создай заявку по инструкциям для любого дз, включая проекты и т.п. и желающий выполнит ее за плату',
        reply_markup=keyboard
    )


@dp.message(F.text == 'создать заявку')
async def create_task(message: Message, state: FSMContext):
    await message.answer('напиши тему работы или название предмета')
    await state.set_state(RequestStates.waiting_for_subject)


@dp.message(RequestStates.waiting_for_subject)
async def task_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('напиши дату для дeдлайна, при необходимости укажи время')
    await state.set_state(RequestStates.waiting_for_deadline)


@dp.message(RequestStates.waiting_for_deadline)
async def task_deadline(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await message.answer('отправь фото задания или его описание')
    await state.set_state(RequestStates.waiting_for_description)


@dp.message(F.content_type.in_({ContentType.TEXT, ContentType.PHOTO}), RequestStates.waiting_for_description)
async def task_description(message: Message, state: FSMContext):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        await state.update_data(description=file_id)
    elif message.content_type == 'text':
        description = message.text
        await state.update_data(description=description)

    data = await state.get_data()

    confirmation_text = (f"Предмет: {data['subject']}\n"
                         f"Дедлайн: {data['deadline']}\n"
                         f"Описание: {data['description']}")

    await message.answer(f'Вот так выглядит твоё задание:\n\n{confirmation_text}\n\nВсё верно?')

    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='да, все верно'),
        KeyboardButton(text='заполнить заново')
    )

    keyboard = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    await message.answer('вот так выглядит твоя заявка, все верно?', reply_markup=keyboard)
    await state.set_state(RequestStates.waiting_for_confirmation)


@dp.message(RequestStates.waiting_for_confirmation)
async def task_confirmation(message: Message, state: FSMContext):
    if message.text == 'да, все верно':
        data = await state.get_data()

        async with aiosqlite.connect(DATABASE_PATH) as db:
            await  db.execute('''
                INSERT INTO tasks (subject, deadline, description)
                VALUES (?, ?, ?)
            ''', (data['subject'], data['deadline'], data['description']))
            await db.commit()

        await message.answer(f'заявка создана успешно.\nв ближайшее время за твою работу возьмутся, жди оповещение')
        await state.clear()
    elif message.text == 'заполнить заново':
        await state.set_state(RequestStates.waiting_for_subject)


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
    dp.run_polling(bot)
