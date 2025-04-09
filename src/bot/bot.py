import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.settings import settings
from src.bot.handlers import (
    diary_handler,
    input_handlers,
    profile_handler,
    start_handler,
)
from src.bot.middlewares.user_check import UserCheckMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_bot():
    try:
        # Инициализация бота
        bot = Bot(token=settings.bot_token.get_secret_value())
        bot_info = await bot.get_me()
        logger.info(f"Bot info: {bot_info}")

        # Создаём диспетчер и регистрируем миддлвари и хендлеры
        dp = Dispatcher()

        dp.update.middleware(UserCheckMiddleware())

        dp.include_router(start_handler.router)
        dp.include_router(input_handlers.router)
        dp.include_router(profile_handler.router)
        dp.include_router(diary_handler.router)

        # Пропускаем все входящие
        await bot.delete_webhook(drop_pending_updates=True)

        # Запускаем polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    asyncio.run(start_bot())
