import aiosqlite
from aiogram import Bot, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Dispatcher

from keyboards import get_create_task_keyboard, get_numeric_task_navigation_keyboard

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATABASE_PATH = 'tasks.db'


class RequestStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_deadline = State()
    asking_for_description = State()
    processing_description = State()
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
async def send_welcome(message: Message, state: FSMContext):
    await message.answer(
        'создай заявку по инструкциям для любого дз, включая проекты и т.п. и желающий выполнит ее за плату',
        reply_markup=get_create_task_keyboard()
    )
    await state.set_state(RequestStates.waiting_for_subject)


@dp.message(RequestStates.waiting_for_subject)
async def ask_for_subject(message: Message, state: FSMContext):
    await message.answer('напиши название предмета')
    await state.set_state(RequestStates.waiting_for_deadline)


@dp.message(RequestStates.waiting_for_deadline)
async def ask_for_deadline(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('укажи дeдлайн, при необходимости вместе с временем')
    await state.set_state(RequestStates.asking_for_description)


@dp.message(RequestStates.asking_for_description)
async def ask_for_description(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await message.answer('отправь фото задания или его описание')
    await state.set_state(RequestStates.processing_description)


@dp.message(F.content_type.in_({ContentType.TEXT, ContentType.PHOTO}), RequestStates.processing_description)
async def process_task_description(message: Message, state: FSMContext):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        await state.update_data(description=file_id)
    elif message.content_type == 'text':
        await state.update_data(description=message.text)

    data = await state.get_data()

    form = (f"Предмет: {data['subject']}\n"
            f"Дедлайн: {data['deadline']}\n"
            f"Описание: {data['description']}")

    navigation = '1. Подтвердить.\n2. Заполнить заявку заново.\n3. Изменить предмет.\n4. Изменить дедлайн.\n5. Изменить описание.'

    await message.answer('вот так выглядит твоя заявка:')
    await message.answer(form)
    await message.answer(navigation, reply_markup=get_numeric_task_navigation_keyboard())
    await state.set_state(RequestStates.waiting_for_confirmation)


@dp.message(RequestStates.waiting_for_confirmation)
async def ask_for_confirmation(message: Message, state: FSMContext):
    if message.text == '1':
        data = await state.get_data()

        async with aiosqlite.connect(DATABASE_PATH) as db:
            await  db.execute('''
                INSERT INTO tasks (subject, deadline, description)
                VALUES (?, ?, ?)
            ''', (data['subject'], data['deadline'], data['description']))
            await db.commit()

        await message.answer(f'заявка создана успешно.\nв ближайшее время за твою работу возьмутся, жди оповещение')
        await state.clear()
    elif message.text == '2':
        await state.set_state(RequestStates.waiting_for_subject)
    elif message.text == '3':
        await state.set_state(RequestStates.waiting_for_subject)
    elif message.text == '4':
        await state.set_state(RequestStates.waiting_for_deadline)
    elif message.text == '5':
        await state.set_state(RequestStates.asking_for_description)


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
    dp.run_polling(bot)
