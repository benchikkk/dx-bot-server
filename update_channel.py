#!/usr/bin/env python3
"""
Скрипт для обновления настроек канала
"""

import os
import asyncio
from telegram import Bot

# Новые настройки
NEW_BOT_TOKEN = "8440826252:AAEZbVkLMUmsDfJzcbTvyzl2agZYgKVbYXM"
NEW_CHAT_ID = "-1002549644699"

async def update_channel_settings():
    """Обновляем настройки канала"""
    print("🔄 Обновление настроек канала...")
    print(f"📝 Новый CHAT_ID: {NEW_CHAT_ID}")
    print(f"🔑 Новый BOT_TOKEN: {NEW_BOT_TOKEN[:10]}...")
    
    try:
        # Создаем экземпляр бота с новыми настройками
        bot = Bot(token=NEW_BOT_TOKEN)
        
        # Тестовое сообщение
        test_message = """
🎯 **DX Bot - Настройка канала**

✅ Бот успешно настроен для работы с каналом!

📊 Функции:
• Автоматический мониторинг токенов каждые 10 минут
• Уведомления о новых токенах
• Статистика и управление через команды

⚙️ Настройки:
• Проверка каждые 10 минут
• Очистка каждые 15 минут
• Фильтры: MC $150K-$15M, объём ≥$75K

🎉 Бот готов к работе в канале!
        """
        
        # Отправляем сообщение в новый канал
        await bot.send_message(
            chat_id=NEW_CHAT_ID,
            text=test_message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        print("✅ Сообщение успешно отправлено в новый канал!")
        print("📱 Проверьте ваш канал")
        
        # Показываем инструкции для .env файла
        print("\n📝 Для постоянной настройки создайте файл .env:")
        print("=" * 50)
        print("BOT_TOKEN=8440826252:AAEZbVkLMUmsDfJzcbTvyzl2agZYgKVbYXM")
        print("CHAT_ID=-1002549644699")
        print("SAVE_SCREENSHOTS=false")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        print("\n🔧 Возможные причины:")
        print("• Бот не добавлен в канал")
        print("• У бота нет прав администратора")
        print("• Неправильный CHAT_ID")
        print("• Неправильный BOT_TOKEN")

if __name__ == "__main__":
    asyncio.run(update_channel_settings())

