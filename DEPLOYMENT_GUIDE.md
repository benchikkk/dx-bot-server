# 🚀 Руководство по развертыванию DX Bot на сервере

## 📋 Подготовка

### 1. Выбор провайдера
**Рекомендуемые провайдеры:**
- **Kontabo** - хорошее соотношение цена/качество
- **DigitalOcean** - надежно, но дороже
- **Linode** - стабильно, средние цены
- **Vultr** - быстрые серверы

### 2. Конфигурация сервера
**Минимальные требования:**
- CPU: 1 ядро
- RAM: 2GB (рекомендуется 4GB)
- SSD: 20GB
- ОС: Ubuntu 22.04 LTS

**Рекомендуемые требования:**
- CPU: 2 ядра
- RAM: 4GB
- SSD: 40GB
- ОС: Ubuntu 22.04 LTS

## 🔧 Пошаговая настройка

### Шаг 1: Аренда сервера

1. Зарегистрируйтесь на сайте провайдера
2. Выберите конфигурацию сервера
3. Выберите Ubuntu 22.04 LTS
4. Выберите ближайший дата-центр
5. Создайте сервер

### Шаг 2: Подключение к серверу

После создания сервера получите:
- IP адрес сервера
- Логин (обычно `root`)
- Пароль или SSH ключ

Подключитесь:
```bash
ssh root@IP_АДРЕС_СЕРВЕРА
```

### Шаг 3: Автоматическая настройка

Скачайте и запустите скрипт настройки:
```bash
# Скачиваем скрипт
wget https://raw.githubusercontent.com/benchikkk/dx-bot/main/server_setup.sh

# Делаем исполняемым
chmod +x server_setup.sh

# Запускаем
./server_setup.sh
```

### Шаг 4: Настройка переменных окружения

Отредактируйте файл `.env`:
```bash
nano /opt/dx-bot/.env
```

Добавьте ваши данные:
```bash
# Telegram Bot настройки
BOT_TOKEN=ваш_токен_бота
CHAT_ID=ваш_chat_id

# Настройки для сервера
SAVE_SCREENSHOTS=false
LOG_LEVEL=INFO
HEADLESS=true
```

### Шаг 5: Запуск бота

```bash
cd /opt/dx-bot

# Запуск
./manage.sh start

# Проверка статуса
./manage.sh status

# Просмотр логов
./manage.sh logs
```

## 🔒 Безопасность сервера

### Настройка firewall
```bash
# Включаем firewall
ufw enable

# Разрешаем SSH
ufw allow ssh

# Разрешаем HTTP/HTTPS (если нужно)
ufw allow 80
ufw allow 443

# Проверяем статус
ufw status
```

### Изменение SSH порта
```bash
# Редактируем конфигурацию SSH
nano /etc/ssh/sshd_config

# Меняем порт (например, на 2222)
Port 2222

# Перезапускаем SSH
systemctl restart sshd
```

### Создание пользователя
```bash
# Создаем пользователя
adduser yourusername

# Добавляем в sudo
usermod -aG sudo yourusername

# Переключаемся на пользователя
su - yourusername
```

## 📊 Мониторинг

### Команды для мониторинга
```bash
# Мониторинг ресурсов
htop

# Место на диске
df -h

# Статистика Docker
docker stats

# Логи бота
./manage.sh logs

# Статус бота
./manage.sh status
```

### Автоматический перезапуск
```bash
# Создаем systemd сервис
sudo cp dx-bot.service /etc/systemd/system/

# Включаем автозапуск
sudo systemctl enable dx-bot.service

# Запускаем сервис
sudo systemctl start dx-bot.service

# Проверяем статус
sudo systemctl status dx-bot.service
```

## 🔧 Управление ботом

### Telegram команды
- `/start` - Информация о боте
- `/status` - Статус и статистика
- `/health` - Проверка здоровья
- `/stats` - Подробная статистика
- `/logs` - Последние логи
- `/restart` - Перезапуск бота
- `/cleanup` - Очистка файлов

### Серверные команды
```bash
# Запуск/остановка
./manage.sh start
./manage.sh stop
./manage.sh restart

# Мониторинг
./manage.sh status
./manage.sh logs

# Обслуживание
./manage.sh cleanup
./manage.sh backup
./manage.sh update
```

## 🚨 Устранение проблем

### Бот не запускается
```bash
# Проверяем логи
./manage.sh logs

# Проверяем .env файл
cat .env

# Тестируем канал
python3 test_channel.py
```

### Нехватка места на диске
```bash
# Очищаем старые файлы
./manage.sh cleanup

# Проверяем место
df -h

# Очищаем Docker
docker system prune -a
```

### Проблемы с Docker
```bash
# Перезапускаем Docker
systemctl restart docker

# Пересобираем контейнер
docker-compose down
docker-compose up -d --build
```

## 📈 Оптимизация

### Отключение скриншотов
В файле `.env`:
```bash
SAVE_SCREENSHOTS=false
```

### Настройка очистки
В `config.py` можно изменить интервалы:
```python
CLEANUP_INTERVAL = 900  # 15 минут
FILE_RETENTION_MINUTES = 15  # JSON файлы
SCREENSHOT_RETENTION_MINUTES = 10  # Скриншоты
```

### Мониторинг ресурсов
```bash
# Установка мониторинга
apt install -y htop iotop

# Мониторинг в реальном времени
htop
iotop
```

## 🎉 Готово!

После выполнения всех шагов ваш бот будет:
- ✅ Работать 24/7 на сервере
- ✅ Автоматически перезапускаться при сбоях
- ✅ Отправлять уведомления в Telegram
- ✅ Очищать старые файлы
- ✅ Показывать статистику и статус

**Следующий шаг:** Арендуйте сервер и начните с Шага 1!
