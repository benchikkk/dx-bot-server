#!/bin/bash

# Автоматическая настройка сервера для DX Bot
# Запускать на сервере после подключения

echo "🚀 Начинаем настройку сервера для DX Bot..."

# Проверяем, что мы root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться от root"
    exit 1
fi

# Обновляем систему
echo "📦 Обновляем систему..."
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем необходимые пакеты..."
apt install -y curl wget git nano htop unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Устанавливаем Docker
echo "🐳 Устанавливаем Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Добавляем пользователя в группу docker
usermod -aG docker $SUDO_USER

# Устанавливаем Docker Compose
echo "📦 Устанавливаем Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Создаем папку для проекта
echo "📁 Создаем папку для проекта..."
mkdir -p /opt/dx-bot
cd /opt/dx-bot

# Клонируем репозиторий
echo "📥 Клонируем репозиторий..."
git clone https://github.com/benchikkk/dx-bot.git .

# Создаем .env файл
echo "📝 Создаем .env файл..."
cp env.example .env

echo ""
echo "✅ Настройка сервера завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте .env файл:"
echo "   nano /opt/dx-bot/.env"
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
echo "5. Посмотрите логи:"
echo "   ./manage.sh logs"
echo ""
echo "🔒 Безопасность:"
echo "- Настройте firewall: ufw enable"
echo "- Измените SSH порт: nano /etc/ssh/sshd_config"
echo "- Создайте пользователя: adduser youruser"
echo ""
echo "📊 Мониторинг:"
echo "- htop - мониторинг ресурсов"
echo "- df -h - место на диске"
echo "- docker stats - статистика контейнеров"
