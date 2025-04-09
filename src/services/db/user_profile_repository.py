from typing import Optional
from sqlalchemy import select

from src.services.db.database import async_session
from src.models.user_profile import UserProfile


async def get_user_profile_by_user_id(user_id: int) -> Optional[UserProfile]:
    """
    Возвращает профиль пользователя по user_id.
    Если профиль не найден, возвращает None.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def create_or_update_profile_by_user_id(
    user_id: int,
    profile_data: dict,
) -> UserProfile:
    """
    Создаёт или обновляет профиль пользователя по user_id.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        existing_profile = result.scalar_one_or_none()

        if existing_profile:
            existing_profile.gender = profile_data["gender"]
            existing_profile.height = profile_data["height"]
            existing_profile.weight = profile_data["weight"]
            existing_profile.target_weight = profile_data["target_weight"]
            existing_profile.age = profile_data["age"]
            existing_profile.activity_level = profile_data["activity_level"]
            existing_profile.goal = profile_data["goal"]

            await session.commit()
            await session.refresh(existing_profile)
            return existing_profile
        else:
            new_profile = UserProfile(
                user_id=user_id,
                gender=profile_data["gender"],
                height=profile_data["height"],
                weight=profile_data["weight"],
                target_weight=profile_data["target_weight"],
                age=profile_data["age"],
                activity_level=profile_data["activity_level"],
                goal=profile_data["goal"],
            )
            session.add(new_profile)
            await session.commit()
            await session.refresh(new_profile)
            return new_profile
