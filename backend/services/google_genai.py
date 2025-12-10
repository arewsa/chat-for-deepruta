import os
import json
from typing import List
from google import genai
from google.genai.types import GenerateContentConfig, Tool, Schema
from schemas.gemini_functions import get_geocoding_functions
from services.gemini_mcp_bridge import GeminiMCPBridge
import asyncio
from dotenv import load_dotenv
from models.job import Job

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

client = genai.Client(api_key=GOOGLE_API_KEY)
class GoogleGenAI:
    def __init__(self):
        self.client = client
        self.bridge = GeminiMCPBridge()

    async def generate_with_tools(self, prompt: str, model: str = "gemini-2.5-flash") -> List[Job]:
        config = GenerateContentConfig(
            tools=[Tool(function_declarations=get_geocoding_functions())]
        )
        
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )

        if not (response.candidates and 
                response.candidates[0].content and 
                response.candidates[0].content.parts and
                len(response.candidates[0].content.parts) > 0):
            return []
        
        first_part = response.candidates[0].content.parts[0]
        
        if not (hasattr(first_part, 'function_call') and first_part.function_call):
            return []
        
        function_call = first_part.function_call
        
        function_result = await self.bridge.handle_function_call(
            function_call.name or "",
            function_call.args or {}
        )
        
        all_results = [function_result]
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            geocode_prompt = f"""Результаты выполнения функций геокодирования:

{json.dumps(all_results, ensure_ascii=False, indent=2)}

Исходный запрос пользователя: {prompt}

Проанализируй результаты. Если в исходном запросе есть еще адреса, для которых не получены координаты, вызови функцию forward_geocode для каждого недостающего адреса.
Если все адреса из запроса уже обработаны и координаты получены, НЕ вызывай больше функций. Просто ответь текстом "Все координаты собраны"."""
            
            geocode_response = await self.client.aio.models.generate_content(
                model=model,
                contents=geocode_prompt,
                config=config
            )
            
            if not (geocode_response.candidates and 
                    geocode_response.candidates[0].content and 
                    geocode_response.candidates[0].content.parts and
                    len(geocode_response.candidates[0].content.parts) > 0):
                break
            
            geocode_part = geocode_response.candidates[0].content.parts[0]
            
            if hasattr(geocode_part, 'function_call') and geocode_part.function_call:
                next_function_call = geocode_part.function_call
                print(f"Additional function call: {next_function_call.name}, args: {next_function_call.args}")
                
                next_result = await self.bridge.handle_function_call(
                    next_function_call.name or "",
                    next_function_call.args or {}
                )
                all_results.append(next_result)
            else:
                break
        
        
        jobs_prompt = f"""Результаты выполнения всех функций геокодирования:

{json.dumps(all_results, ensure_ascii=False, indent=2)}

Исходный запрос пользователя: {prompt}

На основе результатов геокодирования создай список Job объектов. 

СТРУКТУРА ДАННЫХ:
Каждый элемент в массиве all_results имеет структуру:
{{
  "success": true,
  "results": [
    {{
      "address": "адрес",
      "coordinates": {{
        "longitude": число,
        "latitude": число
      }},
      "quality": "LOCATION" или "STREET"
    }}
  ],
  "count": число
}}

ИНСТРУКЦИЯ ПО СОЗДАНИЮ Job:
Для каждого элемента в all_results[].results[] создай Job со следующими полями:
- point: объект с полями {{"type": "Point", "coordinates": [longitude, latitude]}}
  где longitude берется из coordinates.longitude, latitude из coordinates.latitude
- address: адрес из поля address
- address_type: тип адреса из поля quality (преобразуй "LOCATION" или "STREET" в соответствующий enum)
- name: название работы из исходного запроса пользователя (например, "Мех мойка прил части дорог")
- comment: дополнительная информация о работе из исходного запроса

ВАЖНО: 
- coordinates должен быть массивом [longitude, latitude] в указанном порядке
- Если для одного адреса несколько результатов (несколько координат), создай отдельный Job для каждого результата
- Если в all_results несколько элементов, обработай все результаты из всех элементов

Верни массив Job объектов в формате JSON."""
        
        jobs_response = await self.client.aio.models.generate_content(
            model=model,
            contents=jobs_prompt,
            config=GenerateContentConfig(
                response_schema=list[Job],
                response_mime_type="application/json"
            )
        )
        
        return jobs_response.text
        

