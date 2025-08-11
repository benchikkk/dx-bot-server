#!/bin/bash

# Скрипт для управления DX Bot на сервере

set -e  # Останавливаем выполнение при ошибке

BOT_NAME="dx-bot"
COMPOSE_FILE="docker-compose.yml"
PROJECT_DIR="/opt/dx-bot"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Функция для проверки Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log "${RED}❌ Docker не установлен${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log "${RED}❌ Docker не запущен${NC}"
        exit 1
    fi
}

# Функция для проверки Docker Compose
check_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log "${RED}❌ Docker Compose не установлен${NC}"
        exit 1
    fi
}

# Функция для проверки .env файла
check_env() {
    if [ ! -f .env ]; then
        log "${RED}❌ Файл .env не найден${NC}"
        log "${YELLOW}💡 Создайте .env файл из env.example${NC}"
        exit 1
    fi
    
    # Проверяем обязательные переменные
    if ! grep -q "BOT_TOKEN=" .env || grep -q "your_bot_token_here" .env; then
        log "${RED}❌ BOT_TOKEN не настроен в .env файле${NC}"
        exit 1
    fi
    
    if ! grep -q "CHAT_ID=" .env || grep -q "your_chat_id_here" .env; then
        log "${RED}❌ CHAT_ID не настроен в .env файле${NC}"
        exit 1
    fi
}

# Функция для проверки статуса
check_status() {
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Бот запущен${NC}"
        return 0
    else
        echo -e "${RED}❌ Бот не запущен${NC}"
        return 1
    fi
}

