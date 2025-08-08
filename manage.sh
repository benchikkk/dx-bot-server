#!/bin/bash

# Скрипт для управления DX Bot на сервере

BOT_NAME="dx-bot"
COMPOSE_FILE="docker-compose.yml"

case "$1" in
    start)
        echo "🚀 Запускаем DX Bot..."
        docker-compose up -d
        echo "✅ Бот запущен"
        ;;
    stop)
        echo "🛑 Останавливаем DX Bot..."
        docker-compose down
        echo "✅ Бот остановлен"
        ;;
    restart)
        echo "🔄 Перезапускаем DX Bot..."
        docker-compose restart
        echo "✅ Бот перезапущен"
        ;;
    status)
        echo "📊 Статус DX Bot:"
        docker-compose ps
        ;;
    logs)
        echo "📋 Логи DX Bot:"
        docker-compose logs -f --tail=50
        ;;
    cleanup)
        echo "🧹 Очищаем старые файлы..."
        find bot_data/json_history -name "*.json" -mtime +1 -delete
        find bot_data/screenshots -name "*.png" -mtime +1 -delete
        echo "✅ Очистка завершена"
        ;;
    test-cleanup)
        echo "🧪 Тестируем настройки очистки..."
        python3 test_cleanup.py
        ;;
    test-channel)
        echo "📡 Тестируем отправку в канал..."
        python3 test_channel.py
        ;;
    update)
        echo "📦 Обновляем бота..."
        git pull
        docker-compose down
        docker-compose up -d --build
        echo "✅ Бот обновлен"
        ;;
    backup)
        echo "💾 Создаем резервную копию..."
        tar -czf "backup_$(date +%Y%m%d_%H%M%S).tar.gz" bot_data/ previous_tokens.json
        echo "✅ Резервная копия создана"
        ;;
    *)
        echo "🤖 DX Bot Manager"
        echo ""
        echo "Использование: $0 {start|stop|restart|status|logs|cleanup|update|backup}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить бота"
        echo "  stop    - Остановить бота"
        echo "  restart - Перезапустить бота"
        echo "  status  - Показать статус"
        echo "  logs    - Показать логи"
        echo "  cleanup - Очистить старые файлы"
        echo "  test-cleanup - Тестировать настройки очистки"
        echo "  test-channel - Тестировать отправку в канал"
        echo "  update  - Обновить бота"
        echo "  backup  - Создать резервную копию"
        echo ""
        echo "Telegram команды:"
        echo "  /start   - Информация о боте"
        echo "  /status  - Статус и статистика"
        echo "  /health  - Проверка здоровья"
        echo "  /logs    - Последние логи"
        echo "  /restart - Перезапуск бота"
        echo "  /cleanup - Очистка файлов"
        ;;
esac