if __name__ == "__main__":
    system_prompt = """Ты - AI-ассистент для обработки запросов о дорожных работах и планировании маршрутов. Твоя задача - извлекать адреса из текста пользователя и получать их координаты.

ОСНОВНАЯ ЗАДАЧА:
Пользователь отправляет запросы о дорожных работах (мойка дорог, уборка и т.д.) с указанием адресов. Ты должен:
1. Найти ВСЕ адреса в тексте запроса
2. Для каждого адреса получить координаты через функцию forward_geocode
3. Вернуть координаты всех найденных адресов

ПРИМЕР ЗАПРОСА:
"КДМ 897, Мех мойка прил части дорог: Проспект металлургов 67, Олимпийская Самара, скажи координаты всех адресов"
В этом запросе два адреса:
- Проспект металлургов 67, Самара
- Олимпийская, Самара

ИНСТРУКЦИЯ ПО ИЗВЛЕЧЕНИЮ АДРЕСОВ:
1. Внимательно прочитай весь текст запроса
2. Найди все упоминания улиц, проспектов, площадей с номерами домов или без
3. Определи город (может быть указан явно или подразумеваться из контекста)
4. Если город не указан, но есть контекстные подсказки - используй их
5. Раздели запятыми или другими разделителями - это могут быть разные адреса

ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ forward_geocode:

1. ФОРМАТ АДРЕСА:
   - Адрес должен быть ПОЛНЫМ и включать ГОРОД
   - Формат: "номер_дома, название_улицы, город"
   - Примеры правильных форматов:
     * "67, проспект Металлургов, Самара"
     * "10, улица Ленина, Москва"
     * "Олимпийская, Самара" (если нет номера дома)
   - НЕ используй формат "город, улица, номер" - это не работает
   - Всегда указывай город в конце адреса

2. ПАРАМЕТР address_type:
   - ОБЯЗАТЕЛЬНО указывай address_type для каждого адреса
   - Используй "LOCATION" для конкретных адресов с номером дома
   - Используй "STREET" для улиц без номера дома
   - Для адресов типа "Проспект металлургов 67" используй "LOCATION"
   - Для адресов типа "Олимпийская" (без номера) используй "STREET"

3. ПАРАМЕТР language:
   - Для русских адресов используй "ru"
   - Для английских адресов используй "en"

4. ОБРАБОТКА НЕСКОЛЬКИХ АДРЕСОВ:
   - Если в запросе несколько адресов, вызови forward_geocode для КАЖДОГО адреса отдельно
   - Не пытайся объединять адреса в один вызов
   - Для каждого адреса используй правильный формат и address_type

5. ПРИМЕРЫ ВЫЗОВА:
   - Адрес с номером дома: address="67, проспект Металлургов, Самара", address_type="LOCATION", language="ru"
   - Только улица: address="Олимпийская, Самара", address_type="STREET", language="ru"

6. ОТВЕТ ФУНКЦИИ:
   - Функция возвращает координаты (latitude, longitude) и качество геокодирования
   - Если геокодирование не удалось, попробуй другой формат адреса или используй suggest_addresses для поиска правильного формата

ФОРМАТ ОТВЕТА:
После получения координат всех адресов, создай список Job объектов. Каждый Job должен содержать:
- point: объект Point с координатами (coordinates: [longitude, latitude])
- address: адрес из результатов геокодирования
- address_type: тип адреса (LOCATION или STREET)
- name: название работы из запроса пользователя
- comment: дополнительная информация о работе

Верни массив Job объектов в формате JSON.

ВАЖНО: 
- Всегда формируй адрес в формате "номер, улица, город" и указывай address_type="LOCATION" для адресов с номером дома
- Если в запросе несколько адресов, обработай ВСЕ адреса
- Если адрес не найден, попробуй разные варианты формата
- Не создавай Job объекты для одинаковых адресов, если это не другая работа или т.п."""

    prompt = "КДМ 897, Мех мойка прил части дорог: Проспект металлургов 67 ,Олимпийская Самара"
    
    full_prompt = f"{system_prompt}\n\nЗапрос пользователя: {prompt}"
    
    genai = GoogleGenAI()
    response = asyncio.run(genai.generate_with_tools(full_prompt))
    jobs = json.loads(response)
    for job in jobs:
        print(Job.model_validate(job).model_dump_json())