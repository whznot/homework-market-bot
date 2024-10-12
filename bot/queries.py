from sqlalchemy.future import select
from models import Task


async def add_task(session, user_id: int, subject: str, deadline: str, description: str = None, photo_id: str = None):
    new_task = Task(user_id=user_id, subject=subject, deadline=deadline, description=description, photo_id=photo_id)
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
