from sqlalchemy.future import select
from models import Task
<<<<<<< HEAD


async def add_task(session, user_id: int, subject: str, deadline: str, description: str = None, photo_id: str = None):
    new_task = Task(user_id=user_id, subject=subject, deadline=deadline, description=description, photo_id=photo_id)
=======
import datetime
import pytz
import dateparser


def convert_to_utc(datetime_str: str) -> datetime.datetime:
    parsed_datetime = dateparser.parse(datetime_str)

    if not parsed_datetime:
        raise ValueError(f"Не удалось распознать дату из строки: {datetime_str}")

    return pytz.utc.localize(parsed_datetime)


def format_datetime_to_str(dt: datetime.datetime) -> str:
    return dt.strftime("%A, %d-%m, %H:%M")


async def add_task(session, user_id: int, subject: str, deadline: str, description: str = None, photo_id: str = None):
    deadline_utc = convert_to_utc(deadline)
    deadline_str = format_datetime_to_str(deadline_utc)
    new_task = Task(user_id=user_id, subject=subject, deadline=deadline_str, description=description, photo_id=photo_id)
>>>>>>> 8a44031 (migrated to a new stable folder)
    session.add(new_task)
    await session.commit()
    return new_task


async def get_user_tasks(session, user_id: int):
    stmt = select(Task).where(Task.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_task_by_id(session, task_id: int):
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_task(session, task_id: int):
    task = await session.get(Task, task_id)
    if task:
        await session.delete(task)
        await session.commit()
