<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import DATABASE_URL
from models import Base

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    try:
        async with engine.begin() as conn:
            print("Создание таблиц...")
            await conn.run_sync(Base.metadata.create_all)  # Удалите круглые скобки здесь
            print("Таблицы успешно созданы!")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
=======
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    import models
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
>>>>>>> 8a44031 (migrated to a new stable folder)
