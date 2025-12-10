import json
from typing import Optional, Type
from dotenv import load_dotenv
import os
from google import genai
from google.genai.types import GenerateContentConfig, Schema, Tool
from models.job import Job
from pydantic import BaseModel
from services.gemini_mcp_bridge import GeminiMCPBridge
from schemas.gemini_functions import get_geocoding_functions

load_dotenv()

class GeminiWithMCP:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))
        self.bridge = GeminiMCPBridge()
        self.functions = get_geocoding_functions()
    
    async def generate_with_tools(self, prompt: str, model: str = "gemini-2.5-pro", response_schema: Optional[Type[BaseModel]] = None):
        """Генерация с использованием MCP инструментов."""
        
        # Конфигурация с функциями
        config: GenerateContentConfig = GenerateContentConfig(
            tools=[Tool(function_declarations=self.functions)],
            response_schema=Schema(**response_schema.model_json_schema()) if response_schema else None
        )
        
        # Первый запрос к Gemini
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        # Проверяем, есть ли вызов функции
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            if hasattr(first_part, 'function_call') and first_part.function_call:
                function_call = first_part.function_call
                
                # Вызываем MCP функцию
                function_result = await self.bridge.handle_function_call(
                    function_call.name or "",
                    function_call.args or {}
                )
            
                # Отправляем результат обратно в Gemini
                follow_up_prompt = f"""
                    Результат выполнения функции {function_call.name}:

                    {json.dumps(function_result, ensure_ascii=False, indent=2)}

                    Продолжи обработку с учетом этого результата.
                    """
                
                final_response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=follow_up_prompt,
                    config=config
                )
                
                if response_schema and final_response.candidates and final_response.candidates[0].content and final_response.candidates[0].content.parts:
                    # Возвращаем структурированный ответ
                    try:
                        content = final_response.candidates[0].content.parts[0].text
                        if content:
                            return response_schema.model_validate_json(content)
                    except Exception:
                        pass
                
                return final_response.text if final_response.text else ""
        
        if response_schema and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            # Возвращаем структурированный ответ
            try:
                content = response.candidates[0].content.parts[0].text
                if content:
                    return response_schema.model_validate_json(content)
            except Exception:
                pass
        
        return response.text if response.text else ""
    
    async def generate_with_multiple_tools(self, prompt: str, model: str = "gemini-2.5-pro"):
        """Генерация с множественными вызовами функций."""
        
        config: GenerateContentConfig = GenerateContentConfig(
            tools=[Tool(function_declarations=self.functions)]
        )
        
        # Первый запрос
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        # Обрабатываем все вызовы функций
        function_results = []
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    
                    # Вызываем MCP функцию
                    result = await self.bridge.handle_function_call(
                        function_call.name or "",
                        function_call.args or {}
                    )
                    
                    function_results.append({
                        "function": function_call.name or "",
                        "args": function_call.args or {},
                        "result": result
                    })
        
        # Отправляем все результаты обратно в Gemini
        if function_results:
            results_text = "\n".join([
                f"Функция {fr['function']}: {json.dumps(fr['result'], ensure_ascii=False)}"
                for fr in function_results
            ])
            
            final_prompt = f"""
                Результаты выполнения функций:

                {results_text}

                Продолжи обработку с учетом всех результатов.
                """
            
            final_response = await self.client.aio.models.generate_content(
                model=model,
                contents=final_prompt,
                config=config
            )
            
            return final_response.text if final_response.text else ""
        
        return response.text if response.text else ""
    
    async def generate_planning_input_with_geocoding(self, prompt: str):
        """Генерация PlanningInput с автоматическим геокодированием."""
        
        # Улучшенный промпт с инструкциями по использованию геокодирования
        enhanced_prompt = f"""
            {prompt}

            Для создания Job объектов используй функцию forward_geocode для получения координат адресов.
            Найди все адреса в тексте и получи их координаты.

            Пример использования:
            - Вызови forward_geocode для "проспект Металлургов Самара"
            - Вызови forward_geocode для "улица Олимпийская Самара"
            - И так далее для всех адресов

            После получения координат создай Job объекты с правильными координатами.
            """
        
        return await self.generate_with_tools(enhanced_prompt)
    
    async def geocode_addresses_from_text(self, text: str):
        """Извлечение и геокодирование адресов из текста."""
        
        prompt = f"""
            Проанализируй следующий текст и найди все адреса:

            {text}

            Для каждого найденного адреса вызови функцию forward_geocode чтобы получить координаты.
            Верни список всех адресов с их координатами.
            """
        
        return await self.generate_with_tools(prompt)
    
    async def create_job_with_coordinates(self, address: str):
        """Создание Job объекта с координатами для указанного адреса."""
        
        prompt = f"""
            Создай Job объект для адреса: {address}

            Сначала получи координаты этого адреса используя функцию forward_geocode.
            Затем создай Job объект с полученными координатами.

            Job должен содержать:
            - point: координаты в формате {{"type": "Point", "coordinates": [longitude, latitude]}}
            - job_id: уникальный идентификатор
            - name: название задачи
            - address: адрес
            - address_type: "STREET"
            """
        
        return await self.generate_with_tools(prompt)
    
    async def generate_with_schema(self, prompt: str, response_schema: Type[BaseModel], model: str = "gemini-2.5-pro"):
        """Генерация структурированного ответа с автоматическим геокодированием."""
        
        # Проверяем, нужны ли координаты для схемы
        schema_dict = response_schema.model_json_schema()
        needs_coordinates = self._schema_needs_coordinates(schema_dict)
        
        if needs_coordinates:
            # Если нужны координаты, используем инструменты геокодирования
            enhanced_prompt = f"""
                {prompt}

                ВАЖНО: Используй доступные функции геокодирования для получения координат адресов.
                Если в тексте есть адреса, сначала получи их координаты через forward_geocode, 
                затем создай структурированный ответ согласно схеме.

                Ответ должен быть в формате JSON, строго соответствующем предоставленной схеме.
                """
            return await self.generate_with_tools(enhanced_prompt, model, response_schema)
        else:
            # Если координаты не нужны, генерируем без инструментов
            config: GenerateContentConfig = GenerateContentConfig(
                response_schema=Schema(**response_schema.model_json_schema())
            )
            
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                try:
                    content = response.candidates[0].content.parts[0].text
                    if content:
                        return response_schema.model_validate_json(content)
                except Exception:
                    pass
            
            return response.text if response.text else ""
    
    def _schema_needs_coordinates(self, schema_dict: dict) -> bool:
        """Проверяет, нужны ли координаты для данной схемы."""
        def check_schema(obj):
            if isinstance(obj, dict):
                # Проверяем наличие полей, связанных с координатами
                if 'properties' in obj:
                    props = obj['properties']
                    coord_fields = ['point', 'coordinates', 'longitude', 'latitude', 'address']
                    if any(field in props for field in coord_fields):
                        return True
                
                # Рекурсивно проверяем вложенные объекты
                for value in obj.values():
                    if check_schema(value):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if check_schema(item):
                        return True
            return False
        
        return check_schema(schema_dict)
    
    async def generate_planning_input_structured(self, prompt: str, model: str = "gemini-2.5-pro"):
        """Генерация PlanningInput с автоматическим геокодированием и структурированным ответом."""
        from models.planning_input import PlanningInput
        
        enhanced_prompt = f"""
            {prompt}

            Создай PlanningInput объект со следующими требованиями:

            1. Найди все адреса в тексте
            2. Используй функцию forward_geocode для получения координат каждого адреса
            3. Создай Job объекты с полученными координатами
            4. Создай Worker объекты (минимум один)
            5. Создай ServicePoint объекты (минимум один с типом DEPOT)
            6. Настрой PlanningSettings с подходящими параметрами

            Структура PlanningInput:
            - jobs: список Job объектов с координатами
            - workers: список Worker объектов
            - service_points: список ServicePoint объектов (минимум один DEPOT)
            - settings: настройки планирования
            - initial_missions: пустой список
            - zones: пустой список

            Каждый Job должен содержать:
            - point: координаты в формате {{"type": "Point", "coordinates": [longitude, latitude]}}
            - job_id: уникальный идентификатор
            - name: название задачи
            - address: адрес
            - address_type: "STREET"

            Каждый Worker должен содержать:
            - worker_id: уникальный идентификатор
            - name: название работника/техники
            - tags: список тегов (например, ["мойка"])

            Каждый ServicePoint должен содержать:
            - point: координаты депо
            - service_point_id: уникальный идентификатор
            - name: название депо
            - service_point_type: "DEPOT"

            Settings должны содержать:
            - name: название планирования
            - locale: "ru"
            - timezone: "Europe/Samara"
            """
        
        return await self.generate_with_schema(enhanced_prompt, PlanningInput, model)
    
    async def generate_planning_input_step_by_step(self, prompt: str, model: str = "gemini-2.5-flash"):
        """Поэтапная генерация PlanningInput с разбиением на несколько шагов."""
        from models.planning_input import PlanningInput
        
        # Шаг 1: Извлечение адресов и геокодирование
        addresses_prompt = f"""
{prompt}

Найди все адреса в тексте и получи их координаты используя функцию forward_geocode.
Верни список адресов с координатами в формате:
{{
    "addresses": [
        {{
            "address": "адрес",
            "coordinates": {{"longitude": 50.123, "latitude": 53.456}},
            "job_name": "название задачи"
        }}
    ]
}}
"""
        
        addresses_result = await self.generate_with_tools(addresses_prompt, model)
        
        # Шаг 2: Создание Job объектов
        jobs_prompt = f"""
На основе следующих адресов с координатами создай Job объекты:

{addresses_result}

Каждый Job должен содержать:
- point: {{"type": "Point", "coordinates": [longitude, latitude]}}
- job_id: уникальный идентификатор (job-1, job-2, etc.)
- name: название задачи
- address: адрес
- address_type: "STREET"

Верни список Job объектов в формате JSON.
"""
        
        jobs_result = await self.generate_with_tools(jobs_prompt, model)
        
        # Шаг 3: Создание Worker объектов
        workers_prompt = """
Создай Worker объекты для планирования. Минимум один работник.

Каждый Worker должен содержать:
- worker_id: уникальный идентификатор (например, "KDM-897")
- name: название работника/техники
- tags: список тегов (например, ["мойка"])

Верни список Worker объектов в формате JSON.
"""
        
        workers_result = await self.generate_with_tools(workers_prompt, model)
        
        # Шаг 4: Создание ServicePoint объектов
        service_points_prompt = """
Создай ServicePoint объекты для планирования. Минимум один с типом DEPOT.

Каждый ServicePoint должен содержать:
- point: {"type": "Point", "coordinates": [50.186429, 53.2151]} (координаты депо)
- service_point_id: уникальный идентификатор (например, "depot-1")
- name: название депо
- service_point_type: "DEPOT"

Верни список ServicePoint объектов в формате JSON.
"""
        
        service_points_result = await self.generate_with_tools(service_points_prompt, model)
        
        # Шаг 5: Сборка финального PlanningInput
        final_prompt = f"""
Собери финальный PlanningInput объект из следующих компонентов:

Jobs:
{jobs_result}

Workers:
{workers_result}

ServicePoints:
{service_points_result}

Создай полный PlanningInput объект со следующими полями:
- jobs: список Job объектов
- workers: список Worker объектов
- service_points: список ServicePoint объектов
- settings: {{
    "name": "Планирование мех мойки",
    "locale": "ru",
    "timezone": "Europe/Samara"
}}
- initial_missions: []
- zones: []

Верни полный PlanningInput объект в формате JSON.
"""
        
    async def generate_jobs_list(self, prompt: str, model: str = "gemini-2.5-flash"):
        """Генерация списка Job объектов с геокодированием."""
        
        enhanced_prompt = f"""
        {prompt}

        Найди все адреса в тексте и получи их координаты используя функцию forward_geocode.
        Создай Job объекты для каждого адреса.

        Каждый Job должен содержать:
        - point: {{"type": "Point", "coordinates": [longitude, latitude]}}
        - job_id: уникальный идентификатор (job-1, job-2, etc.)
        - name: название задачи
        - address: адрес
        - address_type: "STREET"
        - comment: дополнительная информация

        Верни список Job объектов в формате JSON.
        """
        
        config: GenerateContentConfig = GenerateContentConfig(
            tools=[Tool(function_declarations=self.functions)]
        )
        
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=enhanced_prompt,
            config=config
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            if hasattr(first_part, 'function_call') and first_part.function_call:
                function_call = first_part.function_call
                
                function_result = await self.bridge.handle_function_call(
                    function_call.name or "",
                    function_call.args or {}
                )
            
                follow_up_prompt = f"""
                    Результат выполнения функции {function_call.name}:

                    {json.dumps(function_result, ensure_ascii=False, indent=2)}

                    Теперь создай Job объекты на основе полученных координат.
                    Верни список Job объектов в формате JSON.
                    """
                
                final_response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=follow_up_prompt,
                    config=config
                )
                
                return final_response.text if final_response.text else ""
        
        return response.text if response.text else ""
