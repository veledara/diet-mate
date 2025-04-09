from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.settings import settings
from src.models.user_profile import ActivityLevel, Goal, Gender


def get_profile_edit_keyboard():
    """
    Возвращает инлайн-клавиатуру для редактирования существующего профиля.
    """
    builder = InlineKeyboardBuilder()

    builder.button(text="Изменить пол", callback_data="edit_gender")
    builder.button(text="Изменить рост", callback_data="edit_height")
    builder.button(text="Изменить вес", callback_data="edit_weight")
    builder.button(text="Изменить целевой вес", callback_data="edit_target_weight")
    builder.button(text="Изменить возраст", callback_data="edit_age")
    builder.button(text="Изменить активность", callback_data="edit_activity")
    builder.button(text="Изменить цель", callback_data="edit_goal")

    builder.button(text="❌ Закрыть", callback_data="close_profile")

    builder.adjust(1)
    return builder.as_markup()


def get_user_agreement_keyboard():
    """
    Возвращает инлайн-клавиатуру для принятия пользовательского соглашения.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Пользовательское соглашение",
        url=settings.user_agreement_url.get_secret_value(),
    )
    builder.button(text="Я принимаю", callback_data="accept_agreement")
    return builder.as_markup()


def gender_keyboard():
    """
    Возвращает инлайн-клавиатуру для ввода пола.
    """
    builder = InlineKeyboardBuilder()
    for gender in Gender:
        builder.button(text=gender.display_name, callback_data=f"gender_{gender.value}")
    return builder.as_markup()


def activity_level_keyboard():
    """
    Возвращает инлайн-клавиатуру для ввода активности.
    """
    builder = InlineKeyboardBuilder()
    for level in ActivityLevel:
        builder.button(text=level.display_name, callback_data=f"activity_{level.value}")
    builder.adjust(1)
    return builder.as_markup()


def goal_keyboard():
    """
    Возвращает инлайн-клавиатуру для ввода цели.
    """
    builder = InlineKeyboardBuilder()
    for goal in Goal:
        builder.button(text=goal.display_name, callback_data=f"goal_{goal.value}")
    return builder.as_markup()


def save_food_button(entry_uuid, action="add"):
    """
    Возвращает инлайн-клавиатуру для сохранения или удаления еды из дневника.
    """
    builder = InlineKeyboardBuilder()
    if action == "add":
        button_text = "✅ Добавить в дневник"
        callback_action = "save_food"
    elif action == "remove":
        button_text = "⛔ Убрать из дневника"
        callback_action = "remove_food"
    else:
        raise ValueError("Invalid action for save_food_button")

    builder.button(
        text=button_text,
        callback_data=f"{callback_action}|{entry_uuid}",
    )
    return builder.as_markup()
