from aiogram import Bot, F
from aiogram import Dispatcher
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from queries import convert_to_utc, format_datetime_to_str
from config import TOKEN
from db import async_session
from keyboards import get_create_task_keyboard, get_numeric_task_navigation_keyboard, get_task_action_keyboard, \
    TaskCallbackFactory
from queries import add_task, get_user_tasks, delete_task, get_task_by_id

bot = Bot(token=TOKEN)
dp = Dispatcher()


class RequestStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_deadline = State()
    waiting_for_description = State()
    waiting_for_deadline_input = State()
    processing_description = State()
    waiting_for_confirmation = State()
    waiting_for_subject_update = State()
    waiting_for_deadline_update = State()
    waiting_for_description_update = State()


@dp.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    await message.answer(
        "Создай заявку по инструкциям для любого дз, включая проекты и т.п. и желающий выполнит ее за плату",
        reply_markup=get_create_task_keyboard()
    )
    await state.set_state(RequestStates.waiting_for_subject)


@dp.message(RequestStates.waiting_for_subject)
async def ask_for_subject(message: Message, state: FSMContext):
    await message.answer("Напиши название предмета")
    await state.set_state(RequestStates.waiting_for_deadline)


@dp.message(RequestStates.waiting_for_deadline)
async def ask_for_deadline(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("Укажи дeдлайн, при необходимости вместе с временем")

    await state.set_state(RequestStates.waiting_for_deadline_input)


@dp.message(RequestStates.waiting_for_deadline_input)
async def process_deadline(message: Message, state: FSMContext):
    date_input = message.text

    try:
        formatted_date = format_datetime_to_str(convert_to_utc(date_input))
    except ValueError:
        await message.answer("Дата не распознана, укажи дедлайн корректно.")
        return

    await state.update_data(deadline=formatted_date)
    await message.answer("Отправь фото задания или его описание")
    await state.set_state(RequestStates.waiting_for_description)


@dp.message(F.content_type.in_({ContentType.TEXT, ContentType.PHOTO}), RequestStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.content_type == ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        data["photo_id"] = file_id
        await state.update_data(photo_id=file_id)
    else:
        description = message.text
        data["description"] = description
        await state.update_data(description=description)

    await show_task_summary(message, state)


@dp.message(RequestStates.waiting_for_confirmation)
async def ask_for_confirmation(message: Message, state: FSMContext):
    if message.text == "1":
        data = await state.get_data()
        async with async_session() as session:
            await add_task(session, user_id=message.from_user.id, subject=data["subject"], deadline=data["deadline"],
                           description=data.get("description"), photo_id=data.get("photo_id"))

        await message.answer(
            f"Заявка создана успешно.\nВ ближайшее время за твою работу возьмутся, жди оповещение.\nСоздать еще одну?")
        await state.clear()

    elif message.text == "2":
        await ask_for_subject(message, state)
    elif message.text == "3":
        await message.answer("Отправь название предмета")
        await state.set_state(RequestStates.waiting_for_subject_update)
    elif message.text == "4":
        await message.answer("Отправь дедлайн")
        await state.set_state(RequestStates.waiting_for_deadline_update)
    elif message.text == "5":
        await message.answer("Отправь фото задания или его описание")
        await state.set_state(RequestStates.waiting_for_description_update)
    else:
        await message.answer("Выбери опцию от 1 до 5")


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

    form = (
        f"<b>Предмет:</b> {data['subject']}\n\n"
        f"<b>Дедлайн:</b> {data['deadline']}\n\n"
    )

    if "description" in data and data["description"]:
        form += f"<b>Описание:</b> {data['description']}"

    await message.answer("Вот так выглядит твоя заявка:", parse_mode="HTML")

    if "photo_id" in data and data["photo_id"]:
        await message.answer_photo(data["photo_id"], caption=form, parse_mode="HTML")
    else:
        await message.answer(form, parse_mode="HTML")

    navigation = (
        "1. Подтвердить.\n"
        "2. Заполнить заявку заново.\n"
        "3. Изменить предмет.\n"
        "4. Изменить дедлайн.\n"
        "5. Изменить описание."
    )

    await message.answer(navigation, reply_markup=get_numeric_task_navigation_keyboard(), parse_mode="HTML")
    await state.set_state(RequestStates.waiting_for_confirmation)


@dp.message(Command("mytasks"))
async def my_tasks(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with async_session() as session:
        tasks = await get_user_tasks(session, user_id)

        if not tasks:
            await message.answer("Текущие заявки отсутствуют, создать новую?", reply_markup=get_create_task_keyboard())
            await state.set_state(RequestStates.waiting_for_subject)
        else:
            for task in tasks:
                task_summary = (
                    f"<b>Предмет:</b> {task.subject}\n\n"
                    f"<b>Дедлайн:</b> {task.deadline}\n\n"
                )

                if task.description:
                    task_summary += f"<b>Описание:</b> {task.description}\n\n"

                if task.photo_id:
                    await message.answer_photo(task.photo_id, caption=task_summary, parse_mode="HTML",
                                               reply_markup=get_task_action_keyboard(task.id))
                else:
                    await message.answer(task_summary, parse_mode="HTML",
                                         reply_markup=get_task_action_keyboard(task.id))


@dp.callback_query(TaskCallbackFactory.filter())
async def task_callback_handler(callback_query: CallbackQuery, callback_data: TaskCallbackFactory, state: FSMContext):
    async with async_session() as session:
        if callback_data.action == "edit":
            task = await get_task_by_id(session, callback_data.task_id)
            if task:
                await state.update_data(current_task_id=task.id, subject=task.subject, deadline=task.deadline,
                                        description=task.description, photo_id=task.photo_id)
                await show_task_summary(callback_query.message, state)
        elif callback_data.action == "delete":
            await delete_task(session, callback_data.task_id)
            await callback_query.answer("Задание удалено")


if __name__ == "__main__":
    import asyncio
    from db import init_db

    async def main():
        await init_db()
        await dp.start_polling(bot)

    asyncio.run(main())
