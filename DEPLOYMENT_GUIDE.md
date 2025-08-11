# 🚀 Руководство по развертыванию DX Bot на сервере

## 📋 Предварительные требования

- Сервер Ubuntu/Debian (рекомендуется Ubuntu 20.04+)
- Минимум 2GB RAM
- Минимум 20GB свободного места
- Доступ по SSH

## 🔧 Быстрое развертывание

### Шаг 1: Подключение к серверу
```bash
ssh username@your_server_ip
```

### Шаг 2: Запуск автоматической настройки
```bash
# Скачиваем скрипт настройки
curl -fsSL https://raw.githubusercontent.com/benchikkk/dx-bot-server/main/server_setup.sh -o server_setup.sh

# Делаем исполняемым
chmod +x server_setup.sh

# Запускаем от root
sudo ./server_setup.sh
```

### Шаг 3: Настройка переменных окружения
```bash
cd /opt/dx-bot
nano .env
```

Замените в файле:
```env
BOT_TOKEN=ваш_реальный_токен_бота
CHAT_ID=ваш_chat_id
LOG_LEVEL=INFO
HEADLESS=true
SAVE_SCREENSHOTS=false
```

### Шаг 4: Запуск бота
```bash
cd /opt/dx-bot
./manage.sh start
```

### Шаг 5: Проверка работы
```bash
# Статус
./manage.sh status

# Логи
./manage.sh logs

# Остановка
./manage.sh stop

# Перезапуск
./manage.sh restart
```

## 🐳 Ручное развертывание через Docker

### Установка Docker
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагружаемся или перезапускаем сессию
newgrp docker
```

### Клонирование и настройка
```bash
# Клонируем репозиторий
git clone https://github.com/benchikkk/dx-bot-server.git
cd dx-bot-server

# Создаем .env файл
cp env.example .env
nano .env

# Создаем папки для данных
mkdir -p bot_data/screenshots bot_data/json_history logs
```

### Запуск через Docker Compose
```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Логи
docker-compose logs -f
```

## 📊 Управление ботом

### Основные команды
```bash
./manage.sh start      # Запуск
./manage.sh stop       # Остановка
./manage.sh restart    # Перезапуск
./manage.sh status     # Статус
./manage.sh logs       # Логи
./manage.sh update     # Обновление
./manage.sh backup     # Резервная копия
```

### Telegram команды
- `/start` - Информация о боте
- `/status` - Статус и статистика
- `/health` - Проверка здоровья
- `/logs` - Последние логи
- `/restart` - Перезапуск бота
- `/cleanup` - Очистка файлов

## 🔒 Безопасность

### Firewall
```bash
# Включаем UFW
sudo ufw enable

# Разрешаем SSH
sudo ufw allow ssh

# Разрешаем HTTP/HTTPS если нужно
sudo ufw allow 80
sudo ufw allow 443
```

### SSH безопасность
```bash
# Меняем порт SSH
sudo nano /etc/ssh/sshd_config
# Port 2222

# Перезапускаем SSH
sudo systemctl restart sshd
```

## 📈 Мониторинг

### Системные ресурсы
```bash
htop                    # Мониторинг ресурсов
df -h                   # Место на диске
free -h                 # Память
docker stats            # Статистика контейнеров
```

### Логи и отладка
```bash
# Логи Docker
docker-compose logs -f

# Логи системы
sudo journalctl -u docker.service -f

# Проверка процессов
ps aux | grep python
```

## 🚨 Устранение неполадок

### Проблемы с Docker
```bash
# Перезапуск Docker
sudo systemctl restart docker

# Очистка Docker
docker system prune -a

# Проверка статуса
sudo systemctl status docker
```

### Проблемы с ботом
```bash
# Проверка логов
./manage.sh logs

# Перезапуск
./manage.sh restart

# Проверка конфигурации
docker-compose config
```

### Проблемы с Chrome/WebDriver
```bash
# Проверка версии Chrome
google-chrome --version

# Обновление Chrome
sudo apt update && sudo apt install google-chrome-stable
```

## 🔄 Обновление

### Автоматическое обновление
```bash
./manage.sh update
```

### Ручное обновление
```bash
# Получаем изменения
git pull origin main

# Пересобираем и перезапускаем
docker-compose down
docker-compose up -d --build
```

## 💾 Резервное копирование

### Создание резервной копии
```bash
./manage.sh backup
```

### Восстановление
```bash
# Останавливаем бота
./manage.sh stop

# Распаковываем резервную копию
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz

# Запускаем
./manage.sh start
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `./manage.sh logs`
2. Проверьте статус: `./manage.sh status`
3. Проверьте конфигурацию: `docker-compose config`
4. Создайте issue в репозитории

## 🔗 Полезные ссылки

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
