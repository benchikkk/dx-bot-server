# 🚀 Быстрое развертывание DX Bot на сервере

## 📋 Что нужно сделать

1. **Подключиться к серверу** по SSH
2. **Запустить скрипт развертывания**
3. **Настроить .env файл** с твоими токенами
4. **Запустить бота**

## 🔧 Пошаговая инструкция

### Шаг 1: Подключение к серверу
```bash
ssh root@IP_АДРЕС_ТВОЕГО_СЕРВЕРА
```

### Шаг 2: Быстрое развертывание
```bash
# Скачиваем и запускаем скрипт
curl -fsSL https://raw.githubusercontent.com/benchikkk/dx-bot-server/main/quick_deploy.sh -o quick_deploy.sh
chmod +x quick_deploy.sh
sudo ./quick_deploy.sh
```

### Шаг 3: Настройка токенов
```bash
cd /opt/dx-bot
nano .env
```

**Замени в файле:**
```env
BOT_TOKEN=твой_реальный_токен_бота
CHAT_ID=твой_chat_id
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

# Проверка здоровья
./manage.sh health
```

## 🎯 Готово!

Твой бот теперь работает на сервере и будет:
- ✅ Автоматически запускаться при перезагрузке
- ✅ Работать 24/7
- ✅ Отправлять уведомления в Telegram
- ✅ Очищать старые файлы

## 📱 Telegram команды

- `/start` - Информация о боте
- `/status` - Статус и статистика
- `/health` - Проверка здоровья
- `/logs` - Последние логи
- `/restart` - Перезапуск бота
- `/cleanup` - Очистка файлов

## 🛠️ Управление ботом

```bash
cd /opt/dx-bot

./manage.sh start      # Запустить
./manage.sh stop       # Остановить
./manage.sh restart    # Перезапустить
./manage.sh status     # Статус
./manage.sh logs       # Логи
./manage.sh health     # Проверка здоровья
./manage.sh update     # Обновить
./manage.sh backup     # Резервная копия
```

## 🚨 Если что-то пошло не так

1. **Проверь логи:** `./manage.sh logs`
2. **Проверь статус:** `./manage.sh status`
3. **Проверь здоровье:** `./manage.sh health`
4. **Перезапусти:** `./manage.sh restart`

## 💡 Полезные команды

```bash
# Мониторинг ресурсов
htop

# Место на диске
df -h

# Статистика Docker
docker stats

# Статус сервиса
systemctl status dx-bot
```

## 🔒 Безопасность

- Firewall автоматически настроен
- SSH доступ разрешен
- Бот работает в изолированном контейнере

---

**🎉 Поздравляю! Твой бот теперь работает на сервере!**
