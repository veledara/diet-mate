import traceback
import re
from typing import List, Optional
import httpx

from src.settings import settings


async def call_gpt_api(
    url: str, headers: dict, data: dict, client: httpx.AsyncClient
) -> str:
    """
    Выполняет запрос к API OpenAI, возвращает ответ или сообщение об ошибке.
    """
    try:
        response = await client.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return f"Запрос не удался, статус: {response.status_code}: {response.text}"
        else:
            return "Возникли проблемы с языковой моделью."
    except Exception as e:
        traceback.print_exc()
        return "Возникли проблемы с языковой моделью."


async def call_whisper_api(
    url: str, headers: dict, data: dict, files: dict, client: httpx.AsyncClient
) -> str:
    """
    Делает запрос к модели OpenAI Whisper для распознавания текста из
    голосового сообщения,
    """
    try:
        response = await client.post(
            url, headers=headers, data=data, files=files, timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("text", "")
        else:
            print(
                f"Запрос не удался, статус: {response.status_code}: {response.text}"
            )
            return ""
    except Exception as e:
        traceback.print_exc()
        return ""


async def convert_speech_to_text(file_path: str) -> str:
    """
    Отправляет аудиофайл на распознавание в OpenAI Whisper.
    """
    api_key = settings.gpt_token.get_secret_value()
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    data = {"model": "whisper-1", "language": "ru"}

    try:
        with open(file_path, "rb") as f:
            files = {"file": ("audio.ogg", f, "audio/ogg")}

            if not settings.proxy_list:
                async with settings.create_async_client_with_proxy() as client:
                    transcript = await call_whisper_api(
                        url, headers, data, files, client
                    )
                return transcript

            for _ in range(len(settings.proxy_list)):
                async with settings.create_async_client_with_proxy() as client:
                    transcript = await call_whisper_api(
                        url, headers, data, files, client
                    )
                    if transcript:
                        return transcript

    except Exception as e:
        print(f"Error in convert_speech_to_text: {e}")
        traceback.print_exc()

    return ""


async def ai_report(
    user_profile,
    user_nutrition,
    food_logs: List,
    report_type: str,
) -> str:
    """
    Функция генерации AI-отчета по пользовательским данным.
    """
    if not food_logs:
        return "Нет данных для анализа."

    if report_type == "quality-report":
        prompt_header = """
            Ты должен сделать "Анализ качества питания", а именно:
            Проанализировать потребляемую мной еду, что стоит добавить в рацион, что убрать.
            Не анализируй КБЖУ, обращай внимание только на потребляемую мной еду.
        """
    elif report_type == "nutrition-report":
        prompt_header = """
            Ты должен сделать "Анализ КБЖУ", а именно:
            Проанализировать исключительно КБЖУ, не обращая внимания на саму еду.
            Опиши, каких макронутриентов слишком много или слишком мало, что добавить в рацион,
            чтобы значения были в норме.
            Не нужно считать суммарное КБЖУ всех моих приемов пищи, что я отправлю тебе далее.
            Это не имеет смысла, так как это последние n приемов пищи, а не то что я съел за сутки.
            Но ты можешь сделать вывод о том, каких макронутирентов я потребляю слишком много, а каких
            слишком мало.
        """
    else:
        prompt_header = "Сделай анализ моих приемов пищи."

    profile_str = (
        f"Рост: {user_profile.height}, "
        f"Вес: {user_profile.weight}, "
        f"Возраст: {user_profile.age}, "
        f"Цель: {user_profile.goal}"
    )

    nurtirtion_str = (
        f"Норма калорий: {user_nutrition.calories}, "
        f"Норма белков: {user_nutrition.proteins}, "
        f"Норма жиров: {user_nutrition.fats}, "
        f"Норма углеводов: {user_nutrition.carbohydrates}"
    )

    logs_description = []
    for idx, log in enumerate(food_logs, start=1):
        logs_description.append(
            f"{idx}) {log.food_name}, Калории: {log.calories}, "
            f"Белки: {log.proteins}, Жиры: {log.fats}, Углеводы: {log.carbohydrates}"
        )
    logs_str = "\n".join(logs_description)
    prompt = f"""
        {prompt_header}
        Тебе нужно сделать четко то, что я сказал в предыдуших предложениях.
        Вот мои данные:{profile_str}
        Вот моя суточная норма:{nurtirtion_str}
        Вот мои последние {len(food_logs)} приемов пищи:
        {logs_str}\n\n
        Тебе нужно дать емкий ответ, не слишком длинный, без привестствий.
        Представь что ты нутрициолог, и к тебе пришел клиент c этими данными.
        Не нужно дублировать информацию, которую я тебе отправил, просто сделай свою задачу.
    """
    print(prompt)

    api_key = settings.gpt_token.get_secret_value()
    url = "https://api.openai.com/v1/chat/completions"
    messages = [
        {"role": "system", "content": "Ты полезный помощник по питанию."},
        {"role": "user", "content": prompt.strip()},
    ]
    data = {
        "model": "chatgpt-4o-latest",
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.5,
        "n": 1,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with settings.create_async_client_with_proxy() as client:
        response_text = await call_gpt_api(url, headers, data, client)

    return response_text


async def retrieve_nutrition_data(
    product_name: str, image_base64: Optional[str] = None
) -> str:
    """
    Отправляет запрос на расчет калорий и макронутриентов приема пищи.
    """

    api_key = settings.gpt_token.get_secret_value()
    url = "https://api.openai.com/v1/chat/completions"

    if image_base64:
        product_name = "прикрепленная фотография"

    prompt = f"""
        Представь, что ты - профессиональный диетолог, и тебе нужно описать клиенту характеристики пищи.
        Свою еду он описывает так — {product_name}. Опиши точное количество калорий, белков, жиров, углеводов и клетчатки в данном продукте в строгом формате:
        - Еда: то, что описал пользователь, или, если описание не точное (например, нет граммовки, то дополненное, если это уместно)
        - Калории: <число> ккал
        - Белки: <число> г., Жиры: <число> г., Углеводы: <число> г.
        - Клетчатка: <число> г.
        Не пиши диапазоны в калориях, белках, жирах, углеводах и клетчатке, если сомневаешься — пиши среднее значение.
        В конце добавь строго одну из таких строк: "Рейтинг: 🔴" или "Рейтинг: 🟡" или "Рейтинг: 🟢", если считаешь еду вредной, обычной или полезной соответственно.
        Если сообщение не представляется возможным распознать как еду, то напиши строго:
        "Не удалось посчитать калории, исходя из сообщения. Попробуйте написать точнее."
    """

    if image_base64:
        messages = [
            {"role": "system", "content": "Ты полезный помощник по питанию."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Определи, что за еда на фото и посчитай КБЖУ.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
            {"role": "user", "content": prompt.strip()},
        ]
    else:
        messages = [
            {"role": "system", "content": "Ты полезный помощник по питанию."},
            {"role": "user", "content": prompt.strip()},
        ]
    data = {
        "model": "chatgpt-4o-latest",
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.5,
        "n": 1,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if not settings.proxy_list:
        async with settings.create_async_client_with_proxy() as client:
            return await call_gpt_api(url, headers, data, client)
    else:
        for _ in range(len(settings.proxy_list)):
            async with settings.create_async_client_with_proxy() as client:
                answer = await call_gpt_api(url, headers, data, client)
                if not answer.startswith("Не удалось"):
                    return answer
        return "Не удалось посчитать калории, исходя из сообщения."


async def extract_nutrition_details(response_text: str):
    """
    Парсит текст ответа от GPT, извлекает данные о еде и ее макронутриентах.
    """
    try:
        food_match = re.search(r"Еда:\s*(.*)", response_text)
        value_pattern = r"(\d+[.,]?\d*)"

        calories_match = re.search(
            rf"Калории:\s*{value_pattern}(?:\s*[-–—]\s*\d+[.,]?\d*)?\s*ккал",
            response_text,
        )
        proteins_match = re.search(
            rf"Белки:\s*{value_pattern}(?:\s*[-–—]\s*\d+[.,]?\d*)?\s*г",
            response_text,
        )
        fats_match = re.search(
            rf"Жиры:\s*{value_pattern}(?:\s*[-–—]\s*\d+[.,]?\d*)?\s*г",
            response_text,
        )
        carbohydrates_match = re.search(
            rf"Углеводы:\s*{value_pattern}(?:\s*[-–—]\s*\d+[.,]?\d*)?\s*г",
            response_text,
        )
        fiber_match = re.search(
            rf"Клетчатка:\s*{value_pattern}(?:\s*[-–—]\s*\d+[.,]?\d*)?\s*г",
            response_text,
        )
        rating_match = re.search(r"Рейтинг:\s*([🔴🟡🟢])", response_text)

        if not all(
            [
                food_match,
                calories_match,
                proteins_match,
                fats_match,
                carbohydrates_match,
                fiber_match,
                rating_match,
            ]
        ):
            return (
                None,
                f"{response_text}",
            )

        def parse_value(value_str: str) -> float:
            return float(value_str.replace(",", "."))

        nutrition_info = {
            "food": food_match.group(1).strip(),
            "calories": parse_value(calories_match.group(1)),
            "proteins": parse_value(proteins_match.group(1)),
            "fats": parse_value(fats_match.group(1)),
            "carbohydrates": parse_value(carbohydrates_match.group(1)),
            "fiber": parse_value(fiber_match.group(1)),
            "rating": rating_match.group(1).strip(),
        }

        if nutrition_info["rating"] not in ["🔴", "🟡", "🟢"]:
            return (
                None,
                f"Некорректное значение рейтинга: {nutrition_info['rating']}",
            )

        return nutrition_info, None

    except Exception as e:
        return None, f"Ошибка при разборе данных: {str(e)}"
