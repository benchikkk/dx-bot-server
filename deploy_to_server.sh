#!/bin/bash

# Скрипт для автоматического развертывания DX Bot на сервере
# Запускать на сервере от имени root

echo "🚀 Начинаем развертывание DX Bot на сервере..."

# Обновляем систему
echo "📦 Обновляем систему..."
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем необходимые пакеты..."
apt install -y curl wget git nano htop docker.io docker-compose

# Запускаем Docker
echo "🐳 Настраиваем Docker..."
systemctl start docker
systemctl enable docker

# Создаем пользователя для бота
echo "👤 Создаем пользователя dxbot..."
useradd -m -s /bin/bash dxbot
usermod -aG docker dxbot

# Создаем директорию для бота
echo "📁 Создаем директорию для бота..."
mkdir -p /opt/dx-bot
chown dxbot:dxbot /opt/dx-bot

# Переключаемся на пользователя dxbot
echo "🔄 Переключаемся на пользователя dxbot..."
su - dxbot << 'EOF'

# Клонируем репозиторий
echo "📥 Клонируем репозиторий..."
cd /opt
git clone https://github.com/benchikkk/dx-bot-server.git dx-bot
cd dx-bot

# Создаем .env файл
echo "📝 Создаем .env файл..."
cp env.example .env

# Создаем папки для данных
echo "📁 Создаем папки для данных..."
mkdir -p bot_data/screenshots bot_data/json_history logs

# Устанавливаем права
chmod +x manage.sh deploy.sh

echo "✅ Базовая настройка завершена!"
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env: nano /opt/dx-bot/.env"
echo "2. Добавьте BOT_TOKEN и CHAT_ID"
echo "3. Запустите бота: ./manage.sh start"

EOF

# Настраиваем systemd сервис
echo "🔧 Настраиваем автозапуск..."
cp /opt/dx-bot/dx-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable dx-bot.service

# Настраиваем firewall
echo "🔥 Настраиваем firewall..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

echo "✅ Развертывание завершено!"
echo "📋 Для запуска бота выполните:"
echo "cd /opt/dx-bot"
echo "nano .env  # Добавьте токен и chat_id"
echo "./manage.sh start"
