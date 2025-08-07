#!/bin/bash

# Скрипт для развертывания DX Bot на сервере

echo "🚀 Начинаем развертывание DX Bot..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Перезагрузите систему и запустите скрипт снова."
    exit 1
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем файл .env..."
    cp env.example .env
    echo "⚠️  Отредактируйте файл .env и добавьте ваши BOT_TOKEN и CHAT_ID"
    echo "📝 Затем запустите: nano .env"
    exit 1
fi

# Создаем папки для данных
mkdir -p bot_data/screenshots bot_data/json_history logs

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose down

# Собираем и запускаем
echo "🔨 Собираем и запускаем контейнер..."
docker-compose up -d --build

# Проверяем статус
echo "📊 Проверяем статус..."
docker-compose ps

echo "✅ Развертывание завершено!"
echo "📋 Логи: docker-compose logs -f"
echo "🛑 Остановка: docker-compose down"
echo "🔄 Перезапуск: docker-compose restart"
