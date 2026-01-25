#!/usr/bin/env python3
import httpx
import base64
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("ДИАГНОСТИКА GIGACHAT API")
print("=" * 60)

# Читаем переменные
client_id = os.getenv('GIGACHAT_CLIENT_ID')
client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
scope = os.getenv('GIGACHAT_SCOPE')

# Проверка 1: Есть ли переменные вообще?
print("\n1. ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
print(f"   Client ID: {'✅ Есть' if client_id else '❌ НЕТ!'}")
print(f"   Client Secret: {'✅ Есть' if client_secret else '❌ НЕТ!'}")
print(f"   Scope: {scope if scope else '❌ НЕТ!'}")

if not client_id or not client_secret:
    print("\n❌ ОШИБКА: Client ID или Secret не найдены в .env!")
    print("Проверь файл .env")
    exit(1)

# Проверка 2: Длина и формат
print("\n2. ДЛИНА ПЕРЕМЕННЫХ:")
print(f"   Client ID длина: {len(client_id)} символов")
print(f"   Client Secret длина: {len(client_secret)} символов")
print(f"   Scope: '{scope}'")

# Проверка 3: Первые/последние символы (для проверки копипасты)
print("\n3. ПРОВЕРКА ФОРМАТА:")
print(f"   Client ID начинается: '{client_id[:8]}...'")
print(f"   Client ID заканчивается: '...{client_id[-8:]}'")
print(f"   Client Secret начинается: '{client_secret[:8]}...'")
print(f"   Client Secret заканчивается: '...{client_secret[-8:]}'")

# Проверка 4: Пробелы
print("\n4. ПРОВЕРКА НА ПРОБЕЛЫ:")
if client_id.strip() != client_id:
    print("   ⚠️ Client ID содержит лишние пробелы!")
    client_id = client_id.strip()
    print("   → Убрал пробелы")
else:
    print("   ✅ Client ID без пробелов")
    
if client_secret.strip() != client_secret:
    print("   ⚠️ Client Secret содержит лишние пробелы!")
    client_secret = client_secret.strip()
    print("   → Убрал пробелы")
else:
    print("   ✅ Client Secret без пробелов")

# Проверка 5: Попытка авторизации
print("\n5. ПОПЫТКА АВТОРИЗАЦИИ:")
print("   Отправляю запрос в GigaChat API...")

try:
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"scope": scope}
    
    with httpx.Client(verify=False, timeout=30.0) as client:
        response = client.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers=headers,
            data=data
        )
        
        print(f"\n   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\n   ✅ ✅ ✅ АВТОРИЗАЦИЯ УСПЕШНА! ✅ ✅ ✅")
            result = response.json()
            print(f"   Access Token получен: {result['access_token'][:30]}...")
            print(f"   Expires in: {result.get('expires_at', 'unknown')} секунд")
        else:
            print(f"\n   ❌ ОШИБКА АВТОРИЗАЦИИ!")
            print(f"   HTTP Код: {response.status_code}")
            print(f"   Ответ сервера:")
            print(f"   {response.text}")
            
            if response.status_code == 401:
                print("\n   💡 РЕШЕНИЕ:")
                print("   1. Проверь Client ID и Secret на портале developers.sber.ru")
                print("   2. Пересоздай Client Secret (он показывается один раз!)")
                print("   3. Скопируй заново БЕЗ лишних пробелов")
            
except Exception as e:
    print(f"\n   ❌ ИСКЛЮЧЕНИЕ ПРИ ЗАПРОСЕ:")
    print(f"   Тип: {type(e).__name__}")
    print(f"   Текст: {str(e)}")
    print(f"\n   💡 РЕШЕНИЕ:")
    print("   Проверь Client ID и Secret в .env файле")

print("\n" + "=" * 60)
