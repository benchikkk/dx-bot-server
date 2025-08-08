# 🤖 DX Bot - Telegram бот для мониторинга трендовых токенов

Автоматический бот для мониторинга трендовых токенов на Dexscreener с отправкой уведомлений в Telegram канал.

## ✨ Возможности

- 🔍 **Мониторинг токенов** каждые 10 минут
- 📱 **Уведомления в Telegram** о новых токенах
- 🧹 **Автоматическая очистка** старых файлов
- 📊 **Статистика и управление** через Telegram команды
- 🐳 **Docker поддержка** для серверного развертывания
- 🔒 **Безопасность** - токены в переменных окружения

## 🚀 Быстрый запуск

### 1. Клонирование и установка
```bash
git clone https://github.com/benchikkk/dx-bot.git
cd dx-bot
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
```bash
cp env.example .env
nano .env
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

### 3. Запуск
```bash
# Локальный запуск
python3 bot.py

# Docker запуск
docker-compose up -d

# Управление через скрипт
./manage.sh start
```

## 📱 Настройка Telegram канала

### Создание канала
1. Создайте новый канал в Telegram
2. Добавьте бота в канал как **администратора**
3. Скопируйте ID канала (начинается с `-100`)

### Права бота в канале
Бот должен иметь права:
- ✅ Отправка сообщений
- ✅ Редактирование сообщений
- ✅ Закрепление сообщений (опционально)

### Настройка .env файла
```bash
# Для канала
CHAT_ID=-1002549644699

# Для личных сообщений
CHAT_ID=123456789
```

## 🎮 Команды управления

### Telegram команды
- `/start` - Информация о боте
- `/status` - Статус бота и системы
- `/health` - Проверка здоровья
- `/stats` - Подробная статистика
- `/logs` - Последние логи
- `/show10` - Топ-10 токенов
- `/restart` - Перезапуск бота
- `/cleanup` - Принудительная очистка файлов

### Серверные команды
```bash
# Управление через скрипт
./manage.sh start    # Запуск
./manage.sh stop     # Остановка
./manage.sh restart  # Перезапуск
./manage.sh status   # Статус
./manage.sh logs     # Логи
./manage.sh cleanup  # Очистка

# Docker команды
docker-compose up -d
docker-compose down
docker-compose logs -f
```

## ⚙️ Настройки для сервера

### Оптимизация места на диске
```bash
# Отключить скриншоты (экономия ~400-700KB на файл)
SAVE_SCREENSHOTS=false

# Настройки очистки (в config.py)
CLEANUP_INTERVAL = 900  # 15 минут
FILE_RETENTION_MINUTES = 15  # JSON файлы
SCREENSHOT_RETENTION_MINUTES = 10  # Скриншоты
```

### Автоматический перезапуск
```bash
# Создание systemd сервиса
sudo cp dx-bot.service /etc/systemd/system/
sudo systemctl enable dx-bot.service
sudo systemctl start dx-bot.service
```

## 🔒 Безопасность

### Важные правила
- **НИКОГДА** не коммитьте файл `.env` в Git
- **НИКОГДА** не добавляйте токены в код
- Используйте только переменные окружения

### Файлы для исключения из Git
Следующие файлы НЕ должны попадать в репозиторий:
- `.env` - файл с переменными окружения
- `bot.log` - логи работы бота
- `previous_tokens.json` - данные о токенах
- `bot_data/` - папка с данными бота

### Проверка безопасности
```bash
# Проверить, что .env не в Git
git status

# Проверить, что токены не в коде
grep -r "BOT_TOKEN" . --exclude-dir=.git
```

## 🐳 Развертывание на сервере

### Автоматическая настройка
```bash
# Скачиваем и запускаем скрипт настройки
wget https://raw.githubusercontent.com/benchikkk/dx-bot/main/server_setup.sh
chmod +x server_setup.sh
./server_setup.sh
```

### Ручная настройка
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Клонирование проекта
git clone https://github.com/benchikkk/dx-bot.git /opt/dx-bot
cd /opt/dx-bot

# Настройка .env
cp env.example .env
nano .env

# Запуск
docker-compose up -d
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
```

### Автоматический мониторинг
Бот автоматически:
- Очищает старые файлы каждые 15 минут
- Показывает статистику использования ресурсов
- Отправляет уведомления о проблемах

## 🚨 Устранение проблем

### Бот не запускается
```bash
# Проверяем логи
./manage.sh logs

# Проверяем .env файл
cat .env

# Проверяем права бота в канале
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

## 📁 Структура проекта

```
dx-bot/
├── bot.py                 # Основной файл бота
├── config.py              # Конфигурация
├── manage.sh              # Скрипт управления
├── docker-compose.yml     # Docker конфигурация
├── Dockerfile             # Docker образ
├── requirements.txt       # Python зависимости
├── env.example           # Пример .env файла
├── DEPLOYMENT_GUIDE.md   # Руководство по развертыванию
├── server_setup.sh       # Автоматическая настройка сервера
└── bot_data/             # Данные бота (не в Git)
    ├── json_history/      # JSON файлы с историей
    └── screenshots/       # Скриншоты (если включены)
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 🎉 Готово!

После настройки ваш бот будет:
- ✅ Работать 24/7 на сервере
- ✅ Автоматически перезапускаться при сбоях
- ✅ Отправлять уведомления в Telegram
- ✅ Очищать старые файлы
- ✅ Показывать статистику и статус

**Следующий шаг:** Настройте переменные окружения и запустите бота!
