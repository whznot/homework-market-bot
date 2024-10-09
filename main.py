import aiosqlite
from aiogram import Bot, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Dispatcher

from keyboards import get_create_task_keyboard, get_numeric_task_navigation_keyboard

from config import TOKEN

DATABASE_PATH = 'tasks.db'

bot = Bot(token=TOKEN)
dp = Dispatcher()


class RequestStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_deadline = State()
    waiting_for_description = State()
    processing_description = State()
    waiting_for_confirmation = State()
    waiting_for_subject_update = State()
    waiting_for_deadline_update = State()
    waiting_for_description_update = State()


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                deadline TEXT NOT NULL,
                description TEXT,
                photo_id TEXT
            )
        ''')
        await db.commit()


@dp.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    await message.answer(
        'Создай заявку по инструкциям для любого дз, включая проекты и т.п. и желающий выполнит ее за плату',
        reply_markup=get_create_task_keyboard()
    )
    await state.set_state(RequestStates.waiting_for_subject)


@dp.message(RequestStates.waiting_for_subject)
async def ask_for_subject(message: Message, state: FSMContext):
    await message.answer('Напиши название предмета')
    await state.set_state(RequestStates.waiting_for_deadline)


@dp.message(RequestStates.waiting_for_deadline)
async def ask_for_deadline(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer('Укажи дeдлайн, при необходимости вместе с временем')
    await state.set_state(RequestStates.waiting_for_description)


@dp.message(RequestStates.waiting_for_description)
async def ask_for_description(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await message.answer('Отправь фото задания или его описание')
    await state.set_state(RequestStates.processing_description)


@dp.message(F.content_type.in_({ContentType.TEXT, ContentType.PHOTO}), RequestStates.processing_description)
async def process_task_description(message: Message, state: FSMContext):
    if message.content_type == ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        await state.update_data(description=file_id)
    else:
        await state.update_data(description=message.text)

    await show_task_summary(message, state)


@dp.message(RequestStates.waiting_for_confirmation)
async def ask_for_confirmation(message: Message, state: FSMContext):
    if message.text == '1':
        data = await state.get_data()

        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute('''
                INSERT INTO tasks (user_id, subject, deadline, description)
                VALUES (?, ?, ?, ?)
            ''', (message.from_user.id, data['subject'], data['deadline'], data['description']))
            await db.commit()

        await message.answer(f'Заявка создана успешно.\nВ ближайшее время за твою работу возьмутся, жди оповещение')
        await state.clear()

    elif message.text == '2':
        await ask_for_subject(message, state)
    elif message.text == '3':
        await message.answer('Отправь название предмета')
        await state.set_state(RequestStates.waiting_for_subject_update)
    elif message.text == '4':
        await message.answer('Отправь дедлайн')
        await state.set_state(RequestStates.waiting_for_deadline_update)
    elif message.text == '5':
        await message.answer('Отправь фото задания или его описание')
        await state.set_state(RequestStates.waiting_for_description_update)
    else:
        await message.answer('Выбери опцию от 1 до 5')


@dp.message(RequestStates.waiting_for_subject_update)
async def update_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await show_task_summary(message, state)


@dp.message(RequestStates.waiting_for_deadline_update)
async def update_deadline(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await show_task_summary(message, state)


@dp.message(RequestStates.waiting_for_description_update)
async def update_description(message: Message, state: FSMContext):
    if message.content_type == ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        await state.update_data(description=file_id)
    else:
        await state.update_data(description=message.text)
    await show_task_summary(message, state)


async def show_task_summary(message: Message, state: FSMContext):
    data = await state.get_data()

    form = (f"Предмет: {data['subject']}\n"
            f"Дедлайн: {data['deadline']}\n")

    await message.answer('Вот так выглядит твоя заявка:')

    if message.content_type == ContentType.PHOTO:
        await message.answer_photo(data['description'], form)
    else:
        form += f"Описание: {data['description']}"
        await message.answer(form)

    navigation = (
        '1. Подтвердить.\n'
        '2. Заполнить заявку заново.\n'
        '3. Изменить предмет.\n'
        '4. Изменить дедлайн.\n'
        '5. Изменить описание.'
    )

    await message.answer(navigation, reply_markup=get_numeric_task_navigation_keyboard())
    await state.set_state(RequestStates.waiting_for_confirmation)


@dp.message(Command('mytasks'))
async def my_tasks(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('SELECT subject, deadline, description FROM tasks WHERE user_id = ?', (user_id,))
        tasks = await cursor.fetchall()

        if not tasks:
            await message.answer('Текущие заявки отсутствуют, создать новую?', reply_markup=get_create_task_keyboard())
        else:
            for task in tasks:
                subject = task[0]
                deadline = task[1]
                description = task[2]

            task_summary = f'Предмет: {subject}\nДедлайн: {deadline}'




            task_list = '\n\n'.join([f'Предмет: {task[0]}\nДедлайн: {task[1]}\nОписание: {task[2]}' for task in tasks])
            await message.answer(task_list)


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
    dp.run_polling(bot)
