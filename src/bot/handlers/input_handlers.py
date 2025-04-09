import logging
from pathlib import Path
import tempfile
import uuid
from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.filters.state import StateFilter
import base64

from src.services.logic.user_food_log_service import create_food_log_by_telegram_user_id
from src.services.logic.chat_gpt_service import (
    retrieve_nutrition_data,
    extract_nutrition_details,
    convert_speech_to_text,
)
from src.bot.keyboards.inline import save_food_button


logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text & ~F.text.startswith("/"), StateFilter(None))
async def handle_text(message: Message):
    """
    Хендлер для обычного текстового сообщения (если не начинается с /).
    """
    user_text = message.text.strip().lower()
    if user_text == "❌ отмена":
        await message.answer("Операция отменена.")
        return
    await _process_food_description(message, message.text.strip())


@router.message(F.voice, StateFilter(None))
async def handle_voice(message: Message):
    """
    Хендлер для голосового сообщения.
    """
    try:
        voice = message.voice
        file_id = voice.file_id
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / f"{file_id}.ogg"
            await message.bot.download(file_id, destination=file_path)
            transcription = await convert_speech_to_text(str(file_path))
    except Exception as e:
        logger.error(f"Ошибка загрузки аудио: {str(e)}")
        await message.answer("Ошибка обработки аудио")
        return

    if not transcription:
        await message.answer("Не удалось распознать речь")
        return

    await _process_food_description(message, transcription)


@router.message(F.photo, StateFilter(None))
async def handle_photo(message: Message):
    """
    Хендлер для получения фотографии. Скачивает фото, кодирует его в base64
    и передает в языковую модель.
    """
    try:
        photo: PhotoSize = message.photo[-1]
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / f"{photo.file_id}.jpg"
            await message.bot.download(photo.file_id, destination=file_path)
            with open(file_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")
        await _process_food_description(
            message, description="прикрепленная фотография", image_base64=image_base64
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке фотографии: {str(e)}")
        await message.answer(
            "Произошла ошибка при обработке фотографии. Попробуйте снова."
        )


async def _process_food_description(
    message: Message, description: str, image_base64: str | None = None
):
    """
    Общая функция обработки описания еды.
    """
    user_id = message.from_user.id
    emoji_message = None
    calculation_message = None

    try:
        emoji_message = await message.answer("⌛")
        calculation_message = await message.answer("Идет расчет...")

        response_text = await retrieve_nutrition_data(
            product_name=description, image_base64=image_base64
        )
        nutrition_info, error = await extract_nutrition_details(response_text)

        if error:
            await message.answer(error)
            return

        for msg in [emoji_message, calculation_message]:
            try:
                if msg:
                    await msg.delete()
            except Exception:
                pass

        entry_uuid = str(uuid.uuid4())
        sent_message = await message.answer(
            f"Еда: {nutrition_info['food']}\n"
            f"Калории: {nutrition_info['calories']} ккал\n"
            f"Белки: {nutrition_info['proteins']} г\n"
            f"Жиры: {nutrition_info['fats']} г\n"
            f"Углеводы: {nutrition_info['carbohydrates']} г\n"
            f"Клетчатка: {nutrition_info.get('fiber', '0')} г\n"
            f"AI Оценка: {nutrition_info['rating']}",
            reply_markup=save_food_button(entry_uuid=entry_uuid, action="add"),
        )

        await create_food_log_by_telegram_user_id(
            telegram_user_id=user_id,
            nutrition_info=nutrition_info,
            message_id=sent_message.message_id,
            entry_uuid=entry_uuid,
        )

    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        await message.answer("Произошла ошибка при расчете. Попробуйте еще раз.")
    finally:
        for msg in [calculation_message, emoji_message]:
            try:
                if msg:
                    await msg.delete()
            except Exception:
                pass
