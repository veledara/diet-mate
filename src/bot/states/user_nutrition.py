from aiogram.fsm.state import StatesGroup, State


class UserNutritionStates(StatesGroup):
    awaiting_food_save = State()
