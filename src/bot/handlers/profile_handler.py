import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from src.services.logic.nutrition_service import (
    create_or_update_profile_and_nutrition_by_telegram_id,
    get_user_profile_by_telegram_id,
    get_user_nutrition_by_telegram_id,
)
from src.services.logic.nutrition_calculation_service import calculate_nutrition
from src.bot.states.user_profile import UserProfileStates
from src.bot.keyboards.inline import (
    gender_keyboard,
    activity_level_keyboard,
    get_profile_edit_keyboard,
    goal_keyboard,
)
from src.bot.keyboards.reply import cancel_keyboard
from src.models.user_profile import Gender, ActivityLevel, Goal
from src.services.logic.user_weight_history_service import (
    create_weight_record_by_telegram_id,
)


logger = logging.getLogger(__name__)

router = Router()


async def apply_profile_update(user_id: int, user_profile, field_name: str, new_value):
    """
    Обновляет одно поле профиля, вовзвращает обновленный профиль и норму,
    """
    profile_data = {
        "gender": user_profile.gender,
        "height": user_profile.height,
        "weight": user_profile.weight,
        "target_weight": user_profile.target_weight,
        "age": user_profile.age,
        "activity_level": user_profile.activity_level,
        "goal": user_profile.goal,
    }
    profile_data[field_name] = new_value

    daily_calories, proteins, fats, carbs = calculate_nutrition(
        gender=profile_data["gender"],
        weight=profile_data["weight"],
        height=profile_data["height"],
        age=profile_data["age"],
        activity_level=profile_data["activity_level"],
        goal=profile_data["goal"],
    )
    nutrition_data = {
        "daily_calories": daily_calories,
        "proteins": proteins,
        "fats": fats,
        "carbohydrates": carbs,
    }

    await create_or_update_profile_and_nutrition_by_telegram_id(
        telegram_id=user_id,
        profile_data=profile_data,
        nutrition_data=nutrition_data,
    )

    updated_profile = await get_user_profile_by_telegram_id(user_id)
    updated_nutrition = await get_user_nutrition_by_telegram_id(user_id)
    return updated_profile, updated_nutrition


def format_profile_text(user_profile, user_nutrition) -> str:
    """
    Формирует красиво отформатированный текст профиля с эмодзи и разделителями.
    """
    return (
        "📋 <b>Ваш профиль</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Пол:</b> {user_profile.gender.display_name}\n"
        f"📏 <b>Рост:</b> {user_profile.height} см\n"
        f"⚖️ <b>Вес:</b> {user_profile.weight} кг\n"
        f"🎯 <b>Целевой вес:</b> {user_profile.target_weight} кг\n"
        f"🎂 <b>Возраст:</b> {user_profile.age} лет\n"
        f"🏃 <b>Активность:</b> {user_profile.activity_level.display_name}\n"
        f"✨ <b>Цель:</b> {user_profile.goal.display_name}\n\n"
        "🍽 <b>Суточная норма</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🔥 <b>Калории:</b> {user_nutrition.calories:.0f} ккал\n"
        f"🥩 <b>Белки:</b> {user_nutrition.proteins:.1f} г\n"
        f"🥑 <b>Жиры:</b> {user_nutrition.fats:.1f} г\n"
        f"🍞 <b>Углеводы:</b> {user_nutrition.carbohydrates:.1f} г\n\n"
        "Выберите параметр для изменения или нажмите <b>Закрыть</b>."
    )


@router.message(Command("profile"))
async def cmd_profile(message: types.Message, state: FSMContext):
    """
    Команда /profile, позволяет ввести свои характеристики и расчитать норму КБЖУ.
    """
    telegram_id = message.from_user.id
    user_profile = await get_user_profile_by_telegram_id(telegram_id)
    if not user_profile:
        await message.answer(
            "Отлично!\n"
            "Для расчета суточной нормы, вам необходимо ввести "
            "некоторые данные о себе.\n\n"
            "Вы можете отменить операцию в любой момент, нажав кнопку 'Отмена'.",
            reply_markup=cancel_keyboard(),
        )
        await message.answer(
            "Пожалуйста, укажите ваш пол:", reply_markup=gender_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_gender)
    else:
        user_nutrition = await get_user_nutrition_by_telegram_id(telegram_id)
        profile_text = format_profile_text(user_profile, user_nutrition)
        await message.answer(
            profile_text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )
        await state.clear()


