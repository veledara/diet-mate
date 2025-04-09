from aiogram.fsm.state import StatesGroup, State


class UserProfileStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_target_weight = State()
    waiting_for_age = State()
    waiting_for_activity_level = State()
    waiting_for_goal = State()
