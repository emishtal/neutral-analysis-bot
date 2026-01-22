"""
Интеграция с Claude API (Anthropic)
Отправка запросов и получение анализа
"""

import httpx
import logging
from typing import Dict, Any
from config import Config

logger = logging.getLogger(__name__)


class ClaudeAPI:
    """Класс для работы с Claude API"""
    
    def __init__(self):
        self.api_key = Config.CLAUDE_API_KEY
        self.model = Config.CLAUDE_MODEL
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def get_analysis(self, prompt: str, tariff: str = "basic") -> str:
        """
        Получить анализ от Claude
        
        Args:
            prompt: Промпт с описанием ситуации
            tariff: Тариф (basic или extended) - влияет на max_tokens
        
        Returns:
            Текст анализа
        """
        # Определяем max_tokens в зависимости от тарифа
        max_tokens = 1000 if tariff == "basic" else 1500
        
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Извлекаем текст ответа
                if "content" in result and len(result["content"]) > 0:
                    analysis = result["content"][0]["text"]
                    logger.info(f"Analysis received, length: {len(analysis)}")
                    return analysis
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return "Ошибка: не удалось получить анализ"
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                return "Ошибка: неверный API ключ Claude"
            elif e.response.status_code == 429:
                return "Ошибка: превышен лимит запросов к Claude API"
            else:
                return f"Ошибка API: {e.response.status_code}"
                
        except httpx.TimeoutException:
            logger.error("Request timeout")
            return "Ошибка: превышено время ожидания ответа"
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Неожиданная ошибка: {str(e)}"
    
    async def test_connection(self) -> bool:
        """
        Проверить подключение к Claude API
        
        Returns:
            True если подключение успешно
        """
        test_prompt = "Ответь одним словом: тест"
        
        try:
            result = await self.get_analysis(test_prompt)
            return "Ошибка" not in result
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
