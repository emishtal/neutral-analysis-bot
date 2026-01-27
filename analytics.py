#!/usr/bin/env python3
"""
Аналитика использования бота
Запуск: python3 analytics.py
"""

import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

def get_db():
    """Подключение к БД"""
    return sqlite3.connect(DATABASE_PATH)

def print_section(title):
    """Красивый заголовок"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def general_stats():
    """Общая статистика"""
    print_section("ОБЩАЯ СТАТИСТИКА")
    
    db = get_db()
    cursor = db.cursor()
    
    # Всего пользователей
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
    total_users = cursor.fetchone()[0]
    print(f"👥 Всего пользователей: {total_users}")
    
    # Всего разборов
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total_analyses = cursor.fetchone()[0]
    print(f"📊 Всего разборов: {total_analyses}")
    
    # Разборов на пользователя
    if total_users > 0:
        avg_per_user = total_analyses / total_users
        print(f"📈 Среднее разборов на пользователя: {avg_per_user:.1f}")
    
    # Уточнений фактов
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE facts_updated = 1")
    with_refinement = cursor.fetchone()[0]
    if total_analyses > 0:
        refinement_rate = (with_refinement / total_analyses) * 100
        print(f"📝 Уточнений фактов: {with_refinement} ({refinement_rate:.1f}%)")
    
    db.close()

def tariff_stats():
    """Статистика по тарифам"""
    print_section("СТАТИСТИКА ПО ТАРИФАМ")
    
    db = get_db()
    cursor = db.cursor()
    
    # По тарифам
    cursor.execute("""
        SELECT tariff, COUNT(*) 
        FROM analyses 
        WHERE tariff IS NOT NULL
        GROUP BY tariff
    """)
    
    total = 0
    for row in cursor.fetchall():
        tariff = row[0] if row[0] else 'unknown'
        count = row[1]
        total += count
        print(f"💳 {tariff}: {count}")
    
    # Конверсия 49₽ → 99₽
    if total > 0:
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE tariff = 'extended'")
        extended = cursor.fetchone()[0]
        conversion = (extended / total) * 100
        print(f"\n📈 Конверсия basic → extended: {conversion:.1f}%")
    
    db.close()

def revenue_stats():
    """Статистика по доходам"""
    print_section("ДОХОДЫ")
    
    db = get_db()
    cursor = db.cursor()
    
    # Всего заработано
    cursor.execute("""
        SELECT SUM(amount) 
        FROM payments 
        WHERE status = 'completed'
    """)
    total_revenue = cursor.fetchone()[0] or 0
    print(f"💰 Всего заработано: {total_revenue}₽")
    
    # По тарифам
    cursor.execute("""
        SELECT tariff, SUM(amount), COUNT(*) 
        FROM payments 
        WHERE status = 'completed'
        GROUP BY tariff
    """)
    
    for row in cursor.fetchall():
        tariff, amount, count = row
        print(f"   {tariff}: {amount}₽ ({count} платежей)")
    
    # Средний чек
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) 
        FROM payments 
        WHERE status = 'completed'
    """)
    paying_users = cursor.fetchone()[0]
    
    if paying_users > 0:
        arpu = total_revenue / paying_users
        print(f"\n📊 Средний доход с пользователя (ARPU): {arpu:.0f}₽")
    
    db.close()

def time_stats():
    """Статистика по времени"""
    print_section("АКТИВНОСТЬ ПО ВРЕМЕНИ")
    
    db = get_db()
    cursor = db.cursor()
    
    # Сегодня
    today = datetime.now().date()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM analyses 
        WHERE DATE(created_at) = ?
    """, (today,))
    today_count = cursor.fetchone()[0]
    print(f"📅 Сегодня: {today_count} разборов")
    
    # Вчера
    yesterday = (datetime.now() - timedelta(days=1)).date()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM analyses 
        WHERE DATE(created_at) = ?
    """, (yesterday,))
    yesterday_count = cursor.fetchone()[0]
    print(f"📅 Вчера: {yesterday_count} разборов")
    
    # Неделя
    week_ago = (datetime.now() - timedelta(days=7)).date()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM analyses 
        WHERE DATE(created_at) >= ?
    """, (week_ago,))
    week_count = cursor.fetchone()[0]
    print(f"📅 За неделю: {week_count} разборов")
    
    # Месяц
    month_ago = (datetime.now() - timedelta(days=30)).date()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM analyses 
        WHERE DATE(created_at) >= ?
    """, (month_ago,))
    month_count = cursor.fetchone()[0]
    print(f"📅 За месяц: {month_count} разборов")
    
    db.close()

def popular_conflict_types():
    """Популярные типы конфликтов"""
    print_section("ТИПЫ КОНФЛИКТОВ (топ-5)")
    
    db = get_db()
    cursor = db.cursor()
    
    # По типу договорённости
    cursor.execute("""
        SELECT agreement_type, COUNT(*) as cnt
        FROM analyses
        WHERE agreement_type IS NOT NULL
        GROUP BY agreement_type
        ORDER BY cnt DESC
        LIMIT 5
    """)
    
    print("\n📋 По типу договорённости:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    db.close()

def api_usage():
    """Использование GigaChat API"""
    print_section("ИСПОЛЬЗОВАНИЕ GIGACHAT API")
    
    db = get_db()
    cursor = db.cursor()
    
    # Всего запросов к API
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE initial_analysis IS NOT NULL")
    basic_analyses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE final_analysis IS NOT NULL")
    extended_analyses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE facts_updated = 1")
    refinements = cursor.fetchone()[0]
    
    total_api_calls = basic_analyses + extended_analyses + refinements
    
    print(f"🔄 Всего запросов к API: {total_api_calls}")
    print(f"   Базовых разборов: {basic_analyses}")
    print(f"   Уточнений: {refinements}")
    print(f"   Расширенных: {extended_analyses}")
    
    # Лимит GigaChat Lite
    limit = 300
    remaining = limit - total_api_calls
    
    if remaining > 0:
        print(f"\n✅ Осталось запросов (лимит 300/день): {remaining}")
    else:
        print(f"\n⚠️  Превышен дневной лимит на {abs(remaining)} запросов")
    
    # Средняя стоимость при переходе на Pro
    if total_api_calls > 300:
        cost_per_request = 2  # примерно 2₽ за разбор
        daily_cost = total_api_calls * cost_per_request
        print(f"💰 Стоимость при GigaChat Pro: ~{daily_cost}₽/день")
    
    db.close()

def main():
    """Запуск всей аналитики"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "АНАЛИТИКА NEUTRAL ANALYSIS BOT" + " " * 17 + "║")
    print("║" + " " * 15 + f"{datetime.now().strftime('%d.%m.%Y %H:%M')}" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    
    general_stats()
    tariff_stats()
    revenue_stats()
    time_stats()
    popular_conflict_types()
    api_usage()
    
    print("\n" + "=" * 60)
    print("Готово! 🎉")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
