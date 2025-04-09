import asyncio
import uvicorn
from src.api.app import create_app
from src.bot.bot import start_bot
from src.services.db.database import init_achievements, init_db, engine


async def start_api(app):
    """
    Запускаем Uvicorn сервер в рамках asyncio.
    """
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    # Инициализация FastAPI приложения
    await init_db(engine)

    # Инициализация достижений
    await init_achievements()

    app = create_app()

    # Запускаем одновременно бота и API
    await asyncio.gather(
        start_bot(),  # Запуск бота
        start_api(app),  # Запуск API через Uvicorn
    )


if __name__ == "__main__":
    asyncio.run(main())
