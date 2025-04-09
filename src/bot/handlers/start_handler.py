import logging
from aiogram import Router, types
from aiogram.filters import CommandStart

from src.services.logic.user_service import (
    get_user_by_telegram_id,
    register_new_user,
    accept_user_agreement,
)
from src.bot.keyboards.inline import get_user_agreement_keyboard


logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        user = await register_new_user(telegram_id, username)

    if not user.agreement_accepted:
        await message.answer(
            "Привет! Для использования бота вам необходимо принять пользовательское соглашение.",
            reply_markup=get_user_agreement_keyboard(),
        )
    else:
        await message.answer("Привет! Добро пожаловать обратно!")


@router.callback_query(lambda call: call.data == "accept_agreement")
async def accept_agreement(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id

    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await callback_query.message.answer(
            "Пользователь не найден. Пожалуйста, используйте команду /start."
        )
        await callback_query.answer()
        return

    if not user.agreement_accepted:
        result = await accept_user_agreement(telegram_id)
        if result:
            await callback_query.message.answer(
                "🎉 <b>Спасибо за принятие соглашения!</b>\n\n"
                "Теперь, просто напишите, что вы съели, а я расчитаю КБЖУ!\n"
                "Пример:\n"
                "<blockquote>Овсяная каша с бананом и кофе</blockquote>\n"
                "Если вам неудобно текстом, можете отправить голосовое сообщение, "
                "или прислать фотографию своей еды.\n\n"
                "Для того, чтобы воспользоваться полным функционалом бота, воспользуйтесь командой /profile\n"
                "С помощью нее вы можете расчитать свою норму калорий!\n\n"
                "<b>Приятного пользования!</b>",
                parse_mode="HTML",
            )
        else:
            await callback_query.message.answer(
                "Не удалось принять соглашение. Попробуйте снова или /start."
            )
    else:
        await callback_query.message.answer("Вы уже приняли соглашение!")

    await callback_query.answer()
