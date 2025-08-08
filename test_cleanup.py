#!/usr/bin/env python3
"""
Скрипт для тестирования функции очистки файлов
"""

import os
import glob
from datetime import datetime, timedelta
from config import *

def test_cleanup():
    """Тестируем функцию очистки"""
    print("🧹 Тестирование функции очистки файлов")
    print(f"📅 Текущее время: {datetime.now()}")
    print(f"⚙️ Настройки:")
    print(f"   - Интервал очистки: {CLEANUP_INTERVAL//60} минут")
    print(f"   - JSON файлы хранятся: {FILE_RETENTION_MINUTES} минут")
    print(f"   - Скриншоты хранятся: {SCREENSHOT_RETENTION_MINUTES} минут")
    print(f"   - Скриншоты включены: {SAVE_SCREENSHOTS}")
    
    # Проверяем существующие файлы
    json_files = glob.glob(os.path.join(JSON_HISTORY_FOLDER, "*.json"))
    screenshot_files = glob.glob(os.path.join(SCREENSHOTS_FOLDER, "*.png"))
    
    print(f"\n📁 Найдено файлов:")
    print(f"   - JSON файлов: {len(json_files)}")
    print(f"   - Скриншотов: {len(screenshot_files)}")
    
    # Показываем время создания файлов
    if json_files:
        print(f"\n📊 JSON файлы:")
        for file_path in json_files[:5]:  # Показываем первые 5
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            age_minutes = (datetime.now() - file_time).total_seconds() / 60
            print(f"   - {os.path.basename(file_path)}: {age_minutes:.1f} минут назад")
    
    if screenshot_files and SAVE_SCREENSHOTS:
        print(f"\n📸 Скриншоты:")
        for file_path in screenshot_files[:5]:  # Показываем первые 5
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            age_minutes = (datetime.now() - file_time).total_seconds() / 60
            print(f"   - {os.path.basename(file_path)}: {age_minutes:.1f} минут назад")
    
    # Симулируем очистку
    print(f"\n🔍 Симуляция очистки:")
    json_cutoff_time = datetime.now() - timedelta(minutes=FILE_RETENTION_MINUTES)
    screenshot_cutoff_time = datetime.now() - timedelta(minutes=SCREENSHOT_RETENTION_MINUTES)
    
    would_delete_json = 0
    would_delete_screenshots = 0
    
    for file_path in json_files:
        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if file_time < json_cutoff_time:
            would_delete_json += 1
    
    if SAVE_SCREENSHOTS:
        for file_path in screenshot_files:
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if file_time < screenshot_cutoff_time:
                would_delete_screenshots += 1
    
    print(f"   - JSON файлов будет удалено: {would_delete_json}")
    print(f"   - Скриншотов будет удалено: {would_delete_screenshots}")
    
    print(f"\n✅ Тест завершен!")

if __name__ == "__main__":
    test_cleanup()
