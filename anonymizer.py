"""
Модуль для обезличивания данных
Автоматически заменяет имена, места, даты на обобщённые версии
"""

import re
from datetime import datetime, timedelta


def anonymize_text(text, participants=None):
    """
    Обезличивает текст, заменяя имена, места, даты
    
    Args:
        text: Исходный текст
        participants: Строка с участниками (опционально)
    
    Returns:
        Обезличенный текст
    """
    if not text:
        return text
    
    anonymized = text
    
    # 1. Заменяем имена участников на "Сторона А", "Сторона Б"
    if participants:
        names = extract_names(participants)
        for i, name in enumerate(names):
            if name:
                side = f"Сторона {chr(65 + i)}"  # A, B, C...
                anonymized = anonymized.replace(name, side)
                anonymized = anonymized.replace(name.lower(), side)
                anonymized = anonymized.replace(name.capitalize(), side)
    
    # 2. Удаляем популярные имена (если не указаны в participants)
    common_names = [
        'Иван', 'Мария', 'Александр', 'Елена', 'Дмитрий', 'Ольга',
        'Сергей', 'Анна', 'Андрей', 'Наталья', 'Алексей', 'Татьяна',
        'Владимир', 'Ирина', 'Евгений', 'Светлана', 'Николай', 'Людмила'
    ]
    
    for name in common_names:
        if name in anonymized:
            anonymized = anonymized.replace(name, "Партнёр")
    
    # 3. Удаляем конкретные адреса
    # "ул. Ленина", "улица Пушкина", "проспект Мира"
    anonymized = re.sub(r'ул\.\s+[А-Яа-я]+', 'улица', anonymized)
    anonymized = re.sub(r'улица\s+[А-Яа-я]+', 'улица', anonymized)
    anonymized = re.sub(r'проспект\s+[А-Яа-я]+', 'проспект', anonymized)
    anonymized = re.sub(r'переулок\s+[А-Яа-я]+', 'переулок', anonymized)
    
    # 4. Удаляем названия городов (кроме очень общих)
    cities = [
        'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург',
        'Казань', 'Нижний Новгород', 'Челябинск', 'Самара', 'Омск',
        'Ростов-на-Дону', 'Уфа', 'Красноярск', 'Воронеж', 'Пермь'
    ]
    
    for city in cities:
        anonymized = anonymized.replace(city, "город")
        anonymized = anonymized.replace(city.lower(), "город")
    
    # 5. Удаляем конкретные даты
    # "15 января", "2025 года", "в понедельник"
    anonymized = re.sub(r'\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)', 'в определённый день', anonymized)
    anonymized = re.sub(r'\d{4}\s+года', 'в недавнем времени', anonymized)
    
    # 6. Удаляем названия компаний
    # "ООО Рога и Копыта", "ИП Иванов"
    anonymized = re.sub(r'ООО\s+[А-Яа-я\s]+', 'компания', anonymized)
    anonymized = re.sub(r'ИП\s+[А-Яа-я]+', 'предприниматель', anonymized)
    anonymized = re.sub(r'ЗАО\s+[А-Яа-я\s]+', 'компания', anonymized)
    anonymized = re.sub(r'АО\s+[А-Яа-я\s]+', 'компания', anonymized)
    
    # 7. Удаляем телефоны
    anonymized = re.sub(r'\+7\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}', '[телефон]', anonymized)
    anonymized = re.sub(r'8\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}', '[телефон]', anonymized)
    
    # 8. Удаляем email
    anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[email]', anonymized)
    
    return anonymized


def extract_names(participants):
    """
    Извлекает имена из строки участников
    
    Args:
        participants: Строка типа "я и Мария", "Иван, Петр и я"
    
    Returns:
        Список имён
    """
    if not participants:
        return []
    
    # Убираем "я", "мы", "и"
    cleaned = participants.replace('я', '').replace('мы', '').replace('и', ',')
    
    # Разбиваем по запятым
    parts = [p.strip() for p in cleaned.split(',')]
    
    # Фильтруем пустые и короткие
    names = [p for p in parts if len(p) > 2]
    
    return names[:5]  # Максимум 5 участников


def extract_key_word(analysis_text):
    """
    Извлекает ключевое слово из анализа
    
    Args:
        analysis_text: Текст анализа
    
    Returns:
        Ключевое слово/фраза или None
    """
    # Ищем паттерн: Слово / фраза: «...»
    match = re.search(r'Слово / фраза:\s*[«"]([^»"]+)[»"]', analysis_text)
    
    if match:
        return match.group(1)
    
    return None


