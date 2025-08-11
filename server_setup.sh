#!/bin/bash

# Автоматическая настройка сервера для DX Bot
# Запускать на сервере после подключения

set -e  # Останавливаем выполнение при ошибке

echo "🚀 Начинаем настройку сервера для DX Bot..."
echo "📅 Дата: $(date)"
echo "🖥️  ОС: $(lsb_release -d | cut -f2)"
echo ""

# Проверяем, что мы root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться от root"
    echo "💡 Запустите: sudo $0"
    exit 1
fi

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Функция для проверки команд
check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Обновляем систему
log "📦 Обновляем систему..."
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
log "🔧 Устанавливаем необходимые пакеты..."
apt install -y curl wget git nano htop unzip software-properties-common \
    apt-transport-https ca-certificates gnupg lsb-release \
    python3 python3-pip python3-venv

# Проверяем и устанавливаем Docker
if ! check_command docker; then
    log "🐳 Устанавливаем Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Добавляем пользователя в группу docker
    if [ ! -z "$SUDO_USER" ]; then
        usermod -aG docker $SUDO_USER
        log "✅ Пользователь $SUDO_USER добавлен в группу docker"
    fi
else
    log "✅ Docker уже установлен: $(docker --version)"
fi

# Проверяем и устанавливаем Docker Compose
if ! check_command docker-compose; then
    log "📦 Устанавливаем Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Создаем символическую ссылку для совместимости
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
else
    log "✅ Docker Compose уже установлен: $(docker-compose --version)"
fi

# Запускаем Docker сервис
log "🔄 Запускаем Docker сервис..."
systemctl enable docker
systemctl start docker

# Создаем папку для проекта
log "📁 Создаем папку для проекта..."
mkdir -p /opt/dx-bot
cd /opt/dx-bot

# Клонируем репозиторий
if [ ! -d ".git" ]; then
    log "📥 Клонируем репозиторий..."
    git clone https://github.com/benchikkk/dx-bot-server.git .
else
    log "✅ Репозиторий уже существует, обновляем..."
    git pull origin main
fi

# Делаем скрипты исполняемыми
log "🔧 Настраиваем скрипты..."
chmod +x manage.sh server_setup.sh deploy.sh

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    log "📝 Создаем .env файл..."
    cp env.example .env
    log "⚠️  Отредактируйте файл .env и добавьте ваши BOT_TOKEN и CHAT_ID"
else
    log "✅ .env файл уже существует"
fi

# Создаем папки для данных
log "📁 Создаем папки для данных..."
mkdir -p bot_data/screenshots bot_data/json_history logs

# Устанавливаем права доступа
log "🔐 Настраиваем права доступа..."
chown -R $SUDO_USER:$SUDO_USER /opt/dx-bot
chmod -R 755 /opt/dx-bot

# Настраиваем firewall
log "🔥 Настраиваем firewall..."
if check_command ufw; then
    ufw --force enable
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    log "✅ Firewall настроен"
else
    log "⚠️  UFW не найден, пропускаем настройку firewall"
fi

# Создаем systemd сервис
log "⚙️  Создаем systemd сервис..."
cat > /etc/systemd/system/dx-bot.service << EOF
[Unit]
Description=DX Bot Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/dx-bot
ExecStart=/opt/dx-bot/manage.sh start
ExecStop=/opt/dx-bot/manage.sh stop
User=$SUDO_USER
Group=$SUDO_USER

[Install]
WantedBy=multi-user.target
EOF

# Включаем автозапуск сервиса
systemctl daemon-reload
systemctl enable dx-bot.service

# Проверяем Docker
log "🔍 Проверяем Docker..."
if docker info > /dev/null 2>&1; then
    log "✅ Docker работает корректно"
else
    log "❌ Проблема с Docker"
    exit 1
fi

# Проверяем Docker Compose
log "🔍 Проверяем Docker Compose..."
if docker-compose --version > /dev/null 2>&1; then
    log "✅ Docker Compose работает корректно"
else
    log "❌ Проблема с Docker Compose"
    exit 1
fi

echo ""
echo "🎉 Настройка сервера завершена!"
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
echo "- Firewall включен и настроен"
echo "- SSH доступ разрешен"
echo "- Создан systemd сервис для автозапуска"
echo ""
echo "📊 Мониторинг:"
echo "- htop - мониторинг ресурсов"
echo "- df -h - место на диске"
echo "- docker stats - статистика контейнеров"
echo "- systemctl status dx-bot - статус сервиса"
echo ""
echo "🔄 Автозапуск:"
echo "- Сервис настроен на автозапуск при перезагрузке"
echo "- Управление: systemctl start/stop/restart dx-bot"
echo ""
echo "💡 Полезные команды:"
echo "- cd /opt/dx-bot && ./manage.sh --help"
echo "- docker-compose logs -f"
echo "- docker system prune -a (очистка Docker)"
