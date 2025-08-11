import requests
from bs4 import BeautifulSoup
import json
import time
import os
import shutil
from datetime import datetime
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import re
import glob
from datetime import datetime, timedelta
import psutil
import platform
import signal
import sys
from config import *

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Глобальная переменная для контроля работы бота
bot_running = True
bot_start_time = datetime.now()
stats = {
    'checks_performed': 0,
    'new_tokens_found': 0,
    'messages_sent': 0,
    'errors_count': 0
}

# URL страницы с трендовыми токенами на Dexscreener
# Trending 1h с фильтрами: минимальный маркет кап $150K, максимальный $15M, минимальный объём $75K
DEXSCREENER_URL = "https://dexscreener.com/?rankBy=trendingScoreH1&order=desc&minMarketCap=150000&maxMarketCap=15000000&min24HVol=75000"

# Файл для хранения предыдущего состояния списка токенов
STATE_FILE = "previous_tokens.json"

# Папка для хранения скриншотов и данных
DATA_FOLDER = "bot_data"
SCREENSHOTS_FOLDER = "bot_data/screenshots"
JSON_HISTORY_FOLDER = "bot_data/json_history"

class DexscreenerBot:
    def __init__(self):
        # Валидация конфигурации
        self._validate_config()
        
        # Создаём экземпляр бота
        self.bot = Bot(token=BOT_TOKEN)
        self.previous_tokens = self.load_previous_tokens()
        self.driver = None
        
        # Создаём папки для хранения данных
        self.setup_folders()
    
    def _validate_config(self):
        """Валидация конфигурации при запуске"""
        if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
            raise ValueError("BOT_TOKEN не настроен. Установите переменную окружения BOT_TOKEN")
        
        if not CHAT_ID or CHAT_ID == "your_chat_id_here":
            raise ValueError("CHAT_ID не настроен. Установите переменную окружения CHAT_ID")
        
        try:
            int(CHAT_ID)
        except ValueError:
            raise ValueError("CHAT_ID должен быть числом")
        
        logger.info("Конфигурация валидна")
    
    def setup_folders(self):
        """Создаём папки для хранения скриншотов и JSON данных"""
        folders = [DATA_FOLDER, SCREENSHOTS_FOLDER, JSON_HISTORY_FOLDER]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                logger.info(f"Создана папка: {folder}")
        
    def setup_driver(self):
        """Настраиваем Selenium WebDriver для парсинга JavaScript сайта"""
        try:
            # Используем undetected-chromedriver для обхода защиты
            options = uc.ChromeOptions()
            
            # Основные настройки
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Ускоряет загрузку
            
            # Используем headless режим из конфигурации
            if HEADLESS_MODE:
                options.add_argument("--headless")
            
            # Создаём драйвер с правильной версией Chrome
            self.driver = uc.Chrome(options=options, version_main=138)
            logger.info("WebDriver успешно настроен с undetected-chromedriver")
            
        except Exception as e:
            logger.error(f"Ошибка при настройке WebDriver: {e}")
            logger.error("Попробуйте установить: pip install undetected-chromedriver")
            # Пробуем альтернативный способ
            try:
                logger.info("Пробуем альтернативный способ запуска драйвера...")
                # Удаляем старые файлы драйвера
                uc_path = os.path.expanduser("~/Library/Application Support/undetected_chromedriver")
                if os.path.exists(uc_path):
                    shutil.rmtree(uc_path)
                    logger.info("Удалены старые файлы драйвера")
                
                # Пробуем снова с правильной версией
                self.driver = uc.Chrome(options=options, version_main=138)
                logger.info("WebDriver запущен с версией 138")
            except Exception as e2:
                logger.error(f"Альтернативный способ тоже не сработал: {e2}")
                self.driver = None
    
    def load_previous_tokens(self):
        """Загружаем список токенов с прошлой проверки из файла"""
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Если файла нет, возвращаем пустой словарь
            return {}
    
    def save_current_tokens(self, tokens):
        """Сохраняем текущий список токенов в файл"""
        # Сохраняем в основной файл
        with open(STATE_FILE, 'w') as f:
            json.dump(tokens, f)
        
        # Также сохраняем историю с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = os.path.join(JSON_HISTORY_FOLDER, f"tokens_{timestamp}.json")
        with open(history_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'tokens_count': len(tokens),
                'tokens': tokens
            }, f, indent=2)
        logger.info(f"Сохранена история токенов: {history_file}")
    
    def fetch_trending_tokens(self):
        """Получаем список трендовых токенов с Dexscreener через web scraping"""
        if not self.driver:
            self.setup_driver()
            if not self.driver:
                logger.error("Не удалось инициализировать WebDriver")
                return {}
        
        try:
            logger.info("Загружаем страницу Dexscreener (Trending 1h с фильтрами)...")
            self.driver.get(DEXSCREENER_URL)
            
            # Ждём загрузки страницы и появления токенов
            wait = WebDriverWait(self.driver, 30)
            
            # Ждём немного для загрузки JavaScript
            time.sleep(5)
            
            # Проверяем, есть ли Cloudflare challenge
            try:
                # Ждём появления Cloudflare
                time.sleep(5)
                
                # Ищем iframe Cloudflare с расширенными селекторами
                cf_iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="cloudflare"], iframe[src*="turnstile"], iframe[src*="challenges"], iframe[src*="captcha"]')
                logger.info(f"Найдено {len(cf_iframes)} Cloudflare iframe")
                
                if cf_iframes:
                    logger.info("Обрабатываем Cloudflare iframe...")
                    
                    # Переключаемся на первый iframe
                    self.driver.switch_to.frame(cf_iframes[0])
                    
                    # Ждём загрузки iframe
                    time.sleep(3)
                    
                    # Ищем чекбокс внутри iframe
                    try:
                        checkbox = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"]'))
                        )
                        logger.info("Найдён чекбокс Cloudflare в iframe")
                        checkbox.click()
                        logger.info("Кликнули на чекбокс")
                        
                        # Возвращаемся к основному контенту
                        self.driver.switch_to.default_content()
                        time.sleep(5)  # Ждём проверку
                        logger.info("Cloudflare проверка завершена")
                        
                    except Exception as e:
                        logger.info(f"Не удалось найти чекбокс в iframe: {e}")
                        self.driver.switch_to.default_content()
                else:
                    # Пробуем найти чекбокс в основном контенте
                    logger.info("Ищем Cloudflare в основном контенте...")
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
                    logger.info(f"Найдено {len(checkboxes)} чекбоксов в основном контенте")
                    
                    cf_found = False
                    for i, checkbox in enumerate(checkboxes):
                        try:
                            name = checkbox.get_attribute('name')
                            class_name = checkbox.get_attribute('class')
                            id_name = checkbox.get_attribute('id')
                            
                            logger.info(f"Чекбокс {i+1}: name='{name}', class='{class_name}', id='{id_name}'")
                            
                            # Проверяем, что это Cloudflare чекбокс
                            if ('cf' in (name or '') or 'cf' in (class_name or '') or 
                                'turnstile' in (name or '') or 'turnstile' in (class_name or '') or
                                'challenge' in (name or '') or 'challenge' in (class_name or '')):
                                logger.info(f"Найдён Cloudflare чекбокс: name='{name}', class='{class_name}'")
                                checkbox.click()
                                logger.info("Кликнули на Cloudflare чекбокс")
                                cf_found = True
                                time.sleep(5)
                                break
                        except Exception as e:
                            logger.info(f"Ошибка при клике на чекбокс {i+1}: {e}")
                    
                    if cf_found:
                        logger.info("Cloudflare проверка завершена")
                    else:
                        logger.info("Cloudflare элементы не найдены")
                        
            except Exception as e:
                logger.info(f"Ошибка при обработке Cloudflare: {e}")
            
            # Создаем временную метку для отладки
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Сохраняем скриншот с временной меткой (если включено)
            if SAVE_SCREENSHOTS:
                screenshot_path = os.path.join(SCREENSHOTS_FOLDER, f"dexscreener_{timestamp}.png")
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Скриншот сохранён: {screenshot_path}")
            else:
                logger.info("Сохранение скриншотов отключено")
            
            # Ждём загрузку таблицы с токенами
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/solana/"], a[href*="/ethereum/"], a[href*="/base/"]')))
                time.sleep(5)  # Даём время на полную загрузку данных
            except Exception:
                logger.warning("Не удалось дождаться загрузки таблицы, пробуем подождать ещё")
                time.sleep(15)  # Ждём ещё 15 секунд
                
                # Проверяем ещё раз
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/solana/"], a[href*="/ethereum/"], a[href*="/base/"]')))
                    logger.info("Таблица загрузилась после дополнительного ожидания")
                except Exception:
                    logger.warning("Таблица всё ещё не загружена, продолжаем")
            
            tokens = {}
            
            # Используем более точный подход - ищем ссылки на токены
            token_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/solana/"], a[href*="/ethereum/"], a[href*="/base/"], a[href*="/blast/"], a[href*="/arbitrum/"], a[href*="/polygon/"]')
            
            logger.info(f"Найдено {len(token_links)} ссылок на токены")
            
            # Если не нашли токены, пробуем альтернативный селектор
            if len(token_links) == 0:
                logger.warning("Не найдено токенов, пробуем альтернативный селектор...")
                token_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/"]')
                logger.info(f"Альтернативным селектором найдено {len(token_links)} ссылок")
            
            # Обрабатываем каждую ссылку
            for i, link in enumerate(token_links[:100]):  # Берём максимум 100
                try:
                    # Получаем текст всей строки
                    row_text = link.text
                    if not row_text:
                        continue
                    
                    # Получаем URL
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Парсим данные из текста
                    lines = row_text.split('\n')
                    
                    if len(lines) < 10:  # Минимальное количество строк для валидного токена
                        continue
                    
                    # Логируем первые несколько для отладки
                    if i < 5:
                        logger.info(f"Токен {i+1} строки: {lines}")
                        logger.info(f"URL: {href}")
                    
                    # Извлекаем ранг - ВАЖНО: используем реальный ранг из позиции
                    rank = i + 1  # Позиция в списке = реальный ранг
                    
                    # Также проверяем, есть ли номер в первой строке
                    rank_str = lines[0].strip()
                    if rank_str.startswith('#'):
                        try:
                            parsed_rank = int(rank_str[1:])
                            # Используем parsed_rank только если он близок к позиции
                            if abs(parsed_rank - rank) <= 2:
                                rank = parsed_rank
                        except:
                            pass
                    
                    # Извлекаем пару токенов
                    pair = None
                    
                    # Проверяем, есть ли тип маркета (CPMM, DLMM и т.д.) в позиции 1
                    market_types = ['CPMM', 'DLMM', 'V2', 'V3', 'AMM']
                    start_idx = 1
                    
                    if len(lines) > 1 and lines[1].strip() in market_types:
                        start_idx = 2  # Пропускаем тип маркета
                    
                    # Ищем паттерн TOKEN / TOKEN
                    # Проверяем позиции где может быть разделитель '/'
                    for j in range(start_idx, min(start_idx + 6, len(lines) - 1)):
                        if j+1 < len(lines) and lines[j+1].strip() == '/':
                            if j+2 < len(lines):
                                token1 = lines[j].strip()
                                token2 = lines[j+2].strip()
                                # Проверяем, что это токены
                                if (token1 and token2 and 
                                    len(token1) <= 20 and len(token2) <= 20 and
                                    not token1.startswith('$') and not token2.startswith('$') and
                                    not any(char in token1 for char in ['%', '(', ')']) and
                                    not any(char in token2 for char in ['%', '(', ')'])):
                                    pair = f"{token1}/{token2}"
                                    break
                    
                    if not pair:
                        # Альтернативный метод: ищем паттерн "TOKEN/TOKEN" в одной строке
                        for j in range(start_idx, min(start_idx + 4, len(lines))):
                            if '/' in lines[j] and not lines[j].startswith('$'):
                                parts = lines[j].split('/')
                                if len(parts) == 2:
                                    token1 = parts[0].strip()
                                    token2 = parts[1].strip()
                                    if (token1 and token2 and 
                                        len(token1) <= 20 and len(token2) <= 20):
                                        pair = f"{token1}/{token2}"
                                        break
                    
                    if not pair:
                        logger.warning(f"Не удалось извлечь пару для токена {i+1}")
                        continue
                    
                    # Извлекаем маркет кап - ищем более тщательно
                    market_cap = 0
                    
                    # Ищем маркет кап в последних строках
                    for idx in range(len(lines)-1, max(len(lines)-5, 0), -1):
                        line = lines[idx].strip()
                        if '$' in line and any(suffix in line for suffix in ['K', 'M', 'B']):
                            # Убираем запятые и пробелы
                            clean_line = line.replace(',', '').replace(' ', '')
                            
                            # Ищем паттерн маркет капа
                            matches = re.findall(r'\$?([\d.]+)([KMB])', clean_line)
                            if matches:
                                # Берём последнее значение (обычно это маркет кап)
                                value = float(matches[-1][0])
                                suffix = matches[-1][1]
                                
                                if suffix == 'K':
                                    market_cap = value * 1000
                                elif suffix == 'M':
                                    market_cap = value * 1_000_000
                                elif suffix == 'B':
                                    market_cap = value * 1_000_000_000
                                
                                # Проверяем, что это в рамках наших фильтров
                                if 150_000 <= market_cap <= 15_000_000:
                                    break
                                else:
                                    market_cap = 0  # Сбрасываем если не подходит под фильтр
                    
                    # Пропускаем токены без валидного маркет капа
                    if market_cap == 0:
                        logger.warning(f"Токен {pair} пропущен - маркет кап не найден или вне диапазона")
                        continue
                    
                    # Используем URL как уникальный идентификатор
                    token_id = href
                    
                    tokens[token_id] = {
                        'rank': rank,
                        'pair': pair,
                        'symbol': pair.split('/')[0],  # Первый токен из пары
                        'marketCap': market_cap,
                        'url': href
                    }
                    
                    # Логируем для отладки первые несколько токенов
                    if rank <= 5:
                        logger.info(f"Токен #{rank}: {pair}, MC: ${market_cap:,.0f}, URL: {href}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при обработке токена {i}: {e}")
                    continue
            
            logger.info(f"Успешно получено {len(tokens)} токенов с валидным маркет капом")
            
            # Если получили мало токенов, сохраняем HTML для отладки
            if len(tokens) < 5:
                logger.warning("Получено мало токенов, сохраняем HTML для отладки")
                with open(os.path.join(DATA_FOLDER, f"debug_html_{timestamp}.html"), 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.info("HTML страницы сохранён для отладки")
            
            return tokens
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            return {}
    
    def find_new_tokens(self, current_tokens):
        """Находим новые токены, которых не было в прошлой проверке"""
        new_tokens = {}
        
        for token_id, token_data in current_tokens.items():
            if token_id not in self.previous_tokens:
                new_tokens[token_id] = token_data
        
        return new_tokens
    
    def format_token_message(self, new_tokens):
        """Форматируем сообщение о новых токенах"""
        if not new_tokens:
            return None
        
        message = f"🆕 New tokens appeared in Trending 1h: ({len(new_tokens)})\n\n"
        
        # Сортируем по рангу
        sorted_tokens = sorted(new_tokens.items(), key=lambda x: x[1]['rank'])
        
        for i, (token_id, token_data) in enumerate(sorted_tokens, 1):
            # Форматируем маркет кап
            market_cap = token_data['marketCap']
            if market_cap >= 1_000_000:
                market_cap_str = f"${market_cap/1_000_000:.2f}M"
            elif market_cap >= 1_000:
                market_cap_str = f"${market_cap/1_000:.2f}K"
            elif market_cap > 0:
                market_cap_str = f"${market_cap:.2f}"
            else:
                market_cap_str = "N/A"
            
            # Используем пару токенов вместо просто символа
            pair = token_data.get('pair', token_data['symbol'])
            
            # Добавляем информацию о токене
            if token_data['url']:
                message += f"{i}. [{pair}]({token_data['url']})\n"
            else:
                message += f"{i}. {pair}\n"
            
            message += f"   Market Cap: {market_cap_str}\n"
            message += f"   Rank in trending: #{token_data['rank']}\n\n"
        
        return message
    
    async def check_and_notify(self):
        """Основная функция проверки и отправки уведомлений"""
        logger.info("check_and_notify: старт")
        
        try:
            # Получаем текущий список токенов
            current_tokens = self.fetch_trending_tokens()
            logger.info(f"check_and_notify: получено {len(current_tokens)} токенов")
            
            if not current_tokens:
                logger.warning("Не удалось получить список токенов")
                return
        except Exception as e:
            logger.error(f"Ошибка при получении токенов: {e}")
            return
        # Если это первый запуск (нет сохранённых токенов)
        if not self.previous_tokens:
            logger.info("Первый запуск - отправляем текущие токены")
            self.save_current_tokens(current_tokens)
            self.previous_tokens = current_tokens
            
            # Отправляем текущие топ-10 токенов
            try:
                # Берём топ-10 токенов
                top_10 = dict(list(sorted(current_tokens.items(), key=lambda x: x[1]['rank'])[:10]))
                
                message = f"🚀 Бот запущен! Текущие топ-10 трендовых токенов:\n\n"
                
                for i, (token_id, token_data) in enumerate(top_10.items(), 1):
                    # Форматируем маркет кап
                    market_cap = token_data['marketCap']
                    if market_cap >= 1_000_000:
                        market_cap_str = f"${market_cap/1_000_000:.2f}M"
                    elif market_cap >= 1_000:
                        market_cap_str = f"${market_cap/1_000:.2f}K"
                    else:
                        market_cap_str = f"${market_cap:.2f}"
                    
                    # Используем пару токенов
                    pair = token_data.get('pair', token_data['symbol'])
                    
                    if token_data['url']:
                        message += f"{i}. [{pair}]({token_data['url']}) - {market_cap_str}\n"
                    else:
                        message += f"{i}. {pair} - {market_cap_str}\n"
                
                message += f"\n📊 Всего токенов отслеживается: {len(current_tokens)}\n"
                message += "🔍 Фильтры: MC $150K-$15M, объём ≥$75K\n"
                message += "⏰ Следующая проверка через 10 минут"
                
                await self.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("check_and_notify: отправлены текущие токены при первом запуске")
            except Exception as e:
                logger.error(f"Ошибка при отправке токенов при первом запуске: {e}")
            return
        # Находим новые токены
        new_tokens = self.find_new_tokens(current_tokens)
        logger.info(f"check_and_notify: найдено {len(new_tokens)} новых токенов")
        
        # Обновляем статистику
        stats['checks_performed'] += 1
        stats['new_tokens_found'] += len(new_tokens)
        
        # Если есть новые токены, отправляем уведомление
        if new_tokens:
            message = self.format_token_message(new_tokens)
            if message:
                try:
                    await self.bot.send_message(
                        chat_id=CHAT_ID,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    logger.info(f"check_and_notify: отправлено уведомление о {len(new_tokens)} новых токенах")
                    stats['messages_sent'] += 1
                except Exception as e:
                    logger.error(f"Ошибка при отправке уведомления: {e}")
                    stats['errors_count'] += 1
        else:
            logger.info("check_and_notify: новых токенов не найдено")
        # Сохраняем текущее состояние
        self.save_current_tokens(current_tokens)
        self.previous_tokens = current_tokens
        logger.info("check_and_notify: завершено")
    
    async def show_top_10(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /show10 - показывает топ-10 текущих трендовых токенов"""
        # Немедленный ответ, что команда получена
        processing_msg = await update.message.reply_text("⏳ Получаю список трендовых токенов...")
        
        current_tokens = self.fetch_trending_tokens()
        
        if not current_tokens:
            await processing_msg.edit_text("❌ Не удалось получить список токенов")
            return
        
        # Берём топ-10
        top_10 = dict(list(sorted(current_tokens.items(), key=lambda x: x[1]['rank'])[:10]))
        
        message = "📊 Top 10 Trending Tokens (1h):\n\n"
        
        for token_id, token_data in top_10.items():
            # Форматируем маркет кап
            market_cap = token_data['marketCap']
            if market_cap >= 1_000_000:
                market_cap_str = f"${market_cap/1_000_000:.2f}M"
            elif market_cap >= 1_000:
                market_cap_str = f"${market_cap/1_000:.2f}K"
            elif market_cap > 0:
                market_cap_str = f"${market_cap:.2f}"
            else:
                market_cap_str = "N/A"
            
            # Используем пару токенов
            pair = token_data.get('pair', token_data['symbol'])
            
            if token_data['url']:
                message += f"#{token_data['rank']} [{pair}]({token_data['url']}) - {market_cap_str}\n"
            else:
                message += f"#{token_data['rank']} {pair} - {market_cap_str}\n"
        
        await processing_msg.edit_text(
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        await update.message.reply_text(
            "👋 Привет! Я бот для отслеживания трендовых токенов на Dexscreener.\n\n"
            "Доступные команды:\n"
            "/show10 - показать топ-10 текущих трендовых токенов\n"
            "/changes - показать изменения в позициях токенов\n"
            "/status - статус бота и системы\n"
            "/stats - статистика работы\n"
            "/logs - последние логи\n"
            "/restart - перезапустить бота\n"
            "/stop - остановить бота\n"
            "/cleanup - очистить старые файлы\n"
            "/help - подробная справка по командам\n"
            "/start - показать это сообщение\n\n"
            "Я автоматически проверяю новые токены каждые 10 минут!"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help - показывает подробную справку по всем командам"""
        help_text = """
🤖 **Справка по командам Dexscreener Bot**

📊 **Основные команды:**
• `/show10` - Показывает топ-10 текущих трендовых токенов с их маркет капом и ссылками на Dexscreener

• `/changes` - Анализирует изменения в позициях токенов:
  - Новые токены, появившиеся в трендинге
  - Большие движения (изменения позиций ≥10)
  - Токены, выпавшие из топа

📈 **Мониторинг и статистика:**
• `/status` - Показывает текущий статус бота:
  - Время работы
  - Количество выполненных проверок
  - Найденные новые токены
  - Загрузка системы (CPU, RAM, диск)

• `/stats` - Подробная статистика работы:
  - Средние показатели за проверку
  - Процент ошибок
  - Детальная аналитика

• `/health` - Проверка здоровья системы:
  - Статус компонентов
  - Состояние WebDriver
  - Системные ресурсы

🔧 **Управление ботом:**
• `/logs` - Показывает последние 10 строк логов для диагностики проблем

• `/restart` - Перезапускает бота (полезно после обновлений кода)

• `/stop` - Полностью останавливает бота и прекращает автоматические проверки

• `/cleanup` - Принудительная очистка старых файлов

📋 **Информация:**
• `/help` - Показывает эту справку

• `/start` - Показывает приветственное сообщение

---
⚙️ **Автоматические функции:**
• Проверка новых токенов каждые 10 минут
• Автоочистка старых файлов каждые 100 минут
• Фильтры: маркет кап $150K-$15M, объём 24ч ≥$75K
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status - показывает статус бота и системы"""
        uptime = self.get_uptime()
        system_info = self.get_system_info()
        
        message = "📊 *Статус бота*\n\n"
        message += "🟢 Статус: Работает\n"
        message += f"⏰ Время работы: {uptime}\n"
        message += f"🔄 Проверок выполнено: {stats['checks_performed']}\n"
        message += f"🆕 Новых токенов найдено: {stats['new_tokens_found']}\n"
        message += f"📨 Сообщений отправлено: {stats['messages_sent']}\n"
        message += f"❌ Ошибок: {stats['errors_count']}\n\n"
        
        if system_info:
            message += "💻 *Система*\n"
            message += f"🖥️ CPU: {system_info['cpu_percent']:.1f}%\n"
            message += f"🧠 RAM: {system_info['memory_percent']:.1f}% ({system_info['memory_used']:.1f}GB/{system_info['memory_total']:.1f}GB)\n"
            message += f"💾 Диск: {system_info['disk_percent']:.1f}% ({system_info['disk_used']:.1f}GB/{system_info['disk_total']:.1f}GB)\n"
        else:
            message += "💻 *Система*: Информация недоступна\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - показывает подробную статистику"""
        uptime = self.get_uptime()
        
        # Рассчитываем средние показатели
        if stats['checks_performed'] > 0:
            avg_tokens_per_check = stats['new_tokens_found'] / stats['checks_performed']
            avg_messages_per_check = stats['messages_sent'] / stats['checks_performed']
        else:
            avg_tokens_per_check = 0
            avg_messages_per_check = 0
        
        message = "📈 *Статистика работы*\n\n"
        message += f"⏰ Время работы: {uptime}\n"
        message += f"🔄 Всего проверок: {stats['checks_performed']}\n"
        message += f"🆕 Найдено новых токенов: {stats['new_tokens_found']}\n"
        message += f"📨 Отправлено сообщений: {stats['messages_sent']}\n"
        message += f"❌ Ошибок: {stats['errors_count']}\n\n"
        message += "📊 *Средние показатели*\n"
        message += f"🆕 Новых токенов за проверку: {avg_tokens_per_check:.2f}\n"
        message += f"📨 Сообщений за проверку: {avg_messages_per_check:.2f}\n"
        
        if stats['checks_performed'] > 0:
            error_rate = (stats['errors_count'] / stats['checks_performed']) * 100
            message += f"❌ Процент ошибок: {error_rate:.1f}%\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /logs - показывает последние логи"""
        try:
            # Читаем последние 10 строк из лог-файла (если есть)
            log_file = "bot.log"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) > 10 else lines
                    logs = ''.join(last_lines)
                    
                    if len(logs) > 4000:  # Telegram лимит
                        logs = logs[-4000:]
                    
                    await update.message.reply_text(f"📋 *Последние логи*\n\n```\n{logs}\n```", parse_mode='Markdown')
            else:
                await update.message.reply_text("📋 Лог-файл не найден. Логи выводятся в консоль.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при чтении логов: {e}")
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /restart - перезапускает бота"""
        await update.message.reply_text(
            "🔄 Перезапускаю бота...\n"
            "Это может занять несколько секунд."
        )
        logger.info("Перезапуск бота по команде пользователя")
        
        # Пробуем разные способы перезапуска
        try:
            # 1. Docker Compose (рекомендуется)
            result = os.system("docker-compose restart dx-bot")
            if result == 0:
                await update.message.reply_text("✅ Бот перезапущен через Docker Compose")
                return
        except:
            pass
        
        try:
            # 2. Systemd (если настроен)
            result = os.system("sudo systemctl restart dx-bot")
            if result == 0:
                await update.message.reply_text("✅ Бот перезапущен через systemd")
                return
        except:
            pass
        
        # 3. Если ничего не сработало
        await update.message.reply_text(
            "⚠️ Не удалось автоматически перезапустить бота.\n"
            "Перезапустите вручную:\n"
            "• Docker: `docker-compose restart`\n"
            "• Systemd: `sudo systemctl restart dx-bot`\n"
            "• Или перезапустите сервер"
        )
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stop - останавливает бота"""
        await update.message.reply_text(
            "🛑 Останавливаю бота...\n"
            "Автоматические проверки прекращены.\n"
            "Для перезапуска используйте команду /start"
        )
        logger.info("Бот остановлен пользователем")
        await self.graceful_shutdown()
        # Останавливаем приложение
        context.application.stop()
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /health - показывает состояние здоровья системы"""
        health = self.health_check()
        
        message = "🏥 *Health Check*\n\n"
        message += f"📊 Статус: {health['status']}\n"
        message += f"⏰ Время работы: {health['uptime']}\n"
        message += f"🤖 Бот работает: {'✅' if health['bot_running'] else '❌'}\n"
        message += f"🌐 WebDriver: {'✅' if health['driver_status'] else '❌'}\n"
        message += f"🕐 Последняя проверка: {health['last_check']}\n\n"
        
        if health['system_info']:
            sys_info = health['system_info']
            message += "💻 *Система*\n"
            message += f"🖥️ CPU: {sys_info['cpu_percent']:.1f}%\n"
            message += f"🧠 RAM: {sys_info['memory_percent']:.1f}%\n"
            message += f"💾 Диск: {sys_info['disk_percent']:.1f}%\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /cleanup - принудительная очистка старых файлов"""
        await update.message.reply_text("🧹 Выполняю принудительную очистку файлов...")
        
        try:
            # Выполняем очистку
            self.cleanup_old_files()
            
            # Показываем статистику по папкам
            json_count = len(glob.glob(os.path.join(JSON_HISTORY_FOLDER, "*.json")))
            screenshot_count = len(glob.glob(os.path.join(SCREENSHOTS_FOLDER, "*.png")))
            
            message = "✅ Очистка завершена!\n\n"
            message += f"📁 JSON файлов: {json_count} (удаляются через {FILE_RETENTION_MINUTES} мин)\n"
            message += f"📸 Скриншотов: {screenshot_count} (удаляются через {SCREENSHOT_RETENTION_MINUTES} мин)\n"
            
            if not SAVE_SCREENSHOTS:
                message += "\n💡 Скриншоты отключены для экономии места"
            else:
                message += f"\n⚡ Частая очистка: каждые {CLEANUP_INTERVAL//60} минут"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при очистке: {e}")
    
    async def show_changes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /changes - показывает изменения в позициях токенов"""
        if not self.previous_tokens:
            await update.message.reply_text("❌ Нет данных о предыдущей проверке")
            return
        
        # Немедленный ответ, что команда получена
        processing_msg = await update.message.reply_text("⏳ Анализирую изменения...")
        
        current_tokens = self.fetch_trending_tokens()
        
        if not current_tokens:
            await processing_msg.edit_text("❌ Не удалось получить список токенов")
            return
        
        # Анализируем изменения
        new_tokens = []
        position_changes = []
        dropped_tokens = []
        
        # Находим новые токены и изменения позиций
        for token_id, token_data in current_tokens.items():
            if token_id not in self.previous_tokens:
                new_tokens.append(token_data)
            else:
                old_rank = self.previous_tokens[token_id]['rank']
                new_rank = token_data['rank']
                if old_rank != new_rank:
                    change = old_rank - new_rank
                    position_changes.append({
                        'token': token_data,
                        'old_rank': old_rank,
                        'new_rank': new_rank,
                        'change': change
                    })
        
        # Находим токены, которые выпали из топа
        for token_id, token_data in self.previous_tokens.items():
            if token_id not in current_tokens:
                dropped_tokens.append(token_data)
        
        # Формируем сообщение
        message = "📊 Изменения в Trending (1h):\n\n"
        
        # Новые токены
        if new_tokens:
            message += f"🆕 Новых токенов: {len(new_tokens)}\n"
            for token in sorted(new_tokens, key=lambda x: x['rank'])[:5]:
                pair = token.get('pair', token['symbol'])
                url = token.get('url')
                if url:
                    pair_str = f"[{pair}]({url})"
                else:
                    pair_str = pair
                message += f"  • #{token['rank']} {pair_str}\n"
            if len(new_tokens) > 5:
                message += f"  • и ещё {len(new_tokens) - 5}...\n"
            message += "\n"
        
        # Значительные изменения позиций
        big_movers = [c for c in position_changes if abs(c['change']) >= 10]
        if big_movers:
            message += "🚀 Большие движения:\n"
            for change in sorted(big_movers, key=lambda x: x['change'], reverse=True)[:5]:
                pair = change['token'].get('pair', change['token']['symbol'])
                url = change['token'].get('url')
                if url:
                    pair_str = f"[{pair}]({url})"
                else:
                    pair_str = pair
                emoji = "📈" if change['change'] > 0 else "📉"
                message += f"  {emoji} {pair_str}: #{change['old_rank']} → #{change['new_rank']} ({change['change']:+d})\n"
            message += "\n"
        
        # Выпавшие токены
        if dropped_tokens:
            message += f"❌ Выпало из топа: {len(dropped_tokens)}\n"
            for token in sorted(dropped_tokens, key=lambda x: x['rank'])[:3]:
                pair = token.get('pair', token['symbol'])
                url = token.get('url')
                if url:
                    pair_str = f"[{pair}]({url})"
                else:
                    pair_str = pair
                message += f"  • {pair_str} (был #{token['rank']})\n"
            if len(dropped_tokens) > 3:
                message += f"  • и ещё {len(dropped_tokens) - 3}...\n"
        
        if not new_tokens and not big_movers and not dropped_tokens:
            message = "😴 Нет значительных изменений в топе"
        
        await processing_msg.edit_text(
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    def get_system_info(self):
        """Получаем информацию о системе"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used / (1024**3),  # GB
                'memory_total': memory.total / (1024**3),  # GB
                'disk_percent': disk.percent,
                'disk_used': disk.used / (1024**3),  # GB
                'disk_total': disk.total / (1024**3)  # GB
            }
        except Exception as e:
            logger.error(f"Ошибка при получении системной информации: {e}")
            return None
    
    def get_uptime(self):
        """Получаем время работы бота"""
        uptime = datetime.now() - bot_start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}д {hours}ч {minutes}м"
        elif hours > 0:
            return f"{hours}ч {minutes}м"
        else:
            return f"{minutes}м {seconds}с"
    
    def health_check(self):
        """Проверка здоровья системы"""
        health_status = {
            'bot_running': bot_running,
            'driver_status': self.driver is not None,
            'uptime': self.get_uptime(),
            'system_info': self.get_system_info(),
            'last_check': datetime.now().isoformat()
        }
        
        # Проверяем критические компоненты
        if not bot_running:
            health_status['status'] = 'STOPPED'
        elif not self.driver:
            health_status['status'] = 'DRIVER_ERROR'
        else:
            health_status['status'] = 'HEALTHY'
        
        return health_status

    def cleanup(self):
        """Закрываем браузер при завершении работы"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver закрыт")
        except Exception as e:
            logger.error(f"Ошибка при закрытии WebDriver: {e}")
    
    async def graceful_shutdown(self):
        """Graceful shutdown бота"""
        global bot_running
        logger.info("Начинаю graceful shutdown...")
        
        # Останавливаем основной цикл
        bot_running = False
        
        # Сохраняем текущее состояние
        if hasattr(self, 'previous_tokens'):
            self.save_current_tokens(self.previous_tokens)
        
        # Закрываем WebDriver
        self.cleanup()
        
        # Отправляем сообщение о завершении работы
        try:
            await self.bot.send_message(
                chat_id=CHAT_ID,
                text="🛑 Бот остановлен. Автоматические проверки прекращены."
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения о завершении: {e}")
        
        logger.info("Graceful shutdown завершён")

    def cleanup_old_files(self):
        """Удаляем старые файлы из папок json_history и screenshots"""
        try:
            # Небольшая задержка для безопасности (если парсинг только что завершился)
            time.sleep(1)
            
            # Разные интервалы для разных типов файлов
            json_cutoff_time = datetime.now() - timedelta(minutes=FILE_RETENTION_MINUTES)
            screenshot_cutoff_time = datetime.now() - timedelta(minutes=SCREENSHOT_RETENTION_MINUTES)
            
            # Очищаем json_history
            json_files = glob.glob(os.path.join(JSON_HISTORY_FOLDER, "*.json"))
            deleted_json = 0
            for file_path in json_files:
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < json_cutoff_time:
                    os.remove(file_path)
                    deleted_json += 1
            
            # Очищаем screenshots (только если они включены)
            if SAVE_SCREENSHOTS:
                screenshot_files = glob.glob(os.path.join(SCREENSHOTS_FOLDER, "*.png"))
                deleted_screenshots = 0
                for file_path in screenshot_files:
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < screenshot_cutoff_time:
                        os.remove(file_path)
                        deleted_screenshots += 1
            else:
                deleted_screenshots = 0
            
            if deleted_json > 0 or deleted_screenshots > 0:
                logger.info(f"Очистка: удалено {deleted_json} JSON файлов и {deleted_screenshots} скриншотов")
                
        except Exception as e:
            logger.error(f"Ошибка при очистке старых файлов: {e}")

# Удаляю функцию periodic_check и её вызовы
# async def periodic_check(bot_instance):
#     ...
# def main():
def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Получен сигнал {signum}, начинаю graceful shutdown...")
    global bot_running
    bot_running = False
    sys.exit(0)

def main():
    """Основная функция запуска бота"""
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаём экземпляр бота
    bot_instance = DexscreenerBot()
    
    # Создаём приложение Telegram бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Сохраняем экземпляр бота в bot_data для доступа из job
    application.bot_data['bot_instance'] = bot_instance

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", bot_instance.start_command))
    application.add_handler(CommandHandler("show10", bot_instance.show_top_10))
    application.add_handler(CommandHandler("changes", bot_instance.show_changes))
    application.add_handler(CommandHandler("status", bot_instance.status_command))
    application.add_handler(CommandHandler("stats", bot_instance.stats_command))
    application.add_handler(CommandHandler("logs", bot_instance.logs_command))
    application.add_handler(CommandHandler("restart", bot_instance.restart_command))
    application.add_handler(CommandHandler("stop", bot_instance.stop_command))
    application.add_handler(CommandHandler("help", bot_instance.help_command))
    application.add_handler(CommandHandler("health", bot_instance.health_command))
    application.add_handler(CommandHandler("cleanup", bot_instance.cleanup_command))

    # Периодическая задача через job_queue
    async def periodic_check_job(context: ContextTypes.DEFAULT_TYPE):
        global bot_running
        if not bot_running:
            return
        try:
            logger.info("periodic_check_job запущен")
            await context.bot_data['bot_instance'].check_and_notify()
        except Exception as e:
            logger.error(f"Ошибка в periodic_check_job: {e}")

    # Задача очистки старых файлов
    async def cleanup_job(context: ContextTypes.DEFAULT_TYPE):
        global bot_running
        if not bot_running:
            return
        try:
            logger.info("cleanup_job запущен")
            context.bot_data['bot_instance'].cleanup_old_files()
        except Exception as e:
            logger.error(f"Ошибка в cleanup_job: {e}")

    # Запускаем первую проверку сразу, а потом каждые 10 минут
    application.job_queue.run_repeating(periodic_check_job, interval=CHECK_INTERVAL, first=0)
    application.job_queue.run_repeating(cleanup_job, interval=CLEANUP_INTERVAL, first=0)  # 15 минут

    # Добавляем задачу отправки сообщения в job_queue
    # Убираем дублирующее сообщение, так как токены будут отправлены в первой проверке

    try:
        application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        bot_instance.cleanup()

if __name__ == "__main__":
    main()