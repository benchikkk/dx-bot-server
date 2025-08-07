import os
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Telegram Bot настройки
BOT_TOKEN = os.getenv("BOT_TOKEN", "8440826252:AAEZbVkLMUmsDfJzcbTvyzl2agZYgKVbYXM")
CHAT_ID = os.getenv("CHAT_ID", "5188883528")

# WebDriver настройки
HEADLESS_MODE = os.getenv("HEADLESS", "false").lower() == "true"
DRIVER_TIMEOUT = 30
PAGE_LOAD_WAIT = 5
CHROME_VERSION = 138  # Версия Chrome для undetected-chromedriver

# Dexscreener настройки
DEXSCREENER_URL = "https://dexscreener.com/?rankBy=trendingScoreH1&order=desc&minMarketCap=150000&maxMarketCap=15000000&min24HVol=75000"

# Фильтры токенов
MIN_MARKET_CAP = 150_000
MAX_MARKET_CAP = 15_000_000
MIN_24H_VOLUME = 75_000

# Интервалы проверок (в секундах)
CHECK_INTERVAL = 600  # 10 минут
CLEANUP_INTERVAL = 6000  # 100 минут

# Файлы и папки
STATE_FILE = "previous_tokens.json"
DATA_FOLDER = "bot_data"
SCREENSHOTS_FOLDER = "bot_data/screenshots"
JSON_HISTORY_FOLDER = "bot_data/json_history"

# Очистка файлов
FILE_RETENTION_MINUTES = 100

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = "bot.log"

# Глобальные переменные для статистики
BOT_RUNNING = True
BOT_START_TIME = None
STATS = {
    'checks_performed': 0,
    'new_tokens_found': 0,
    'messages_sent': 0,
    'errors_count': 0
} 