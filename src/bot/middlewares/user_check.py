from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from src.services.db.user_repository import (
    get_user_by_telegram_id,
)


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        """
        Middleware для проверки регистрации и принятия соглашения пользователем.
        """
        user_id = None

        if event.message:
            message = event.message
            user_id = message.from_user.id
            if message.text and message.text.startswith("/start"):
                return await handler(event, data)
        elif event.callback_query:
            callback_query = event.callback_query
            user_id = callback_query.from_user.id
            if callback_query.data == "accept_agreement":
                return await handler(event, data)
        else:
            return await handler(event, data)

        user = await get_user_by_telegram_id(user_id)
        if not user:
            if event.message:
                await message.reply(
                    "Пожалуйста, используйте команду /start для регистрации."
                )
            elif event.callback_query:
                await callback_query.message.reply(
                    "Пожалуйста, используйте команду /start для регистрации."
                )
                await callback_query.answer()
            return

        if not user.agreement_accepted:
            if event.message:
                await message.reply(
                    "Для работы с ботом вам нужно принять пользовательское соглашение. Используйте команду /start."
                )
            elif event.callback_query:
                await callback_query.message.reply(
                    "Для работы с ботом вам нужно принять пользовательское соглашение. Используйте команду /start."
                )
                await callback_query.answer()
            return

        return await handler(event, data)
