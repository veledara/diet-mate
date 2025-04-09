from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def cancel_keyboard():
    """
    Возвращает reply-клавиатуру для отмены действия.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