def extract_conflict_type(analysis_text):
    """
    Извлекает тип конфликта из расширенного анализа
    
    Args:
        analysis_text: Текст расширенного анализа
    
    Returns:
        Тип конфликта или "неизвестно"
    """
    if not analysis_text:
        return "неизвестно"
    
    # Ищем паттерн: Тип ситуации: конфликт ...
    match = re.search(r'Тип ситуации:\s*конфликт\s+([А-Яа-я]+)', analysis_text)
    
    if match:
        return match.group(1)
    
    # Если не нашли, возвращаем "неизвестно"
    return "неизвестно"


def create_anonymized_record(analysis_data):
    """
    Создаёт анонимную запись из полного анализа
    
    Args:
        analysis_data: Словарь с данными анализа
    
    Returns:
        Словарь с анонимными данными
    """
    # Обезличиваем ситуацию
    anonymized_situation = anonymize_text(
        analysis_data.get('situation', ''),
        analysis_data.get('participants', '')
    )
    
    # Создаём шаблон ситуации (первые 100 символов)
    situation_template = anonymized_situation[:100] + "..." if len(anonymized_situation) > 100 else anonymized_situation
    
    # Извлекаем ключевое слово
    key_word = extract_key_word(analysis_data.get('initial_analysis', ''))
    
    # Извлекаем тип конфликта
    conflict_type = extract_conflict_type(analysis_data.get('final_analysis', ''))
    
    # Определяем месяц (без дня!)
    created_at = analysis_data.get('created_at', datetime.now())
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    created_month = created_at.strftime('%Y-%m')
    
    # Метрики качества
    final_text = analysis_data.get('final_analysis', '')
    
    quality_metrics = {
        'has_all_blocks': check_has_all_blocks(final_text),
        'block4_correct': check_block4_format(final_text),
        'has_questions': check_has_questions(final_text),
        'has_advice': check_has_advice(final_text),
        'key_word_found': key_word is not None
    }
    
    return {
        'created_month': created_month,
        'conflict_type': conflict_type,
        'key_word': key_word,
        'situation_template': situation_template,
        'tariff': analysis_data.get('tariff', 'unknown'),
        'quality_metrics': quality_metrics
    }


def check_has_all_blocks(text):
    """Проверяет наличие всех 5 блоков в расширенном"""
    if not text:
        return False
    
    blocks = [
        'Тип ситуации',
        'Где произошёл структурный сбой',
        'Почему обе стороны чувствуют себя правыми',
        'Структурные границы конфликта',
        'Возможные структурные пути выхода'
    ]
    
    return all(block in text for block in blocks)


def check_block4_format(text):
    """Проверяет правильность формата блока 4"""
    if not text:
        return False
    
    # Ищем правильную вводную фразу
    correct_intro = "Конфликт стал возможен, потому что не было зафиксировано:"
    
    return correct_intro in text


def check_has_questions(text):
    """Проверяет наличие вопросов в блоке 4"""
    if not text:
        return False
    
    # Ищем блок 4
    match = re.search(r'Структурные границы конфликта(.+?)(?=##|Возможные структурные пути|$)', text, re.DOTALL)
    
    if not match:
        return False
    
    block4_text = match.group(1)
    
    # Проверяем наличие вопросительных знаков
    return '?' in block4_text


def check_has_advice(text):
    """Проверяет наличие советов в блоке 5"""
    if not text:
        return False
    
    # Ищем блок 5
    match = re.search(r'Возможные структурные пути выхода(.+?)$', text, re.DOTALL)
    
    if not match:
        return False
    
    block5_text = match.group(1)
    
    # Проверяем запрещённые слова
    forbidden_words = ['нужно', 'следует', 'стоит', 'рекомендуется', 'лучше', 'правильно']
    
    return any(word in block5_text.lower() for word in forbidden_words)


# Пример использования
if __name__ == "__main__":
    # Тест обезличивания
    text = "Иван и Мария спорят о том, как вести домашний бюджет в их квартире на ул. Ленина в Москве"
    participants = "я, Мария"
    
    anonymized = anonymize_text(text, participants)
    print("Исходный:", text)
    print("Обезличенный:", anonymized)
    
    # Должно быть:
    # "Сторона A и Сторона Б спорят о том, как вести домашний бюджет в их квартире на улица в город"