@router.callback_query(F.data == "close_profile")
async def process_close_profile(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Закрывает текущее сообщение с редактированием профиля.
    """
    await state.clear()
    await callback_query.message.delete()
    await callback_query.message.answer(
        "Отлично, теперь вы можете продолжать вводить данные о еде."
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("edit_"))
async def process_edit_field(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопок "Изменить ...", переводит в нужный State.
    """
    field_to_edit = callback_query.data.split("_", 1)[1]
    await state.update_data(field_to_edit=field_to_edit)
    await callback_query.message.delete()
    if field_to_edit == "gender":
        await callback_query.message.answer(
            "Укажите ваш пол:", reply_markup=gender_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_gender)
    elif field_to_edit == "height":
        await callback_query.message.answer(
            "Введите новое значение роста (см):", reply_markup=cancel_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_height)
    elif field_to_edit == "weight":
        await callback_query.message.answer(
            "Введите новое значение веса (кг):", reply_markup=cancel_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_weight)
    elif field_to_edit == "target_weight":
        await callback_query.message.answer(
            "Введите новое значение целевого веса (кг):", reply_markup=cancel_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_target_weight)
    elif field_to_edit == "age":
        await callback_query.message.answer(
            "Введите ваш новый возраст (лет):", reply_markup=cancel_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_age)
    elif field_to_edit == "activity":
        await callback_query.message.answer(
            "Выберите ваш уровень активности:", reply_markup=activity_level_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_activity_level)
    elif field_to_edit == "goal":
        await callback_query.message.answer(
            "Выберите вашу цель:", reply_markup=goal_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_goal)
    else:
        await callback_query.message.answer("Неизвестный параметр для изменения.")
        await state.clear()

    await callback_query.answer()


@router.callback_query(
    F.data.startswith("gender_"), StateFilter(UserProfileStates.waiting_for_gender)
)
async def process_gender(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор пола.
    """
    gender_value = callback_query.data.split("_", 1)[1]
    try:
        gender = Gender(gender_value)
    except ValueError:
        await callback_query.message.answer("Неверный выбор. Попробуйте снова.")
        await callback_query.answer()
        return

    user_profile = await get_user_profile_by_telegram_id(callback_query.from_user.id)
    if not user_profile:
        await state.update_data(gender=gender)
        await callback_query.message.answer(
            "Введите ваш рост в сантиметрах:",
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(UserProfileStates.waiting_for_height)
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=callback_query.from_user.id,
            user_profile=user_profile,
            field_name="gender",
            new_value=gender,
        )
        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await callback_query.message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.message(StateFilter(UserProfileStates.waiting_for_gender))
async def process_gender_cancel(message: types.Message, state: FSMContext):
    """
    Обрабатывает отмену при ожидании пола.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return
    await message.answer(
        "Пожалуйста, выберите ваш пол:", reply_markup=gender_keyboard()
    )


@router.message(StateFilter(UserProfileStates.waiting_for_height))
async def process_height(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод роста.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return

    try:
        height = int(message.text)
        if not 50 <= height <= 300:
            raise ValueError
    except ValueError:
        await message.answer(
            "Введите корректное значение роста (см).", reply_markup=cancel_keyboard()
        )
        return

    user_profile = await get_user_profile_by_telegram_id(message.from_user.id)
    if not user_profile:
        await state.update_data(height=height)
        await message.answer("Введите ваш вес (кг):", reply_markup=cancel_keyboard())
        await state.set_state(UserProfileStates.waiting_for_weight)
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=message.from_user.id,
            user_profile=user_profile,
            field_name="height",
            new_value=height,
        )
        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )


@router.message(StateFilter(UserProfileStates.waiting_for_weight))
async def process_weight(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод веса.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return

    try:
        weight_str = message.text.replace(",", ".")
        weight = float(weight_str)

        if not 20.0 <= weight <= 500.0:
            raise ValueError
    except ValueError:
        await message.answer(
            "Введите корректное значение веса (кг).", reply_markup=cancel_keyboard()
        )
        return

    user_profile = await get_user_profile_by_telegram_id(message.from_user.id)
    if not user_profile:
        await state.update_data(weight=weight)
        await message.answer(
            "Введите ваш целевой вес (кг):", reply_markup=cancel_keyboard()
        )

        await create_weight_record_by_telegram_id(message.from_user.id, weight)

        await state.set_state(UserProfileStates.waiting_for_target_weight)
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=message.from_user.id,
            user_profile=user_profile,
            field_name="weight",
            new_value=weight,
        )

        await create_weight_record_by_telegram_id(message.from_user.id, weight)

        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )


@router.message(StateFilter(UserProfileStates.waiting_for_target_weight))
async def process_target_weight(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод целевого веса.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return

    try:
        target_weight_str = message.text.replace(",", ".")
        target_weight = float(target_weight_str)

        if not 20.0 <= target_weight <= 500.0:
            raise ValueError
    except ValueError:
        await message.answer(
            "Введите корректное значение целевого веса (кг).",
            reply_markup=cancel_keyboard(),
        )
        return

    user_profile = await get_user_profile_by_telegram_id(message.from_user.id)
    if not user_profile:
        await state.update_data(target_weight=target_weight)
        await message.answer(
            "Введите ваш возраст (лет):", reply_markup=cancel_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_age)
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=message.from_user.id,
            user_profile=user_profile,
            field_name="target_weight",
            new_value=target_weight,
        )
        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )


