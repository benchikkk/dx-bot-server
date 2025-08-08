#!/usr/bin/env python3
"""
Скрипт для тестирования отправки сообщений в канал
"""

import asyncio
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

async def test_channel_message():
    """Тестируем отправку сообщения в канал"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не настроен")
        return
    
    if not CHAT_ID:
        print("❌ CHAT_ID не настроен")
        return
    
    print(f"🤖 Тестирование отправки в канал")
    print(f"📝 CHAT_ID: {CHAT_ID}")
    print(f"🔑 BOT_TOKEN: {BOT_TOKEN[:10]}...")
    
    try:
        # Создаем экземпляр бота
        bot = Bot(token=BOT_TOKEN)
        
        # Тестовое сообщение
        test_message = """
🧪 **Тестовое сообщение от DX Bot**

✅ Бот успешно настроен для работы с каналом!

📊 Функции:
• Автоматический мониторинг токенов
• Уведомления о новых токенах
• Статистика и управление

⚙️ Настройки:
• Проверка каждые 10 минут
• Очистка каждые 15 минут
• Фильтры: MC $150K-$15M

🎯 Если вы видите это сообщение, значит бот готов к работе!
        """
        
        # Отправляем сообщение
        await bot.send_message(
            chat_id=CHAT_ID,
            text=test_message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        print("✅ Сообщение успешно отправлено в канал!")
        print("📱 Проверьте ваш канал")
        
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        print("\n🔧 Возможные причины:")
        print("• Бот не добавлен в канал")
        print("• У бота нет прав администратора")
        print("• Неправильный CHAT_ID")
        print("• Неправильный BOT_TOKEN")

if __name__ == "__main__":
    asyncio.run(test_channel_message())

