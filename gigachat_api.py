import httpx
import base64
import uuid
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GigaChatAPI:
    def __init__(self):
        self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
        self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        self.scope = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
        self.access_token = None
        self.token_expires_at = None
    
    async def _get_access_token(self):
        """Получить OAuth токен от GigaChat"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # OAuth запрос
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"scope": self.scope}
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
                response = await client.post(
                    "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                    headers=headers,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.access_token = result["access_token"]
                    # Фиксированное время жизни токена 30 минут (обход проблемы с expires_at)
                    self.token_expires_at = datetime.now() + timedelta(minutes=30)
                    logger.info(f"Token will expire at: {self.token_expires_at}")
                    return self.access_token
                else:
                    logger.error(f"Failed to get access token: HTTP {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Failed to get GigaChat access token: {e}")
            return None
    
    async def get_analysis(self, prompt: str, tariff: str = "basic") -> str:
        """Получить анализ ситуации от GigaChat"""
        token = await self._get_access_token()
        if not token:
            raise Exception("Ошибка авторизации GigaChat")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=90.0) as client:
                response = await client.post(
                    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"GigaChat API error: HTTP {response.status_code}")
                    raise Exception(f"Ошибка GigaChat API: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error calling GigaChat API: {e}")
            raise