@router.message(StateFilter(UserProfileStates.waiting_for_age))
async def process_age(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод возраста.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return

    try:
        age = int(message.text)
        if not 5 <= age <= 120:
            raise ValueError
    except ValueError:
        await message.answer(
            "Введите корректное значение возраста (лет).",
            reply_markup=cancel_keyboard(),
        )
        return

    user_profile = await get_user_profile_by_telegram_id(message.from_user.id)
    if not user_profile:
        await state.update_data(age=age)
        await message.answer(
            "Выберите ваш уровень активности:", reply_markup=activity_level_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_activity_level)
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=message.from_user.id,
            user_profile=user_profile,
            field_name="age",
            new_value=age,
        )
        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )


@router.callback_query(
    F.data.startswith("activity_"),
    StateFilter(UserProfileStates.waiting_for_activity_level),
)
async def process_activity_level(
    callback_query: types.CallbackQuery, state: FSMContext
):
    """
    Обрабатывает выбор уровня активности.
    """
    activity_key = callback_query.data.split("_", 1)[1]
    try:
        activity_level = ActivityLevel(activity_key)
    except ValueError:
        await callback_query.message.answer("Неверный выбор активности.")
        await callback_query.answer()
        return

    user_profile = await get_user_profile_by_telegram_id(callback_query.from_user.id)
    if not user_profile:
        await state.update_data(activity_level=activity_level)
        await callback_query.message.answer(
            "Выберите вашу цель:", reply_markup=goal_keyboard()
        )
        await state.set_state(UserProfileStates.waiting_for_goal)
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=callback_query.from_user.id,
            user_profile=user_profile,
            field_name="activity_level",
            new_value=activity_level,
        )
        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await callback_query.message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.message(StateFilter(UserProfileStates.waiting_for_activity_level))
async def process_activity_level_cancel(message: types.Message, state: FSMContext):
    """
    Обрабатывает отмену при ожидании уровня активности.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return
    await message.answer(
        "Выберите уровень активности:", reply_markup=activity_level_keyboard()
    )


@router.callback_query(
    F.data.startswith("goal_"), StateFilter(UserProfileStates.waiting_for_goal)
)
async def process_goal(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор цели.
    """
    goal_key = callback_query.data.split("_", 1)[1]
    try:
        goal = Goal(goal_key)
    except ValueError:
        await callback_query.message.answer("Неверный выбор цели.")
        await callback_query.answer()
        return

    await state.update_data(goal=goal)
    user_data = await state.get_data()
    user_profile = await get_user_profile_by_telegram_id(callback_query.from_user.id)
    if not user_profile:
        daily_calories, proteins, fats, carbs = calculate_nutrition(
            gender=user_data["gender"],
            weight=user_data["weight"],
            height=user_data["height"],
            age=user_data["age"],
            activity_level=user_data["activity_level"],
            goal=user_data["goal"],
        )
        profile_data = {
            "gender": user_data["gender"],
            "height": user_data["height"],
            "weight": user_data["weight"],
            "target_weight": user_data["target_weight"],
            "age": user_data["age"],
            "activity_level": user_data["activity_level"],
            "goal": user_data["goal"],
        }
        nutrition_data = {
            "daily_calories": daily_calories,
            "proteins": proteins,
            "fats": fats,
            "carbohydrates": carbs,
        }

        try:
            await create_or_update_profile_and_nutrition_by_telegram_id(
                callback_query.from_user.id, profile_data, nutrition_data
            )
        except Exception as e:
            await callback_query.message.answer(
                str(e), reply_markup=types.ReplyKeyboardRemove()
            )
            await state.clear()
            await callback_query.answer()
            return

        await state.clear()
        new_profile = await get_user_profile_by_telegram_id(callback_query.from_user.id)
        new_nutrition = await get_user_nutrition_by_telegram_id(
            callback_query.from_user.id
        )
        text = format_profile_text(new_profile, new_nutrition)
        await callback_query.message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )
    else:
        updated_profile, updated_nutrition = await apply_profile_update(
            user_id=callback_query.from_user.id,
            user_profile=user_profile,
            field_name="goal",
            new_value=goal,
        )
        await state.clear()
        text = format_profile_text(updated_profile, updated_nutrition)
        await callback_query.message.answer(
            text,
            reply_markup=get_profile_edit_keyboard(),
            parse_mode="HTML",
        )

    await callback_query.answer()


@router.message(StateFilter(UserProfileStates.waiting_for_goal))
async def process_goal_cancel(message: types.Message, state: FSMContext):
    """
    Обрабатывает отмену при ожидании цели.
    """
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
        )
        return
    await message.answer("Выберите вашу цель:", reply_markup=goal_keyboard())
