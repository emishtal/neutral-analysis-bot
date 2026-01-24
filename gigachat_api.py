"""
Интеграция с GigaChat API (Сбер)
OAuth авторизация и отправка запросов
"""

import httpx
import logging
import base64
import uuid
from typing import Optional
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)


class GigaChatAPI:
    """Класс для работы с GigaChat API"""
    
    def __init__(self):
        self.client_id = Config.GIGACHAT_CLIENT_ID
        self.client_secret = Config.GIGACHAT_CLIENT_SECRET
        self.scope = Config.GIGACHAT_SCOPE
        
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        self.access_token = None
        self.token_expires_at = None
    
    async def _get_access_token(self) -> str:
        """
        Получить OAuth токен для GigaChat API
        Токен кэшируется и обновляется по мере необходимости
        """
        # Проверяем есть ли валидный токен
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):
                return self.access_token
        
        # Получаем новый токен
        try:
            # Создаем Authorization заголовок
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "scope": self.scope
            }
            
            async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
                response = await client.post(
                    self.auth_url,
                    headers=headers,
                    data=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                self.access_token = result["access_token"]
                # Токен живет обычно 30 минут
                self.token_expires_at = datetime.now() + timedelta(seconds=result.get("expires_at", 1800))
                
                logger.info("GigaChat access token obtained")
                return self.access_token
                
        except Exception as e:
            logger.error(f"Failed to get GigaChat access token: {e}")
            raise
    
    async def get_analysis(self, prompt: str, tariff: str = "basic") -> str:
        """
        Получить анализ от GigaChat
        
        Args:
            prompt: Промпт с описанием ситуации
            tariff: Тариф (basic или extended)
        
        Returns:
            Текст анализа
        """
        # Получаем токен
        try:
            token = await self._get_access_token()
        except Exception as e:
            return f"Ошибка авторизации GigaChat: {str(e)}"
        
        # Определяем параметры в зависимости от тарифа
        max_tokens = 2048 if tariff == "basic" else 4096
        temperature = 0.1  # Низкая температура для нейтральности
        
        # Формируем запрос
        data = {
            "model": "GigaChat",  # Можно использовать GigaChat-Plus для лучшего качества
            "messages": [
                {
                    "role": "system",
                    "content": "Ты нейтральный аналитик конфликтных ситуаций."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "repetition_penalty": 1.0
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Извлекаем текст ответа
                if "choices" in result and len(result["choices"]) > 0:
                    analysis = result["choices"][0]["message"]["content"]
                    logger.info(f"Analysis received from GigaChat, length: {len(analysis)}")
                    return analysis
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return "Ошибка: не удалось получить анализ от GigaChat"
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                return "Ошибка: неверные учетные данные GigaChat"
            elif e.response.status_code == 429:
                return "Ошибка: превышен лимит запросов к GigaChat API"
            else:
                return f"Ошибка GigaChat API: {e.response.status_code}"
                
        except httpx.TimeoutException:
            logger.error("Request timeout")
            return "Ошибка: превышено время ожидания ответа от GigaChat"
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Неожиданная ошибка: {str(e)}"
    
    async def test_connection(self) -> bool:
        """
        Проверить подключение к GigaChat API
        
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
