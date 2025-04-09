from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.models.achievement import Achievement
from src.settings import settings
from src.models.base import Base
import logging


logger = logging.getLogger(__name__)

engine = create_async_engine(settings.db_url.get_secret_value(), echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

achievements_data = [
    {
        "code": "start",
        "name": "Главное - начать!",
        "description": "Ты расчитал КБЖУ в первый раз.",
        "icon_url": "/static/achievements/start.png",
    },
    {
        "code": "discipline",
        "name": "Дисциплина",
        "description": "Ты расчитывал КБЖУ 7 дней подряд!",
        "icon_url": "/static/achievements/discipline.png",
    },
    {
        "code": "halfway",
        "name": "Половина пути",
        "description": "Ты прошел 50% пути к целевому весу.",
        "icon_url": "/static/achievements/halfway.png",
    },
    {
        "code": "winner",
        "name": "Победитель",
        "description": "Ты достиг целевого веса!",
        "icon_url": "/static/achievements/winner.png",
    },
]


async def init_achievements():
    """
    Добавляет 4 достижения в таблицу achievements, если их там ещё нет.
    """
    async with async_session() as session:
        for ach in achievements_data:
            result = await session.execute(
                text("SELECT * FROM achievements WHERE code = :code"),
                {"code": ach["code"]},
            )
            if not result.scalar_one_or_none():
                new_ach = Achievement(
                    code=ach["code"],
                    name=ach["name"],
                    description=ach["description"],
                    icon_url=ach["icon_url"],
                )
                session.add(new_ach)
        await session.commit()


async def init_db(engine: AsyncEngine):
    """
    Инициализация базы данных: удаление всех таблиц и их повторное создание.
    """
    async with engine.begin() as conn:
        # Удаляем все существующие таблицы
        # logger.info("Удаляем все таблицы...")
        # await conn.run_sync(Base.metadata.drop_all)

        # Создаём таблицы заново
        logger.info("Создаём таблицы заново...")
        await conn.run_sync(Base.metadata.create_all)

        logger.info("Все таблицы созданы.")