# Основная логика
case "$1" in
    start)
        log "${BLUE}🚀 Запускаем DX Bot...${NC}"
        check_docker
        check_compose
        check_env
        
        # Создаем папки если их нет
        mkdir -p bot_data/screenshots bot_data/json_history logs
        
        # Останавливаем если уже запущен
        if check_status &> /dev/null; then
            log "${YELLOW}⚠️  Бот уже запущен, перезапускаем...${NC}"
            docker-compose down
        fi
        
        # Запускаем
        docker-compose up -d --build
        
        # Ждем немного и проверяем
        sleep 5
        if check_status; then
            log "${GREEN}✅ Бот успешно запущен${NC}"
        else
            log "${RED}❌ Ошибка запуска бота${NC}"
            docker-compose logs --tail=20
            exit 1
        fi
        ;;
        
    stop)
        log "${BLUE}🛑 Останавливаем DX Bot...${NC}"
        check_docker
        check_compose
        
        if docker-compose down; then
            log "${GREEN}✅ Бот остановлен${NC}"
        else
            log "${RED}❌ Ошибка остановки бота${NC}"
            exit 1
        fi
        ;;
        
    restart)
        log "${BLUE}🔄 Перезапускаем DX Bot...${NC}"
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        log "${BLUE}📊 Статус DX Bot:${NC}"
        check_docker
        check_compose
        
        echo ""
        docker-compose ps
        echo ""
        
        if check_status &> /dev/null; then
            # Показываем статистику
            echo -e "${BLUE}📈 Статистика контейнера:${NC}"
            docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
            
            echo ""
            echo -e "${BLUE}💾 Использование диска:${NC}"
            df -h | grep -E "(Filesystem|/dev/)"
        fi
        ;;
        
    logs)
        log "${BLUE}📋 Логи DX Bot:${NC}"
        check_docker
        check_compose
        
        if [ "$2" = "follow" ] || [ "$2" = "-f" ]; then
            docker-compose logs -f --tail=100
        else
            docker-compose logs --tail=100
        fi
        ;;
        
    cleanup)
        log "${BLUE}🧹 Очищаем старые файлы...${NC}"
        
        # Очищаем старые JSON файлы (старше 1 дня)
        if [ -d "bot_data/json_history" ]; then
            find bot_data/json_history -name "*.json" -mtime +1 -delete
            log "${GREEN}✅ Очищены старые JSON файлы${NC}"
        fi
        
        # Очищаем старые скриншоты (старше 1 дня)
        if [ -d "bot_data/screenshots" ]; then
            find bot_data/screenshots -name "*.png" -mtime +1 -delete
            log "${GREEN}✅ Очищены старые скриншоты${NC}"
        fi
        
        # Очищаем Docker
        log "${BLUE}🐳 Очищаем Docker...${NC}"
        docker system prune -f
        
        log "${GREEN}✅ Очистка завершена${NC}"
        ;;
        
    test-cleanup)
        log "${BLUE}🧪 Тестируем настройки очистки...${NC}"
        if [ -f "test_cleanup.py" ]; then
            python3 test_cleanup.py
        else
            log "${YELLOW}⚠️  Файл test_cleanup.py не найден${NC}"
        fi
        ;;
        
    test-channel)
        log "${BLUE}📡 Тестируем отправку в канал...${NC}"
        if [ -f "test_channel.py" ]; then
            python3 test_channel.py
        else
            log "${YELLOW}⚠️  Файл test_channel.py не найден${NC}"
        fi
        ;;
        
    update)
        log "${BLUE}📦 Обновляем бота...${NC}"
        
        # Проверяем git статус
        if [ -d ".git" ]; then
            log "${BLUE}📥 Получаем изменения из репозитория...${NC}"
            git pull origin main
            
            # Останавливаем бота
            $0 stop
            
            # Пересобираем и запускаем
            log "${BLUE}🔨 Пересобираем и запускаем...${NC}"
            docker-compose up -d --build
            
            # Проверяем статус
            sleep 5
            if check_status; then
                log "${GREEN}✅ Бот успешно обновлен и запущен${NC}"
            else
                log "${RED}❌ Ошибка после обновления${NC}"
                exit 1
            fi
        else
            log "${RED}❌ Это не git репозиторий${NC}"
            exit 1
        fi
        ;;
        
    backup)
        log "${BLUE}💾 Создаем резервную копию...${NC}"
        
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        
        # Создаем резервную копию
        tar -czf "$BACKUP_NAME" \
            --exclude='*.log' \
            --exclude='*.tmp' \
            --exclude='venv' \
            --exclude='.git' \
            bot_data/ \
            previous_tokens.json \
            .env \
            config.py \
            bot.py
        
        if [ -f "$BACKUP_NAME" ]; then
            log "${GREEN}✅ Резервная копия создана: $BACKUP_NAME${NC}"
            ls -lh "$BACKUP_NAME"
        else
            log "${RED}❌ Ошибка создания резервной копии${NC}"
            exit 1
        fi
        ;;
        
    health)
        log "${BLUE}🏥 Проверка здоровья бота...${NC}"
        check_docker
        check_compose
        
        # Проверяем статус контейнера
        if check_status &> /dev/null; then
            echo -e "${GREEN}✅ Контейнер работает${NC}"
            
            # Проверяем логи на ошибки
            ERROR_COUNT=$(docker-compose logs --tail=100 | grep -i "error\|exception\|traceback" | wc -l)
            if [ "$ERROR_COUNT" -gt 0 ]; then
                echo -e "${YELLOW}⚠️  Найдено $ERROR_COUNT ошибок в логах${NC}"
            else
                echo -e "${GREEN}✅ Ошибок в логах не найдено${NC}"
            fi
            
            # Проверяем использование ресурсов
            echo -e "${BLUE}💻 Использование ресурсов:${NC}"
            docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        else
            echo -e "${RED}❌ Контейнер не работает${NC}"
            exit 1
        fi
        ;;
        
    --help|-h|help)
        echo -e "${BLUE}🤖 DX Bot Manager${NC}"
        echo ""
        echo -e "Использование: ${GREEN}$0 {команда}${NC}"
        echo ""
        echo -e "${YELLOW}Основные команды:${NC}"
        echo -e "  ${GREEN}start${NC}     - Запустить бота"
        echo -e "  ${GREEN}stop${NC}      - Остановить бота"
        echo -e "  ${GREEN}restart${NC}   - Перезапустить бота"
        echo -e "  ${GREEN}status${NC}    - Показать статус"
        echo -e "  ${GREEN}logs${NC}      - Показать логи"
        echo -e "  ${GREEN}health${NC}    - Проверка здоровья"
        echo ""
        echo -e "${YELLOW}Обслуживание:${NC}"
        echo -e "  ${GREEN}cleanup${NC}   - Очистить старые файлы"
        echo -e "  ${GREEN}update${NC}    - Обновить бота"
        echo -e "  ${GREEN}backup${NC}    - Создать резервную копию"
        echo ""
        echo -e "${YELLOW}Тестирование:${NC}"
        echo -e "  ${GREEN}test-cleanup${NC}  - Тестировать настройки очистки"
        echo -e "  ${GREEN}test-channel${NC}  - Тестировать отправку в канал"
        echo ""
        echo -e "${YELLOW}Telegram команды:${NC}"
        echo -e "  ${GREEN}/start${NC}    - Информация о боте"
        echo -e "  ${GREEN}/status${NC}   - Статус и статистика"
        echo -e "  ${GREEN}/health${NC}   - Проверка здоровья"
        echo -e "  ${GREEN}/logs${NC}     - Последние логи"
        echo -e "  ${GREEN}/restart${NC}  - Перезапуск бота"
        echo -e "  ${GREEN}/cleanup${NC}  - Очистка файлов"
        echo ""
        echo -e "${YELLOW}Примеры:${NC}"
        echo -e "  ${GREEN}$0 start${NC}      # Запустить бота"
        echo -e "  ${GREEN}$0 logs -f${NC}    # Логи в реальном времени"
        echo -e "  ${GREEN}$0 health${NC}     # Проверка здоровья"
        ;;
        
    *)
        echo -e "${RED}❌ Неизвестная команда: $1${NC}"
        echo ""
        echo -e "Используйте: ${GREEN}$0 --help${NC} для справки"
        exit 1
        ;;
esac
