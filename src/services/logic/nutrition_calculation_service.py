from src.models.user_profile import Gender, ActivityLevel, Goal


def calculate_bmr(gender, weight, height, age):
    """
    Рассчитывает базовый обмен веществ (BMR) по формуле Миффлина-Сан Жеора.
    """
    if gender == Gender.MALE:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr


def calculate_tdee(bmr, activity_level):
    """
    Рассчитывает TDEE (суточную потребность в калориях) с учётом уровня активности.
    """
    activity_multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,
        ActivityLevel.MODERATELY_ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTRA_ACTIVE: 1.9,
    }
    return bmr * activity_multipliers[activity_level]


def adjust_tdee_for_goal(tdee, goal):
    """
    Корректирует TDEE в зависимости от цели пользователя.
    """
    if goal == Goal.LOSE_WEIGHT:
        return tdee * 0.85
    elif goal == Goal.GAIN_WEIGHT:
        return tdee * 1.15
    else:
        return tdee


def calculate_macros(calories, weight, goal):
    """
    Рассчитывает количество белков, жиров и углеводов на основе калорий, веса и цели.
    """
    if goal == Goal.LOSE_WEIGHT:
        # Для сохранения мышц при похудении нужно чуть больше белков, жиров минимум
        protein_per_kg = 1.4
        fat_per_kg = 0.8
    elif goal == Goal.GAIN_WEIGHT:
        # Для набора веса можем поднять жиры
        protein_per_kg = 1.6
        fat_per_kg = 1.2
    else:
        # Используем средние значения при поддержании веса
        protein_per_kg = 1.2
        fat_per_kg = 1.0

    proteins = protein_per_kg * weight
    fats = fat_per_kg * weight

    carbs = (calories - (proteins * 4 + fats * 9)) / 4  # Остаток - углеводы
    return proteins, fats, carbs


def calculate_nutrition(gender, weight, height, age, activity_level, goal):
    """
    Общая функция для расчёта всех показателей.
    """
    bmr = calculate_bmr(gender, weight, height, age)
    tdee = calculate_tdee(bmr, activity_level)
    daily_calories = adjust_tdee_for_goal(tdee, goal)
    proteins, fats, carbs = calculate_macros(daily_calories, weight, goal)
    return round(daily_calories, 2), round(proteins, 2), round(fats, 2), round(carbs, 2)
