#!/bin/bash

# Быстрое развертывание DX Bot на сервере
# Запускать на сервере после подключения

echo "🚀 Быстрое развертывание DX Bot..."

# Проверяем, что мы root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться от root"
    echo "💡 Запустите: sudo $0"
    exit 1
fi

# Устанавливаем Docker если его нет
if ! command -v docker &> /dev/null; then
    echo "🐳 Устанавливаем Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    usermod -aG docker $SUDO_USER
fi

# Устанавливаем Docker Compose если его нет
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Устанавливаем Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Запускаем Docker
systemctl enable docker
systemctl start docker

# Создаем папку и клонируем репозиторий
mkdir -p /opt/dx-bot
cd /opt/dx-bot

if [ ! -d ".git" ]; then
    echo "📥 Клонируем репозиторий..."
    git clone https://github.com/benchikkk/dx-bot-server.git .
else
    echo "✅ Репозиторий уже существует, обновляем..."
    git pull origin main
fi

# Делаем скрипты исполняемыми
chmod +x manage.sh server_setup.sh deploy.sh quick_deploy.sh

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл..."
    cp env.example .env
    echo "⚠️  Отредактируйте файл .env и добавьте ваши BOT_TOKEN и CHAT_ID"
    echo "📝 Затем запустите: nano .env"
    exit 1
fi

# Создаем папки для данных
mkdir -p bot_data/screenshots bot_data/json_history logs

# Устанавливаем права доступа
chown -R $SUDO_USER:$SUDO_USER /opt/dx-bot
chmod -R 755 /opt/dx-bot

echo ""
echo "✅ Быстрое развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте .env файл:"
echo "   nano .env"
echo ""
echo "2. Добавьте ваши токены в .env:"
echo "   BOT_TOKEN=ваш_токен_бота"
echo "   CHAT_ID=ваш_chat_id"
echo ""
echo "3. Запустите бота:"
echo "   cd /opt/dx-bot"
echo "   ./manage.sh start"
echo ""
echo "4. Проверьте статус:"
echo "   ./manage.sh status"
echo ""
echo "💡 Полезные команды:"
echo "   ./manage.sh --help    # Справка по командам"
echo "   ./manage.sh logs      # Логи бота"
echo "   ./manage.sh health    # Проверка здоровья"
