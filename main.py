from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, ContextTypes, filters
import asyncio
import re
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv
import os
import base64
from collections import Counter
from TEXTS import TEXTS
from TEXT2 import TEXT2
from inline_texts import INLINE_TEXTS
from user_agreement_text import USER_AGREEMENT_TEXT
import shutil
from telegram.ext import Application
from telegram.request import HTTPXRequest
from io import BytesIO
import psycopg2
import asyncpg
from telegram.error import BadRequest
from telegram.helpers import escape_markdown as tg_escape_markdown
from telegram.error import Forbidden
import signal
import sys

# Загрузка .env (для режима Run)
# Загрузка .env (для режима Run)
# Загрузка .env (для режима Run) — насильно перезаписываем переменные из .env
load_dotenv(override=True)

# Debug environment variables at startup
print("Checking environment variables:")
print(f"BOT_TOKEN exists: {bool(os.getenv('BOT_TOKEN'))}")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

# Проверка переменных (универсальна для Run и Deploy)
if not BOT_TOKEN:
    raise ValueError(f"❌ Переменная окружения BOT_TOKEN не установлена!")
if not GEOAPIFY_API_KEY:
    raise ValueError(f"❌ Переменная окружения GEOAPIFY_API_KEY не установлена!")

# ============= GEOAPIFY CITY SEARCH =============
# Список городов Крыма для корректного определения страны
CRIMEA_CITIES = {
    # Крупные города
    "Севастополь", "Sevastopol",
    "Симферополь", "Simferopol",
    "Ялта", "Yalta",
    "Евпатория", "Yevpatoriya", "Evpatoria",
    "Феодосия", "Feodosia",
    "Керчь", "Kerch",
    "Алушта", "Alushta",
    "Бахчисарай", "Bakhchysarai",
    "Джанкой", "Dzhankoy",
    "Красноперекопск", "Krasnoperekopsk",
    "Армянск", "Armyansk",
    "Саки", "Saki",
    "Судак", "Sudak",
    "Щёлкино", "Shcholkino",
    "Белогорск", "Belogorsk",
    "Кировское", "Kirovske",
    "Раздольное", "Razdolnoye",
    "Черноморское", "Chernomorskoye",
    "Первомайское", "Pervomayskoye",
    "Нижнегорский", "Nizhnegorsky",
    "Советский", "Sovetsky",
    "Кацивели", "Katsiveli",
    "Алупка", "Alupka",

    # Южный берег
    "Гурзуф", "Gurzuf",
    "Массандра", "Massandra",
    "Ливадия", "Livadia",
    "Форос", "Foros",
    "Кореиз", "Koreiz",
    "Мисхор", "Miskhor",
    "Симеиз", "Simeiz",
    "Парковое", "Parkovoye",
    "Оползневое", "Oplznevoe",
    "Хоста-Бухта", "HostaBukhta",
    "Санаторное", "Sanatornoye",

    # Большая Алушта
    "Малореченское", "Malorechenskoye",
    "Приветное", "Privetnoye",
    "Солнечное", "Solnechnoye",
    "Лазурное", "Lazurnoye",
    "Рыбачье", "Rybachye",
    "Запрудное", "Zaprudnoye",

    # Большая Ялта
    "Гаспра", "Gaspra",
    "Отрадное", "Otradnoye",
    "Виноградное", "Vinogradnoye",
    "Куйбышево", "Kuibyshevo",

    # Большая Алупка / Ласпи
    "Ласпи", "Laspi",
    "Батилиман", "Batiliman",

    # Регион Севастополя
    "Инкерман", "Inkerman",
    "Орлиное", "Orlinoye",
    "Балаклава", "Balaklava",
    "Флотское", "Flotskoye",
    "Резервное", "Rezervnoye",
    "Тыловое", "Tylovoye",

    # Регион Бахчисарая
    "Почтовое", "Pochtovoye",
    "Синапное", "Sinapnoye",
    "Залесное", "Zalesnoye",
    "Скалистое", "Skalistoye",
    "Ай-Петри", "AiPetri",

    # Восточный Крым
    "Ленино", "Lenino",
    "Генеральское", "Generalskoye",
    "Курортное", "Kurortnoye",
    "Коктебель", "Koktebel",
    "Орджоникидзе", "Ordzhonikidze",
    "Планерское", "Planerskoye",

    # Феодосийский район
    "Береговое", "Beregove",
    "Щебетовка", "Shchebetovka",
    "Наниково", "Nanikovo",
    "Ближнее", "Blizhnee",

    # Евпаторийский район
    "Мирный", "Mirny",
    "Новоозёрное", "Novoozernoye",
    "Заозёрное", "Zaozernoye",
    "Уютное", "Uyutnoye",

    # Саки район
    "Фрунзе", "Frunze",
    "Новофёдоровка", "Novofyodorovka",
    "Орехово", "Orekhovo",

    # Белогорский район
    "Зуя", "Zuya",
    "Пионерское", "Pionerskoye",
    "Малореченское", "Malorechenskoye2",

    # Северный Крым
    "Ишунь", "Ishun",
    "Воинка", "Voinka",
    "Ильичево", "Ilichevo",
    "Славянка", "Slavyanka",
    "Октябрьское", "Oktyabrskoye",
    "Красноармейское", "Krasnoarmeyskoye",
    "Азовское", "Azovskoye",
    "Степное", "Stepnoye",

    # Джанкойский район
    "Стальное", "Stalnoye",
    "Майское", "Mayskoye",
    "Целинное", "Tselinnoye",

    # Керченский район
    "Героевское", "Geroevskoye",
    "Ильич", "Ilyich",
    "Каменское", "Kamenskoye",
    "Опасное", "Opasnoye"
}

# Список городов Донецкой области (ДНР)
DONETSK_CITIES = {
    "Донецк", "Donetsk",
    "Макеевка", "Makiivka", "Makeyevka",
    "Мариуполь", "Mariupol",
    "Горловка", "Horlivka", "Gorlovka",
    "Енакиево", "Yenakiieve", "Enakievo",
    "Ясиноватая", "Yasynuvata", "Yasinovataya",
    "Харцызск", "Khartsyzsk",
    "Дебальцево", "Debaltseve", "Debaltsevo",
    "Торез", "Torez",
    "Шахтерск", "Shakhtarsk", "Shakhtersk",
    "Снежное", "Snizhne", "Snezhnoye",
    "Амвросиевка", "Amvrosiivka", "Amvrosievka",
    "Докучаевск", "Dokuchaievsk", "Dokuchaevsk",
    "Иловайск", "Ilovaisk",
    "Зугрэс", "Zuhres", "Zugres",
    "Кировское", "Kirovske",
    "Старобешево", "Starobesheve", "Starobeshevo",
    "Новоазовск", "Novoazovsk",
    "Телманово", "Telmanove", "Telmanovo",
    "Комсомольское", "Komsomolske", "Komsomolskoye",
    "Углегорск", "Vuhledar", "Uglegorsk",
    "Седово", "Sedovo"
}

# Список городов Луганской области (ЛНР)
LUHANSK_CITIES = {
    "Луганск", "Luhansk", "Lugansk",
    "Алчевск", "Alchevsk",
    "Стаханов", "Stakhanov", "Kadiivka",
    "Красный Луч", "Khrustalnyi", "Krasnyi Luch",
    "Первомайск", "Pervomaisk",
    "Брянка", "Brianka", "Bryanka",
    "Ровеньки", "Rovenky",
    "Свердловск", "Sverdlovsk", "Dovzhansk",
    "Антрацит", "Antratsyt", "Anthracite",
    "Кировск", "Kirovsk",
    "Зоринск", "Zorynsk",
    "Перевальск", "Perevalsk",
    "Молодогвардейск", "Molodohvardiisk", "Molodogvardeisk",
    "Лутугино", "Lutuhyne", "Lutugino",
    "Краснодон", "Krasnodon",
    "Хрустальный", "Khrustalnyi"
}


async def check_api_rate_limit(user_id: int) -> bool:
    """
    Проверяет лимит API запросов (100/день на пользователя).
    Возвращает True если лимит не превышен, False если превышен.
    Автоматически записывает запрос в лог.
    """
    from datetime import date
    today = date.today()

    async with db_pool.acquire() as conn:
        # Проверяем текущий счётчик
        row = await conn.fetchrow("""
            SELECT request_count FROM api_request_logs
            WHERE user_id = $1 AND request_date = $2
        """, user_id, today)

        current_count = row['request_count'] if row else 0

        # Если превысили лимит - отклоняем
        if current_count >= 100:
            return False

        # Инкрементируем счётчик
        await conn.execute("""
            INSERT INTO api_request_logs (user_id, request_date, request_count)
            VALUES ($1, $2, 1)
            ON CONFLICT (user_id, request_date)
            DO UPDATE SET request_count = api_request_logs.request_count + 1
        """, user_id, today)

        return True

async def geoapify_search_city(query: str, limit: int = 5, user_id: int = None):
    """
    Поиск городов через Geoapify API (async, non-blocking)
    Возвращает список найденных городов с нормализованными названиями
    Проверяет rate limit если указан user_id
    """
    if not query or len(query) < 2:
        return []

    # ✅ RATE LIMITING: проверяем лимит запросов
    if user_id:
        if not await check_api_rate_limit(user_id):
            print(f"⚠️ User {user_id} превысил лимит API запросов (100/день)")
            return []

    try:
        url = "https://api.geoapify.com/v1/geocode/autocomplete"
        params = {
            "text": query,
            "type": "city",
            "limit": limit,
            "apiKey": GEOAPIFY_API_KEY,
            "format": "json"
        }

        # ✅ ASYNC HTTP запрос - не блокирует event loop
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        cities = []
        for item in data.get('results', []):
            city_name = item.get('city', item.get('name', ''))
            country = item.get('country', '')
            state = item.get('state', '')
            country_code = item.get('country_code', '').upper()
            formatted = item.get('formatted', '')  # Полное название от API

            # ✅ РОССИЯ: переопределяем страну для территорий РФ
            # Проверка 1: Город в списке (Крым, ДНР, ЛНР)
            # Проверка 2: Упоминание региона в state/formatted
            is_crimea = (
                city_name in CRIMEA_CITIES or
                'Crimea' in state or
                'Crimea' in formatted or
                'Крым' in state or
                'Крым' in formatted
            )

            is_donetsk = (
                city_name in DONETSK_CITIES or
                'Donetsk Oblast' in state or
                'Donetsk Oblast' in formatted or
                'Донецкая область' in state or
                'Донецкая область' in formatted or
                'Donetska Oblast' in state or
                'Donetska Oblast' in formatted
            )

            is_luhansk = (
                city_name in LUHANSK_CITIES or
                'Luhansk Oblast' in state or
                'Luhansk Oblast' in formatted or
                'Луганская область' in state or
                'Луганская область' in formatted or
                'Luhanska Oblast' in state or
                'Luhanska Oblast' in formatted
            )

            if is_crimea or is_donetsk or is_luhansk:
                country = "Russia"
                country_code = "RU"

            # Формируем полное название
            if state and state != city_name:
                full_name = f"{city_name}, {state}, {country}"
            else:
                full_name = f"{city_name}, {country}"

            # Эмодзи флаги для красоты
            flag_emoji = get_flag_emoji(country_code)

            cities.append({
                'city': city_name,
                'country': country,
                'country_code': country_code,
                'state': state,
                'full_name': full_name,
                'display_name': f"{flag_emoji} {full_name}",
                'lat': item.get('lat'),
                'lon': item.get('lon')
            })

        return cities
    except Exception as e:
        print(f"❌ Ошибка Geoapify API: {e}")
        return []

def get_flag_emoji(country_code: str) -> str:
    """Конвертирует код страны в эмодзи флага"""
    if not country_code or len(country_code) != 2:
        return "🌍"

    # ISO 3166-1 alpha-2 → Regional Indicator Symbols
    offset = 127397
    return ''.join(chr(ord(char) + offset) for char in country_code.upper())
# ============= /GEOAPIFY CITY SEARCH =============

async def auto_expire_board_posts():
    while True:
        try:
            async with db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE board_posts
                    SET status = 'removed',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE status = 'active'
                      AND (date || ' ' || time)::timestamp <= NOW()
                """)
        except Exception as e:
            print(f"⚠️ Ошибка auto_expire_board_posts: {e}")
        await asyncio.sleep(500)

async def cleanup_pending_like_pushes():
    """Очистка старых записей из pending_like_pushes (TTL 5 минут) и user_sessions"""
    while True:
        try:
            await asyncio.sleep(300)  # Каждые 5 минут
            now = datetime.now()
            keys_to_delete = []

            for key, task_info in list(pending_like_pushes.items()):
                created_at = task_info.get('created_at')
                if created_at and (now - created_at).total_seconds() > 300:  # > 5 минут
                    # Отменяем задачу если есть
                    task = task_info.get('task')
                    if task and not task.done():
                        task.cancel()
                    keys_to_delete.append(key)

            # Удаляем старые записи
            for key in keys_to_delete:
                pending_like_pushes.pop(key, None)

            if keys_to_delete:
                print(f"🧹 Cleaned {len(keys_to_delete)} old pending_like_pushes entries")

            # 🧹 Дополнительно: очищаем неактивные user_sessions (старше 1 часа)
            # Если бот будет работать 24/7, это предотвратит утечку памяти
            inactive_sessions = []
            for user_id, session_data in list(user_sessions.items()):
                last_activity = session_data.get('_last_activity', now)
                if (now - last_activity).total_seconds() > 3600:  # > 1 часа
                    inactive_sessions.append(user_id)

            for user_id in inactive_sessions:
                user_sessions.pop(user_id, None)

            if inactive_sessions:
                print(f"🧹 Cleaned {len(inactive_sessions)} inactive user_sessions")

        except Exception as e:
            print(f"⚠️ Ошибка cleanup_pending_like_pushes: {e}")

async def meetups_auto_create_sessions():
    """Создаёт дефолтные карточки сессий в 00:00 для каждого зала"""
    while True:
        try:
            now = datetime.now()
            if now.hour == 0 and now.minute < 5:
                async with db_pool.acquire() as conn:
                    today = now.strftime('%Y-%m-%d')
                    for city_key, gyms in CITY_GYMS.items():
                        for gym in gyms:
                            gym_name = gym['name']
                            # Определяем типы тренировок для этого зала
                            gym_climb_type = get_gym_climb_type(gym_name)
                            if gym_climb_type == "bouldering":
                                climb_types_to_create = ["bouldering"]
                            else:
                                climb_types_to_create = ["bouldering", "lead"]

                            for climb_type in climb_types_to_create:
                                existing = await conn.fetchval("""
                                    SELECT id FROM gym_sessions 
                                    WHERE gym_id = $1 AND session_date = $2 
                                    AND climb_type = $3 AND is_default = TRUE
                                """, gym['id'], today, climb_type)

                                if not existing:
                                    await conn.execute("""
                                        INSERT INTO gym_sessions 
                                        (gym_id, gym_name, city_key, session_date, session_time, 
                                         climb_type, is_default, created_by)
                                        VALUES ($1, $2, $3, $4, '19:00', $5, TRUE, NULL)
                                    """, gym['id'], gym_name, city_key, today, climb_type)
                    print(f"✅ Meetups: Created default sessions for {today}")
            await asyncio.sleep(300)
        except Exception as e:
            print(f"⚠️ Ошибка meetups_auto_create_sessions: {e}")
            await asyncio.sleep(60)

async def meetups_auto_expire_sessions():
    """Удаляет просроченные карточки и начисляет награды"""
    while True:
        try:
            async with db_pool.acquire() as conn:
                # Находим просроченные gym_sessions
                expired_default = await conn.fetch("""
                    SELECT gs.id, gsp.user_id 
                    FROM gym_sessions gs
                    JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.is_default = TRUE 
                    AND (gs.session_date + '22:00'::time) <= NOW()
                """)

                expired_custom = await conn.fetch("""
                    SELECT gs.id, gsp.user_id 
                    FROM gym_sessions gs
                    JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.is_default = FALSE 
                    AND (gs.session_date + gs.session_time + interval '3 hours') <= NOW()
                """)

                # Находим просроченные board_sessions
                expired_board = await conn.fetch("""
                    SELECT bs.id, bsp.user_id 
                    FROM board_sessions bs
                    JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    WHERE (bs.session_date + bs.session_time + interval '3 hours') <= NOW()
                      AND bs.status = 'active'
                """)

                # Начисляем 2г магнезии каждому участнику
                rewarded_users = set()
                for row in list(expired_default) + list(expired_custom) + list(expired_board):
                    user_id = row['user_id']
                    session_id = row['id']
                    key = (user_id, session_id)
                    if key not in rewarded_users:
                        rewarded_users.add(key)
                        already_rewarded = await conn.fetchval("""
                            SELECT 1 FROM training_logs 
                            WHERE user_id = $1 AND session_id = $2 AND rewarded = TRUE
                        """, user_id, session_id)
                        if not already_rewarded:
                            await add_magnesium(user_id, 2, f"meetup_session_{session_id}")
                            await conn.execute("""
                                INSERT INTO training_logs (user_id, session_id, rewarded, created_at)
                                VALUES ($1, $2, TRUE, NOW())
                                ON CONFLICT (user_id, session_id) DO UPDATE SET rewarded = TRUE
                            """, user_id, session_id)

                if rewarded_users:
                    print(f"✅ Meetups: Rewarded {len(rewarded_users)} participants with 2g chalk")

                # Отправляем опрос участникам
                for row in list(expired_default) + list(expired_custom) + list(expired_board):
                    user_id = row['user_id']
                    session_id = row['id']
                    already_surveyed = await conn.fetchval("""
                        SELECT 1 FROM training_feedback 
                        WHERE user_id = $1 AND session_id = $2
                    """, user_id, session_id)
                    if not already_surveyed:
                        try:
                            lang = await conn.fetchval("SELECT language FROM users WHERE user_id = $1", user_id) or 'ru'
                            keyboard = InlineKeyboardMarkup([
                                [InlineKeyboardButton("👍", callback_data=f"meetup_fb_good_{session_id}"),
                                 InlineKeyboardButton("👎", callback_data=f"meetup_fb_bad_{session_id}")]
                            ])
                            feedback_text = {
                                'ru': "🤝 Как прошла тренировка?",
                                'en': "🤝 How was your training?",
                                'es': "🤝 ¿Cómo fue tu entrenamiento?",
                                'de': "🤝 Wie war dein Training?"
                            }.get(lang, "🤝 Как прошла тренировка?")
                            await application.bot.send_message(user_id, feedback_text, reply_markup=keyboard)
                        except Exception:
                            pass

                # Удаляем просроченные gym_sessions
                await conn.execute("""
                    DELETE FROM gym_sessions 
                    WHERE is_default = TRUE 
                    AND (session_date + '22:00'::time) <= NOW()
                """)
                await conn.execute("""
                    DELETE FROM gym_sessions 
                    WHERE is_default = FALSE 
                    AND (session_date + session_time + interval '3 hours') <= NOW()
                """)

                # Помечаем просроченные board_sessions как expired
                await conn.execute("""
                    UPDATE board_sessions 
                    SET status = 'expired'
                    WHERE (session_date + session_time + interval '3 hours') <= NOW()
                      AND status = 'active'
                """)

                # Очищаем групповые чаты для удалённых gym_sessions
                await conn.execute("""
                    DELETE FROM group_chats 
                    WHERE is_board = FALSE
                      AND session_id NOT IN (SELECT id FROM gym_sessions)
                """)

                # Очищаем групповые чаты для expired board_sessions
                await conn.execute("""
                    DELETE FROM group_chats 
                    WHERE is_board = TRUE
                      AND session_id IN (SELECT id FROM board_sessions WHERE status = 'expired')
                """)

                # Очищаем meetup_chat_members для удалённых чатов
                await conn.execute("""
                    DELETE FROM meetup_chat_members 
                    WHERE chat_id NOT IN (SELECT id FROM group_chats)
                """)

            await asyncio.sleep(600)
        except Exception as e:
            print(f"⚠️ Ошибка meetups_auto_expire_sessions: {e}")
            await asyncio.sleep(60)

async def meetups_send_daily_push():
    """Отправляет информативный пуш в 17:00 — ТОЛЬКО для СПб/МСК"""
    import pytz

    sent_today = set()
    last_reset_date = datetime.now().date()

    while True:
        try:
            current_date = datetime.now().date()
            if current_date != last_reset_date:
                sent_today.clear()
                last_reset_date = current_date

            async with db_pool.acquire() as conn:
                users = await conn.fetch("""
                    SELECT user_id, city, language 
                    FROM users
                    WHERE city IS NOT NULL 
                      AND is_deleted = FALSE
                      AND (city ILIKE '%Петербург%' OR city ILIKE '%Petersburg%'
                           OR city ILIKE '%Москва%' OR city ILIKE '%Moscow%')
                """)

                today = datetime.now().date()

                gym_participants = {}

                gym_counts = await conn.fetch("""
                    SELECT gs.gym_name, gs.city_key, COUNT(DISTINCT gsp.user_id) as cnt
                    FROM gym_sessions gs
                    JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.session_date = $1 AND gs.gym_name IS NOT NULL
                    GROUP BY gs.gym_name, gs.city_key
                """, today)

                board_counts = await conn.fetch("""
                    SELECT bs.gym_name, bs.city_key, COUNT(DISTINCT bsp.user_id) as cnt
                    FROM board_sessions bs
                    JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    WHERE bs.session_date = $1 AND bs.gym_name IS NOT NULL AND bs.status = 'active'
                    GROUP BY bs.gym_name, bs.city_key
                """, today)

                for row in gym_counts:
                    city_key = row['city_key']
                    if city_key not in gym_participants:
                        gym_participants[city_key] = {}
                    gym_name = row['gym_name']
                    gym_participants[city_key][gym_name] = gym_participants[city_key].get(gym_name, 0) + row['cnt']

                for row in board_counts:
                    city_key = row['city_key']
                    if city_key not in gym_participants:
                        gym_participants[city_key] = {}
                    gym_name = row['gym_name']
                    gym_participants[city_key][gym_name] = gym_participants[city_key].get(gym_name, 0) + row['cnt']

                known_gyms = set(g[0] for g in GYMS_SPB + GYMS_MSK)

                for user in users:
                    user_id = user['user_id']

                    if user_id in sent_today:
                        continue

                    try:
                        city = user['city']
                        lang = user['language'] or 'ru'

                        tz_name = CITY_TIMEZONES.get(city, 'Europe/Moscow')
                        tz = pytz.timezone(tz_name)
                        local_now = datetime.now(tz)

                        if local_now.hour != 17 or local_now.minute >= 5:
                            continue

                        if "Петербург" in city or "Petersburg" in city:
                            city_key = "spb"
                        elif "Москва" in city or "Moscow" in city:
                            city_key = "msk"
                        else:
                            continue

                        city_gym_stats = gym_participants.get(city_key, {})

                        # Если никого нет — отправляем только в понедельник
                        if not city_gym_stats:
                            if local_now.weekday() != 0:  # 0 = понедельник
                                continue

                            text = TEXT2[lang].get("daily_push_empty_monday", 
                                "🧗 Новая неделя — отличное время найти напарника!\n\nСоздай тренировку первым:")
                            keyboard = InlineKeyboardMarkup([[
                                InlineKeyboardButton(TEXTS[lang]["board_create"], callback_data="menu_board")
                            ]])
                        else:
                            # Есть участники — формируем список
                            lines = [TEXT2[lang].get("daily_push_header", "🧗 Сегодня тренируются в твоём городе:"), ""]

                            sorted_gyms = sorted(city_gym_stats.items(), key=lambda x: x[1], reverse=True)

                            other_count = 0
                            for gym_name, count in sorted_gyms:
                                if gym_name in known_gyms:
                                    lines.append(f"🔥 {gym_name} — {count} чел.")
                                else:
                                    other_count += count

                            if other_count > 0:
                                lines.append(f"📍 Другая локация — {other_count} чел.")

                            lines.append("")
                            lines.append(TEXT2[lang].get("daily_push_cta", "Присоединяйся!"))

                            text = "\n".join(lines)
                            keyboard = InlineKeyboardMarkup([[
                                InlineKeyboardButton(TEXTS[lang]["menu_board"], callback_data="menu_board")
                            ]])

                        await application.bot.send_message(
                            chat_id=user_id,
                            text=text,
                            reply_markup=keyboard
                        )
                        sent_today.add(user_id)

                    except Exception as e:
                        if "bot was blocked" not in str(e).lower():
                            print(f"⚠️ Daily push error for {user_id}: {e}")

            await asyncio.sleep(300)

        except Exception as e:
            print(f"⚠️ Ошибка meetups_send_daily_push: {e}")
            await asyncio.sleep(60)

async def post_init(app: Application):
    # Инициализируем async DB pool
    await init_db_pool()

    # Создаём индексы для оптимизации (безопасно - IF NOT EXISTS)
    async with db_pool.acquire() as conn:
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_likes_to_user ON likes(to_user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_likes_from_user ON likes(from_user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_likes_both ON likes(from_user_id, to_user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_chats_both ON user_chats(user_id, partner_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_board_posts_date ON board_posts(date, time)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_city ON users(city)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_search_filters_user ON search_filters(user_id)")
        print("✅ Database indexes created/verified")

    # Запускаем фоновые задачи
    loop = asyncio.get_running_loop()
    loop.create_task(auto_expire_board_posts())
    loop.create_task(cleanup_pending_like_pushes())
    loop.create_task(meetups_auto_create_sessions())
    loop.create_task(meetups_auto_expire_sessions())
    loop.create_task(meetups_send_daily_push())

# Создаём Application (асинхронный клиент)
# Настройки HTTPXRequest для стабильной работы с сетевыми ошибками
tg_request = HTTPXRequest(
    connection_pool_size=10,  # Уменьшено для экономии памяти
    connect_timeout=30.0,     # Увеличенный таймаут подключения
    read_timeout=30.0,        # Увеличенный таймаут чтения
    write_timeout=30.0,       # Увеличенный таймаут записи
    pool_timeout=10.0         # Таймаут получения соединения из пула
)
application = Application.builder().token(BOT_TOKEN).request(tg_request).post_init(post_init).build()

# === DB init ===
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ Переменная окружения DATABASE_URL не установлена!")

# Async connection pool (10тыс пользователей)
db_pool = None

async def init_db_pool():
    """Создаёт async connection pool для asyncpg"""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        print("✅ Async DB pool initialized (2-10 connections)")

        # 🔥 ПРОГРЕВ ПУЛА: создаём все TLS-соединения заранее
        async def warmup_connection():
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

        await asyncio.gather(*[warmup_connection() for _ in range(2)])
        print("✅ DB pool warmed up (2 connections ready)")
    return db_pool

async def close_db_pool():
    """Закрывает connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        print("✅ DB pool closed")

# === Sync connection для database initialization ===
# Используется ТОЛЬКО для create_tables() и migrations при старте
# Все handlers используют async pool!

init_conn = None
init_cursor = None

def db_init_connect():
    """Sync connection ТОЛЬКО для database init code при старте"""
    global init_conn, init_cursor
    init_conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    init_conn.autocommit = True
    init_cursor = init_conn.cursor()
    print("✅ Init DB connection established (sync, for startup only)")

# Алиасы для обратной совместимости с create_tables()
conn = None
cursor = None

def prepare_db_init():
    """Подготавливает sync connection для database init"""
    global conn, cursor
    db_init_connect()
    conn = init_conn
    cursor = init_cursor

# === /DB init ===



# 🔐 Список ID администраторов
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

DEBUG_MODE = os.getenv(
    "DEBUG_MODE",
    "false").lower() == "true"  # <-- Включи отладку при необходимости

PLACEHOLDER_URLS = {
    "male": [
        "https://i.postimg.cc/2yrLtC3X/Picture1-jpg.png",
        "https://i.postimg.cc/sDpsX56S/Picture4-jpg.png"
    ],
    "female": [
        "https://i.postimg.cc/CK2WJKrS/Picture2-jpg.png",
        "https://i.postimg.cc/QtLfHKn9/Picture3-jpg.png"
    ],
    "other": [
        "https://i.postimg.cc/Xq1FBT7H/Picture5-jpg.png"
    ]
}

# ✅ Известные размеры заглушек (определены из production БД)
# Фото с этими размерами - заглушки, has_real_photo должен быть FALSE
PLACEHOLDER_SIZES = {230154, 243315, 241434, 223273, 239872}

DIFFICULTY_PAGES = [
    ["3", "4", "5A", "5B", "5C", "5C+"],                  # страница 1
    ["6A", "6A+", "6B", "6B+", "6C", "6C+"],              # страница 2
    ["7A", "7A+", "7B", "7B+", "7C", "7C+"],              # страница 3
    ["8A", "8A+", "8B", "8B+", "8C", "8C+"],              # страница 4
    ["9A", "9A+", "9B", "9B+", "9C"]                      # страница 5
]

# ===== Difficulty utils (registration/edit) =====
# Плоский список всех градаций из ваших страниц
ALL_DIFFICULTIES = [g for page in DIFFICULTY_PAGES for g in page]

def get_difficulty_value_label(value: str | None, lang: str) -> str:
    # Показ в карточках профиля: конкретный грейд или "не указано"
    return value if value else TEXT2[lang]["not_specified"]

def get_difficulty_keyboard(page: int = 0, per_page: int = 12, lang: str = "ru", prefix: str = "diffval_"):
    """
    Пагинация строго по DIFFICULTY_PAGES (5 страниц).
    Кнопки раскладываются по 2 в ряд.
    """
    total_pages = len(DIFFICULTY_PAGES)
    page = max(0, min(page, total_pages - 1))

    items = DIFFICULTY_PAGES[page]

    keyboard = []
    # по 2 кнопки в строке
    for i in range(0, len(items), 2):
        row = items[i:i+2]
        keyboard.append([
            InlineKeyboardButton(lbl, callback_data=f"{prefix}{lbl}")
            for lbl in row
        ])

    # навигация (показываем всегда там, где есть куда листать)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_back"], callback_data=f"{prefix}page_{page-1}")
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_next"], callback_data=f"{prefix}page_{page+1}")
        )
    if nav_buttons:
        keyboard.append(nav_buttons)

    # кнопка Пропустить
    keyboard.append([InlineKeyboardButton(TEXT2[lang]["btn_skip"], callback_data=f"{prefix}skip")])
    return InlineKeyboardMarkup(keyboard)


# ===== Difficulty range keyboard (for filters menu) =====
DIFFICULTY_RANGES = [
    ("3_5Cplus",   "3–5C+"),
    ("6A_6Cplus",  "6A–6C+"),
    ("7A_7Cplus",  "7A–7C+"),
    ("8A_8Cplus",  "8A–8C+"),
    ("9A_9Cplus",  "9A–9C+"),
]

def get_board_difficulty_keyboard(page: int = 0, per_page: int = 12, lang: str = "ru", prefix: str = "boarddiff_"):
    """
    Клавиатура уровней С ПАГИНАЦИЕЙ для ОБЪЯВЛЕНИЙ.
    Такое же наполнение, как get_difficulty_keyboard, но:
    - свой prefix (boarddiff_)
    - вместо 'Пропустить' — кнопка 'Любой'
    """
    total_pages = len(DIFFICULTY_PAGES)
    page = max(0, min(page, total_pages - 1))

    items = DIFFICULTY_PAGES[page]

    keyboard = []
    # по 2 кнопки в строке
    for i in range(0, len(items), 2):
        row = items[i:i+2]
        keyboard.append([
            InlineKeyboardButton(lbl, callback_data=f"{prefix}{lbl}")
            for lbl in row
        ])

    # навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_back"], callback_data=f"{prefix}page_{page-1}")
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_next"], callback_data=f"{prefix}page_{page+1}")
        )
    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)


def get_difficulty_range_keyboard(lang: str = "ru", prefix: str = "diffrange_"):
    rows = []
    for code, label in DIFFICULTY_RANGES:
        rows.append([InlineKeyboardButton(label, callback_data=f"{prefix}{code}")])
    # Кнопка "Пропустить"
    rows.append([InlineKeyboardButton(TEXT2[lang]["btn_skip"], callback_data=f"{prefix}skip")])
    return InlineKeyboardMarkup(rows)
# ===== /Difficulty range keyboard =====

# ===== /Difficulty utils =====
# ---- Difficulty search buckets (для фильтра поиска) ----
DIFFICULTY_BUCKETS = {
    "3_5Cplus": ["3", "4", "5A", "5B", "5C", "5C+"],
    "6A_6Cplus": ["6A", "6A+", "6B", "6B+", "6C", "6C+"],
    "7A_7Cplus": ["7A", "7A+", "7B", "7B+", "7C", "7C+"],
    "8A_8Cplus": ["8A", "8A+", "8B", "8B+", "8C", "8C+"],
    "9A_9Cplus": ["9A", "9A+", "9B", "9B+", "9C", "9C+"],
}

DIFFICULTY_BUCKET_LABELS = {
    "3_5Cplus": "3–5C+",
    "6A_6Cplus": "6A–6C+",
    "7A_7Cplus": "7A–7C+",
    "8A_8Cplus": "8A–8C+",
    "9A_9Cplus": "9A–9C+",
    "any": "Any",
    None: "Any",
}

# ===== ЗАЛЫ ДЛЯ ВСТРЕЧ (gym_sessions) =====
GYMS_SPB = [
    ("СС Петр.", "both"),
    ("Атом", "bouldering"),
    ("СС Бух.", "both"),
    ("Неолит", "bouldering"),
    ("Энергия выс.", "both"),
    ("Igels", "both"),
    ("El Capitan", "both"),
    ("Трамонтана", "both"),
    ("Луч", "bouldering"),
    ("Climb Art", "bouldering"),
    ("Ориентир", "both"),
    ("Жесть", "both"),
    ]

GYMS_MSK = [
    ("Limestone", "both"),
    ("Скала Сити", "both"),
    ("BigWall", "both"),
    ("Атмосфера", "bouldering"),
    ("RockZona", "bouldering"),
    ("Старая Школа", "both"),
    ("Climb Lab", "bouldering"),
    ("ЦСКА", "both"),
    ("RedPoint", "both"),
    ("Tengu's", "bouldering"),
    ("Sport Station", "both"),
]

def format_gym_name(gym_tuple):
    """Возвращает название зала (первый элемент кортежа)"""
    return gym_tuple[0] if gym_tuple else ""

def get_gym_climb_type(gym_name: str) -> str:
    """Возвращает climb_type зала: 'bouldering' или 'both'"""
    for gym in GYMS_SPB + GYMS_MSK:
        if gym[0] == gym_name:
            return gym[1] if len(gym) > 1 else "both"
    return "both"  # По умолчанию — оба типа

CITY_GYMS = {
    "spb": [{"id": f"spb_{i}", "name": format_gym_name(g)} for i, g in enumerate(GYMS_SPB)],
    "msk": [{"id": f"msk_{i}", "name": format_gym_name(g)} for i, g in enumerate(GYMS_MSK)],
}

# Timezone для городов (для пушей в 17:00 по местному времени)
CITY_TIMEZONES = {
    "Санкт-Петербург": "Europe/Moscow",
    "Saint Petersburg": "Europe/Moscow",
    "Москва": "Europe/Moscow",
    "Moscow": "Europe/Moscow",
    "Новосибирск": "Asia/Novosibirsk",
    "Novosibirsk": "Asia/Novosibirsk",
    "Екатеринбург": "Asia/Yekaterinburg",
    "Yekaterinburg": "Asia/Yekaterinburg",
    "Иркутск": "Asia/Irkutsk",
    "Irkutsk": "Asia/Irkutsk",
    "Владивосток": "Asia/Vladivostok",
    "Vladivostok": "Asia/Vladivostok",
    "Красноярск": "Asia/Krasnoyarsk",
    "Krasnoyarsk": "Asia/Krasnoyarsk",
    "Калининград": "Europe/Kaliningrad",
    "Kaliningrad": "Europe/Kaliningrad",
    # Европейские города
    "Berlin": "Europe/Berlin",
    "Munich": "Europe/Berlin",
    "Madrid": "Europe/Madrid",
    "Barcelona": "Europe/Madrid",
    "Paris": "Europe/Paris",
    "London": "Europe/London",
    "Vienna": "Europe/Vienna",
    "Zurich": "Europe/Zurich",
    "Prague": "Europe/Prague",
    # Дефолт
    "_default": "Europe/Moscow",
}

def get_timezone_for_city(city: str) -> str:
    """Возвращает timezone для города"""
    return CITY_TIMEZONES.get(city, CITY_TIMEZONES["_default"])

# ===== Like Push Notification System =====
# Словарь для хранения отложенных пушей: ключ = (from_user_id, to_user_id), значение = asyncio.Task
pending_like_pushes = {}

async def send_delayed_like_push(from_user_id: int, to_user_id: int):
    """Отправляет пуш-уведомление о лайке через 60 секунд после лайка"""
    try:
        # Ждём 60 секунд
        await asyncio.sleep(60)

        async with db_pool.acquire() as conn:
            # Проверяем, что лайк всё ещё существует
            row = await conn.fetchrow(
                "SELECT 1 FROM likes WHERE from_user_id = $1 AND to_user_id = $2",
                from_user_id, to_user_id
            )
            if not row:
                # Лайк был убран за эту минуту, не отправляем пуш
                return

            # Проверяем, не отправляли ли уже пуш от from_user_id к to_user_id сегодня
            row = await conn.fetchrow("""
                SELECT 1 FROM like_push_log
                WHERE from_user_id = $1 AND to_user_id = $2
                  AND push_date = CURRENT_DATE
            """, from_user_id, to_user_id)

            if row:
                # Уже отправляли пуш сегодня, не спамим
                return

            # Получаем язык получателя
            row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", to_user_id)
            lang = row['language'] if row and row['language'] else "ru"

        # Создаём инлайн-кнопку для перехода в меню "Кто меня лайкнул"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                INLINE_TEXTS[lang]["btn_view_liked_me"],
                callback_data="view_liked_me"
            )
        ]])

        # Отправляем пуш-уведомление
        try:
            await application.bot.send_message(
                chat_id=to_user_id,
                text=TEXT2[lang]["like_push_notification"],
                reply_markup=keyboard
            )

            # Логируем отправку пуша
            async with db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO like_push_log (from_user_id, to_user_id, push_date)
                    VALUES ($1, $2, CURRENT_DATE)
                """, from_user_id, to_user_id)
        except Exception as e:
            print(f"⚠️ Ошибка отправки like push to {to_user_id}: {e}")

    except asyncio.CancelledError:
        # Задача была отменена (разлайк), это нормально
        pass
    finally:
        # Удаляем задачу из словаря pending_like_pushes
        key = (from_user_id, to_user_id)
        if key in pending_like_pushes:
            del pending_like_pushes[key]
# ===== /Like Push Notification System =====

def get_bucket_label_md(bucket_code: str, lang: str) -> str:
    """Текст для сводки фильтров (MarkdownV2-безопасный, экранируем + и -)."""
    raw = DIFFICULTY_BUCKET_LABELS.get(bucket_code, DIFFICULTY_BUCKET_LABELS["any"])
    return escape_markdown(raw)

def get_grades_for_bucket(bucket_code: str) -> list[str]:
    """Список конкретных градаций для выбранного диапазона (поиск по users.difficulty)."""
    return DIFFICULTY_BUCKETS.get(bucket_code, [])

async def get_search_filters_row(user_id: int) -> dict:
    """
    Читаем строку фильтров пользователя из БД и возвращаем dict с дефолтами.
    Поддерживает расширенную схему: has_photo, status_slug, city_override, sort_popular.

    ВАЖНО:
    - has_photo и sort_popular могут быть True / False / None (tri-state).
      None = "Всех / Любые".
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT difficulty, climb_type, gender, weight_min, weight_max,
                   has_photo, status_slug, city_override, sort_popular
            FROM search_filters
            WHERE user_id = $1
        """, user_id)
        if not row:
            return {
                "difficulty": None,
                "climb_type": "any",
                "gender": "any",
                "weight_min": None,
                "weight_max": None,
                # по умолчанию — "Любые", поэтому None
                "has_photo": None,
                "status_slug": None,
                "city_override": None,
                "sort_popular": None,
            }

        return {
            "difficulty": row['difficulty'],
            "climb_type": (row['climb_type'] or "any"),
            "gender": (row['gender'] or "any"),
            "weight_min": row['weight_min'],
            "weight_max": row['weight_max'],
            # НЕ оборачиваем в bool(), оставляем как есть: True / False / None
            "has_photo": row['has_photo'],
            "status_slug": row['status_slug'],
            "city_override": row['city_override'],
            # тоже без bool(), оставляем tri-state
            "sort_popular": row['sort_popular'],
        }

async def upsert_search_filters(user_id: int, **patch):
    """
    Обновляем строку фильтров: берём текущее значение из БД, применяем patch и UPSERT.
    - Преобразует строки 'any', 'null', 'none', '' в None (NULL в БД)
    - Для булевых полей принимает True/False/None и строки 'true'/'false'
    """
    f = await get_search_filters_row(user_id)
    f.update(patch)

    # --- нормализация входных значений ---
    def normalize_value(v):
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("any", "none", "null", ""):
                return None
            if s in ("true", "yes", "1"):
                return True
            if s in ("false", "no", "0"):
                return False
        return v

    # нормализуем только булевые премиум-поля (их часто нужно обнулять до NULL)
    f["has_photo"] = normalize_value(f.get("has_photo"))
    f["sort_popular"] = normalize_value(f.get("sort_popular"))

    # --- выполнение UPSERT ---
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO search_filters (
                user_id, difficulty, climb_type, gender,
                weight_min, weight_max, has_photo, status_slug,
                city_override, sort_popular
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
            ON CONFLICT (user_id) DO UPDATE SET
                difficulty    = EXCLUDED.difficulty,
                climb_type    = EXCLUDED.climb_type,
                gender        = EXCLUDED.gender,
                weight_min    = EXCLUDED.weight_min,
                weight_max    = EXCLUDED.weight_max,
                has_photo     = EXCLUDED.has_photo,
                status_slug   = EXCLUDED.status_slug,
                city_override = EXCLUDED.city_override,
                sort_popular  = EXCLUDED.sort_popular
        """, user_id, f.get("difficulty"), f.get("climb_type"), f.get("gender"),
            f.get("weight_min"), f.get("weight_max"), f.get("has_photo"),
            f.get("status_slug"), f.get("city_override"), f.get("sort_popular"))



######################################################################
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id

        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO registration_times (user_id, start_time) VALUES ($1, NOW()) ON CONFLICT DO NOTHING",
                user_id)

            await conn.execute(
                "INSERT INTO user_logins (user_id, login_date) VALUES ($1, CURRENT_DATE)",
                user_id)

            # ✅ Обработка реферальной ссылки — начисление только 1 раз
            if context.args and context.args[0].startswith("ref"):
                try:
                    inviter_id = int(context.args[0].replace("ref", ""))
                    if inviter_id != user_id:
                        row = await conn.fetchrow("SELECT invited_by FROM users WHERE user_id = $1", user_id)
                        if not row or row['invited_by'] is None:
                            await conn.execute("UPDATE users SET invited_by = $1 WHERE user_id = $2",
                                inviter_id, user_id)
                            print(f"🎁 Новый пользователь {user_id} пришёл по реферальной ссылке от {inviter_id}")
                            context.user_data["invited_by"] = inviter_id
                        else:
                            print(f"ℹ️ Пользователь {user_id} уже был приглашён ранее — бонус не начисляем повторно.")
                except ValueError:
                    print("❌ Некорректный ref параметр")

        # Выбор языка
        keyboard = [[
            InlineKeyboardButton("🇬🇧", callback_data='lang_en'),
            InlineKeyboardButton("🇷🇺", callback_data='lang_ru'),
            InlineKeyboardButton("🇪🇸", callback_data="lang_es"),
            InlineKeyboardButton("🇩🇪", callback_data='lang_de'),
        ]]

        await update.message.reply_text(
            "🌍 Please choose your language:",
            reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print("❌ Ошибка в start:", e)


async def lang_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.split("_")[1]

    context.user_data["lang"] = lang
    user_sessions.setdefault(user_id, {})["lang"] = lang

    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET language = $1 WHERE user_id = $2", lang, user_id)

        context.user_data["awaiting_consent"] = True

        if lang not in TEXT2:
            await query.message.reply_text("🌍 Interface for this language is coming very soon.")
            return

        user_count = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_deleted = FALSE AND name IS NOT NULL AND name != ''")

    welcome_text = (f"{TEXT2[lang]['welcome_intro']}\n\n"
                    f"{TEXT2[lang]['welcome_subtitle']}\n\n"
                    f"*{user_count}* {TEXT2[lang]['welcome_subtitle2']}")

    photo_url = "https://postimg.cc/Jy24yJKh"

    await query.message.reply_photo(photo=photo_url,
                                    caption=welcome_text,
                                    parse_mode="Markdown")

    await asyncio.sleep(1.5)

    agreement_text = TEXT2[lang]["consent_intro"]

    buttons = [[
        InlineKeyboardButton(TEXT2[lang]["btn_rules"],
                             callback_data="show_user_agreement")
    ],
               [
                   InlineKeyboardButton(TEXT2[lang]["btn_agree"],
                                        callback_data="consent_agree")
               ],
               [
                   InlineKeyboardButton(TEXT2[lang]["btn_decline"],
                                        callback_data="consent_decline")
               ]]

    await query.message.reply_text(agreement_text,
                                   parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(buttons))

async def assign_placeholders_to_all_users_missing_photos():
    print("🚀 Запуск assign_placeholders_to_all_users_missing_photos()")

    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT user_id, gender FROM users WHERE photo_bytes IS NULL")
    print(f"👥 Найдено пользователей без фото: {len(users)}")

    from random import choice

    for user_row in users:
        user_id, gender = user_row['user_id'], user_row['gender']
        gender = gender or "other"
        selected_url = choice(PLACEHOLDER_URLS.get(gender, PLACEHOLDER_URLS["other"]))
        print(f"➡️ Обрабатываю user_id={user_id}, пол={gender}, URL={selected_url}")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(selected_url, headers={"User-Agent": "Mozilla/5.0"})
            print(f"🌐 Статус ответа: {response.status_code}, размер: {len(response.content)} байт")

            if response.status_code == 200 and len(response.content) > 1000:
                async with db_pool.acquire() as conn:
                    await conn.execute(
                        "UPDATE users SET photo_bytes = $1, has_real_photo = FALSE WHERE user_id = $2",
                        response.content, user_id
                    )
                print(f"✅ Заглушка поставлена для {user_id}")
            else:
                print(f"⚠️ Некорректный ответ или пустое изображение для {user_id}")

        except Exception as e:
            print(f"❌ Ошибка при обработке {user_id}: {e}")

    print("✅ Все заглушки загружены и сохранены.")


def escape_markdown(text: str) -> str:
    return tg_escape_markdown(text, version=2)

# --- Унифицированные лейблы для карточек (уровень + вес) ---
def get_difficulty_label(value: str | None, lang: str) -> str:
    """Отдаёт текст уровня: поддерживает старые коды ('beginner'/'advanced'/'pro')
    и новые грейды ('6B+'). Без экранирования."""
    if not value:
        return TEXT2[lang]["not_specified"]
    return DIFFICULTY_LABELS.get(value, value)

def display_difficulty_md(value: str | None, lang: str) -> str:
    """Готовый к выводу в MARKDOWN_V2 уровень (с экранированием)."""
    return escape_markdown(get_difficulty_label(value, lang))

def display_weight_md(value: str | None, lang: str) -> str:
    """Готовый к выводу в MARKDOWN_V2 вес (с экранированием)."""
    raw = get_weight_label(value, lang) if value else TEXT2[lang]["not_specified"]
    return escape_markdown(raw)


def get_climb_type_label(code, lang):
    if not code or code == "None":
        return TEXT2[lang]["not_specified"]
    return TEXT2[lang].get(f"climb_{code}", TEXT2[lang]["not_specified"])


def get_gender_label(code, lang):
    if not code or code == "None":
        return TEXT2[lang]["not_specified"]
    return TEXT2[lang].get(f"gender_{code}", TEXT2[lang]["not_specified"])


async def ensure_lang(context, user_id):
    """Async version - гарантирует что у пользователя установлен язык"""
    if "lang" not in context.user_data:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
            context.user_data["lang"] = row['language'] if row and row['language'] else "ru"


def get_country_keyboard(context, page=0, per_page=6, prefix="country_", show_custom=True):
    raw_countries = [
        "🇦🇷 Argentina", "🇦🇲 Armenia", "🇦🇺 Australia", "🇦🇹 Austria", "🇧🇾 Belarus", "🇧🇪 Belgium",
        "🇧🇷 Brazil", "🇨🇦 Canada", "🇨🇱 Chile", "🇨🇳 China", "🇨🇴 Colombia",
        "🇨🇿 Czech Republic", "🇩🇰 Denmark", "🇫🇮 Finland", "🇫🇷 France",
        "🇩🇪 Germany", "🇬🇷 Greece", "🇬🇪 Georgia", "🇭🇰 Hong Kong", "🇮🇳 India",
        "🇮🇩 Indonesia", "🇮🇷 Iran", "🇮🇪 Ireland", "🇮🇱 Israel", "🇮🇹 Italy",
        "🇯🇵 Japan", "🇰🇿 Kazakhstan", "🇲🇾 Malaysia", "🇲🇽 Mexico",
        "🇳🇱 Netherlands", "🇳🇿 New Zealand", "🇳🇴 Norway", "🇵🇪 Peru",
        "🇵🇭 Philippines", "🇵🇱 Poland", "🇵🇹 Portugal", "🇷🇺 Russia", "🇷🇸 Serbia",
        "🇸🇬 Singapore", "🇸🇰 Slovakia", "🇸🇮 Slovenia", "🇿🇦 South Africa",
        "🇰🇷 South Korea", "🇪🇸 Spain", "🇸🇪 Sweden", "🇨🇭 Switzerland",
        "🇹🇼 Taiwan", "🇹🇭 Thailand", "🇹🇷 Turkey", "🇦🇪 UAE", "🇺🇸 USA",
        "🇺🇦 Ukraine", "🇬🇧 United Kingdom", "🌍 Other"
    ]

    lang = context.user_data.get("lang", "ru")
    russia = "🇷🇺 Russia"
    other = "🌍 Other"

    keyboard = []
    nav_buttons = []

    # Для пагинации используем соответствующий префикс
    if prefix == "country_":
        page_prefix = "country_page_"
    elif prefix.endswith("_"):
        page_prefix = prefix[:-1] + "_page_"
    else:
        page_prefix = prefix + "_page_"

    if lang == "ru":
        # Выделим список без России и Other
        middle = sorted([c for c in raw_countries if c not in [russia, other]],
                        key=lambda c: c.split(" ", 1)[1])
        total_pages = ((len(middle) - 1) // per_page) + 1

        if page == 0:
            # Стартовая страница: только Россия
            keyboard = [[
                InlineKeyboardButton(russia, callback_data=f"{prefix}{russia}")
            ]]
            nav_buttons.append(
                InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_next"],
                                     callback_data=f"{page_prefix}1"))
        else:
            start = (page - 1) * per_page
            end = start + per_page
            countries = middle[start:end]
            keyboard = [[
                InlineKeyboardButton(c, callback_data=f"{prefix}{c}")
            ] for c in countries]

            if page > 1:
                nav_buttons.append(
                    InlineKeyboardButton(
                        INLINE_TEXTS[lang]["btn_city_back"],
                        callback_data=f"{page_prefix}{page - 1}"))
            else:
                nav_buttons.append(
                    InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_back"],
                                         callback_data=f"{page_prefix}0"))
            if end < len(middle):
                nav_buttons.append(
                    InlineKeyboardButton(
                        INLINE_TEXTS[lang]["btn_city_next"],
                        callback_data=f"{page_prefix}{page + 1}"))

        # "Other" — только на последней странице (если разрешено)
        if page == total_pages and show_custom:
            keyboard.append([
                InlineKeyboardButton(other, callback_data=f"{prefix}{other}")
            ])

    else:
        # Языки кроме "ru": обычная пагинация со всеми странами, включая Россию
        full = sorted([c for c in raw_countries if c != other],
                      key=lambda c: c.split(" ", 1)[1])
        start = page * per_page
        end = start + per_page
        countries = full[start:end]
        total_pages = (len(full) - 1) // per_page + 1

        keyboard = [[InlineKeyboardButton(c, callback_data=f"{prefix}{c}")]
                    for c in countries]

        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_back"],
                                     callback_data=f"{page_prefix}{page - 1}"))
        if end < len(full):
            nav_buttons.append(
                InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_next"],
                                     callback_data=f"{page_prefix}{page + 1}"))

        if end >= len(full) and show_custom:
            keyboard.append([
                InlineKeyboardButton(other, callback_data=f"{prefix}{other}")
            ])

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)


def get_city_keyboard(context, country, page=0, per_page=6, prefix="city_", show_custom=True):
    cities_by_country = {
        "🇦🇷 Argentina": [
            "Buenos Aires", "Córdoba", "La Plata", "Mendoza", "Patagonia",
            "Sierra"
        ],
        "🇦🇲 Armenia": ["Yerevan", "Gyumri", "Vanadzor"],
        "🇦🇺 Australia":
        ["Adelaide", "Brisbane", "Melbourne", "Perth", "Sydney"],
        "🇦🇹 Austria": [
            "Bregenz", "Dornbirn", "Graz", "Innsbruck", "Klagenfurt", "Leoben",
            "Linz", "Salzburg", "Seefeld", "St. Pölten", "Tirol", "Villach",
            "Wattens", "Wels", "Vienna"
        ],
        "🇧🇾 Belarus": [
            "Minsk",
            "Gomel",
            "Vitebsk",
            "Grodno",
            "Brest",
            "Mogilev",
            "Baranovichi",
            "Bobruisk",
            "Lida",
            "Novopolotsk"
        ],
        "🇧🇪 Belgium": [
            "Anderlecht", "Auderghem", "Brussels", "Forest", "Ixelles",
            "Meiser", "Molenbeek-Saint-Jean", "Woluwe-Saint-Lambert"
        ],
        "🇧🇷 Brazil": [
            "Belo Horizonte", "Brasília", "Curitiba", "Rio de Janeiro",
            "São Paulo"
        ],
        "🇨🇦 Canada": [
            "Calgary", "Edmonton", "Hamilton", "Montreal", "Ottawa",
            "Quebec City", "Toronto", "Vancouver", "Victoria", "Winnipeg"
        ],
        "🇨🇱 Chile": ["Concepción", "Santiago", "Valparaíso"],
        "🇨🇳 China": [
            "Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Chengdu",
            "Nanjing", "Hangzhou", "Wuhan", "Xi’an", "Tianjin", "Chongqing",
            "Dongguan", "Suzhou", "Harbin", "Qingdao"
        ],
        "🇨🇴 Colombia": ["Bogotá", "Cali", "Medellín"],
        "🇨🇿 Czech Republic": ["Brno", "Liberec", "Ostrava", "Plzeň", "Prague"],
        "🇩🇰 Denmark": ["Copenhagen", "Aarhus", "Odense"],
        "🇫🇮 Finland": ["Helsinki", "Tampere", "Espoo"],
        "🇫🇷 France": [
            "Paris", "Lyon", "Marseille", "Toulouse", "Grenoble", "Lille",
            "Bordeaux", "Nice", "Nantes", "Strasbourg", "Montpellier",
            "Rennes", "Dijon", "Toulon", "Le Havre", "Chamonix"
        ],
        "🇩🇪 Germany": [
            "Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt am Main",
            "Nuremberg", "Bremen", "Stuttgart", "Düsseldorf", "Leipzig",
            "Dresden", "Hanover", "Essen", "Dortmund", "Bonn"
        ],
        "🇬🇷 Greece": ["Athens", "Patras", "Thessaloniki"],
        "🇬🇪 Georgia": ["Tbilisi", "Batumi", "Kutaisi", "Rustavi", "Zugdidi"],
        "🇭🇰 Hong Kong": ["Hong Kong (SAR China)"],
        "🇮🇳 India": ["Bangalore", "Delhi", "Mumbai", "Hyderabad"],
        "🇮🇩 Indonesia": ["Bandung", "Jakarta"],
        "🇮🇷 Iran": ["Mashhad", "Shiraz", "Tehran"],
        "🇮🇪 Ireland": ["Cork", "Dublin", "Galway"],
        "🇮🇱 Israel": ["Eilat", "Haifa", "Jerusalem", "Tel Aviv"],
        "🇮🇹 Italy": [
            "Bari", "Bologna", "Cagliari", "Catania", "Florence", "Genoa",
            "Milan", "Naples", "Padua", "Palermo", "Rome", "Turin", "Trento",
            "Udine", "Verona"
        ],
        "🇯🇵 Japan": [
            "Tokyo", "Osaka", "Yokohama", "Nagoya", "Fukuoka", "Sapporo",
            "Kyoto", "Kobe", "Hiroshima", "Sendai"
        ],
        "🇰🇿 Kazakhstan":
        ["Almaty", "Astana", "Karaganda", "Pavlodar", "Shymkent"],
        "🇲🇾 Malaysia": ["George Town", "Kuala Lumpur"],
        "🇲🇽 Mexico":
        ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Toluca"],
        "🇳🇱 Netherlands": [
            "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven",
            "Groningen", "Nijmegen", "Haarlem", "Maastricht", "Arnhem",
            "Delft", "Leiden", "Zwolle", "Amersfoort", "Almere"
        ],
        "🇳🇿 New Zealand": ["Auckland", "Christchurch", "Wellington"],
        "🇳🇴 Norway": ["Oslo", "Bergen", "Stavanger", "Trondheim", "Drammen"],
        "🇵🇪 Peru": ["Cusco", "Lima"],
        "🇵🇭 Philippines": ["Cebu City", "Manila"],
        "🇵🇱 Poland": [
            "Bydgoszcz", "Gdańsk", "Katowice", "Kraków", "Lublin", "Łódź",
            "Poznań", "Szczecin", "Warsaw", "Wrocław"
        ],
        "🇵🇹 Portugal": ["Lisbon", "Porto"],
        "🇷🇺 Russia": [
            "Moscow",
            "Saint Petersburg",
            "Alushta",
            "Bakhchisaray",
            "Chelyabinsk",
            "Chita",
            "Elets",
            "Foros",
            "Irkutsk",
            "Kaliningrad",
            "Kamenomostsky",
            "Kazan",
            "Kemerovo",
            "Kislovodsk",
            "Krasnodar",
            "Krasnoyarsk",
            "Nizhny Novgorod",
            "Novosibirsk",
            "Perm",
            "Pyatigorsk",
            "Rostov-on-Don",
            "Samara",
            "Sevastopol",
            "Simeiz",
            "Simferopol",
            "Sochi",
            "Sterlitamak",
            "Sudak",
            "Tolyatti",
            "Tyrnyauz",
            "Ufa",
            "Vladikavkaz",
            "Yalta",
            "Yekaterinburg",
            "Yessentuki",
            "Zheleznovodsk"
        ],
        "🇷🇸 Serbia": ["Belgrade", "Novi Sad"],
        "🇸🇬 Singapore": ["Singapore"],
        "🇸🇰 Slovakia": ["Bratislava", "Košice"],
        "🇸🇮 Slovenia": ["Ljubljana", "Maribor"],
        "🇿🇦 South Africa": ["Cape Town", "Durban", "Johannesburg"],
        "🇰🇷 South Korea": [
            "Busan", "Cheonan", "Daegu", "Daejeon", "Gangneung", "Gwangju",
            "Incheon", "Seoul", "Suwon", "Ulsan"
        ],
        "🇪🇸 Spain": [
            "Alicante", "Barcelona", "Bilbao", "San Sebastián", "Gran Canaria",
            "Granada", "Madrid", "Málaga", "Murcia", "Oviedo",
            "Palma de Mallorca", "Seville", "Valencia", "Valladolid",
            "Zaragoza"
        ],
        "🇸🇪 Sweden": ["Gothenburg", "Malmö", "Stockholm"],
        "🇨🇭 Switzerland": [
            "Basel", "Bern", "Biel", "Geneva", "Lausanne", "Lugano", "Lucerne",
            "St. Gallen", "Winterthur", "Zurich"
        ],
        "🇹🇼 Taiwan": ["Kaohsiung", "Taipei", "Taichung"],
        "🇹🇭 Thailand": ["Bangkok", "Chiang Mai", "Phuket"],
        "🇹🇷 Turkey": [
            "Alanya",
            "Ankara",
            "Antalya",
            "Geyikbayırı",
            "Isparta",
            "Istanbul",
            "Izmir",
            "Kemer",
            "Mersin"
        ],
        "🇺🇦 Ukraine": ["Dnipro", "Kyiv", "Lviv", "Odesa", "Kharkiv"],
        "🇦🇪 United Arab Emirates": ["Abu Dhabi", "Dubai"],
        "🇬🇧 United Kingdom": [
            "Birmingham",  # England
            "Bristol",  # England
            "London",  # England
            "Manchester",  # England
            "Liverpool",  # England
            "Edinburgh",  # Scotland
            "Glasgow",  # Scotland
            "Cardiff",  # Wales
            "Swansea",  # Wales
            "Belfast",  # Northern Ireland (или оставить без флага)
        ],
        "🇺🇸 USA": [
            "Atlanta", "San Francisco", "Boston", "Chicago", "Dallas",
            "Denver", "Houston", "Los Angeles", "Miami", "Minneapolis",
            "New York City", "Phoenix", "Salt Lake City", "Seattle",
            "Washington, D.C."
        ],
        "🌍 Other": ["Other"]
    }

    cities = cities_by_country.get(country, ["Город по умолчанию"])
    total_pages = (len(cities) - 1) // per_page + 1
    start = page * per_page
    end = start + per_page

    # Для пагинации используем соответствующий префикс
    if prefix == "city_":
        page_prefix = "city_page_"
    elif prefix.endswith("_"):
        page_prefix = prefix[:-1] + "_page_"
    else:
        page_prefix = prefix + "_page_"

    keyboard = [[InlineKeyboardButton(city, callback_data=f"{prefix}{city}")]
                for city in cities[start:end]]

    lang = context.user_data.get("lang", "ru")
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_back"],
                                 callback_data=f"{page_prefix}{page - 1}"))
    if end < len(cities):
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_next"],
                                 callback_data=f"{page_prefix}{page + 1}"))
    if end >= len(cities) and show_custom:  # Только на последней странице (если разрешено)
        keyboard.append([
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_other"],
                                 callback_data=f"{prefix}custom" if prefix != "city_" else "city_custom")
        ])

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)

def render_status_line(lang: str, status_slug: str | None) -> str:
    if not status_slug:
        return ""
    opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
    label = opts_map.get(status_slug)
    return f"{label}\n" if label else ""


# ensure_db_alive() удалена - async pool управляет соединениями автоматически


async def check_user_reports_and_apply_sanctions(reported_id):
    now = datetime.now()

    # Фильтрация валидных жалоб
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ur.reason
            FROM user_reports ur
            JOIN users u ON ur.reporter_id = u.user_id
            WHERE ur.reported_id = $1
              AND ur.timestamp > $2
              AND (NOW() - u.registration_date) >= INTERVAL '1 day'
              AND (
                  SELECT COUNT(*) FROM user_reports
                  WHERE reporter_id = ur.reporter_id
                    AND timestamp >= NOW() - INTERVAL '1 day'
              ) <= 3
            """, reported_id, now - timedelta(days=30))
    valid_reasons = [row['reason'] for row in rows]

    reason_counts = Counter(valid_reasons)
    total_reports = sum(reason_counts.values())
    recent_reports = sum(1 for r in valid_reasons if r)

    serious_reasons = ["Оскорбления", "Спам", "Неприемлемое фото", "Реклама"]
    serious_count = sum(reason_counts.get(r, 0) for r in serious_reasons)

    async def set_hidden(user_id, until, level):
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO hidden_users (user_id, hidden_user_id, hide_until, notified)
                VALUES ($1, $2, $3, 0)
                ON CONFLICT (user_id, hidden_user_id) DO UPDATE
                SET hide_until = EXCLUDED.hide_until,
                    notified = EXCLUDED.notified
                """, user_id, reported_id, until)
        return level

    if total_reports >= 12:
        return await set_hidden(0, now + timedelta(days=365), "hard_ban")
    if serious_count >= 8 and recent_reports >= 8:
        return await set_hidden(0, now + timedelta(days=7), "ban")
    if total_reports >= 5:
        return await set_hidden(0, now + timedelta(days=3), "isolation")

    return None


def check_image_for_harm_base64(image_bytes):
    return True  # ⬅️ Заглушка, всегда пропускает фото

def get_weight_keyboard(page=0, per_page=10, lang="ru", prefix="weightval_"):
    min_weight = 40
    max_weight = 150
    all_weights = list(range(min_weight, max_weight + 1))
    total_pages = (len(all_weights) - 1) // per_page + 1  # (если используешь где-то)

    start = page * per_page
    end = start + per_page
    chunk = all_weights[start:end]

    # сетка весов: по 2 в ряд
    keyboard = [
        [
            InlineKeyboardButton(f"{w} {TEXT2[lang]['kg']}", callback_data=f"{prefix}{w}")
            for w in chunk[i:i + 2]
        ]
        for i in range(0, len(chunk), 2)
    ]

    # навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_back"], callback_data=f"{prefix}page_{page - 1}")
        )
    if end < len(all_weights):
        nav_buttons.append(
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_city_next"], callback_data=f"{prefix}page_{page + 1}")
        )
    if nav_buttons:
        keyboard.append(nav_buttons)

    # ПРОПУСТИТЬ — ВСЕГДА ПОСЛЕ НАВИГАЦИИ (в самом низу)
    keyboard.append([
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_weight_skip"], callback_data=f"{prefix}skip")
    ])

    return InlineKeyboardMarkup(keyboard)

def get_search_weight_keyboard(lang="ru", selected_min=None, selected_max=None):
    ranges = [
        (40, 59),
        (60, 79),
        (80, 99),
        (100, 119),
        (120, 150)
    ]
    keyboard = []
    for r in ranges:
        marker = " ✓" if r[0] == selected_min and r[1] == selected_max else ""
        keyboard.append([
            InlineKeyboardButton(
                f"{r[0]}–{r[1]} {TEXT2[lang]['kg']}{marker}",
                callback_data=f"search_weight_{r[0]}_{r[1]}"
            )
        ])

    any_marker = " ✓" if selected_min is None and selected_max is None else ""
    keyboard.append([
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_weight_any"] + any_marker,
                             callback_data="search_weight_any")
    ])
    return InlineKeyboardMarkup(keyboard)

def get_weight_filter_label(wmin, wmax, lang):
    if wmin is None or wmax is None:
        return TEXT2[lang]["any"]
    return f"{wmin}–{wmax} {TEXT2[lang]['kg']}"



def reset_user_context(context: ContextTypes.DEFAULT_TYPE):
    # Полная очистка всех ожидаемых состояний пользователя
    context.user_data["awaiting_photo"] = False
    context.user_data["awaiting_bio"] = False
    context.user_data["awaiting_weight"] = False
    context.user_data["awaiting_gender"] = False
    context.user_data["awaiting_custom_city"] = False
    context.user_data["awaiting_edit_photo"] = False
    context.user_data["awaiting_bio_again"] = False
    # Можно добавить ещё если будут новые этапы в будущем


def contains_emoji(text):
    """Проверяет наличие эмодзи в тексте"""
    import re
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "]+", 
        flags=re.UNICODE
    )
    return bool(emoji_pattern.search(text))


def validate_text(text,
                  lang="ru",
                  max_length=100,
                  min_length=1,
                  allow_symbols=False):
    if not text or len(text.strip()) < min_length:
        return TEXT2[lang]["err_too_short"]
    if len(text) > max_length:
        return TEXT2[lang]["err_too_long"].format(max=max_length)

    BAD_WORDS = [
        # Русский мат и формы
        "пизд",
        "пиздц",
        "пёзд",
        "письк",
        "обосс",
        "залуп",
        "соси",
        "выеб",
        "заеб",
        "уеб",
        "наеб",
        "дроч",
        "гандон",
        "гондон",
        "шлюх",
        "манда",
        "мразь",
        "жоп",
        "жпу",
        "сука",
        "суки",
        "сучка",
        "сучон",
        "сцука",
        "чмо",
        "чмош",
        "пидор",
        "педик",
        "петух",
        "ебыр",
        "мудак",
        "долбоеб",
        "дебил",
        "даун",
        "тварь",
        "мерзавец",
        "падла",
        "урод",
        "гнида",
        "пидар",

        # Латиницей и транслитом
        "fuck",
        "fck",
        "fak",
        "fak u",
        "fak you",
        "f*ck",
        "fuk",
        "fcku",
        "shit",
        "bitch",
        "asshole",
        "ass",
        "cunt",
        "whore",
        "slut",
        "dick",
        "suck",
        "blowjob",
        "anal",
        "porn",
        "gay",
        "faggot",
        "retard",
        "idiot",
        "loser",
        "crap",
        "jerk",
        "motherf",
        "cum",

        # Обходы с символами
        "п*зда",
        "с*ка",
        "м*разь",
        "ж*па",
        "др*ч",
        "пид*р",
        "г*ндон",
        "ш*юха"
    ]

    if any(word in text.lower() for word in BAD_WORDS):
        return TEXT2[lang]["err_profanity"]

    return None


REGISTRATION_STATES = [
    "awaiting_name", "awaiting_city_search", "awaiting_custom_country", "awaiting_custom_city",
    "awaiting_photo", "awaiting_bio", "awaiting_name2",
    "awaiting_edit_location_search", "awaiting_filter_city_search"
]

EDIT_STATES = ["awaiting_edit_photo", "awaiting_bio_again"]

BOARD_STATES = [
    "awaiting_board_date", "awaiting_board_time", "awaiting_board_climb_type",
    "awaiting_board_category", "awaiting_board_weight", "awaiting_board_gym",
    "awaiting_board_text"
]


def set_state(context, state_name):
    for state in REGISTRATION_STATES:
        context.user_data[state] = (state == state_name)


def get_state(context):
    for state in REGISTRATION_STATES:
        if context.user_data.get(state):
            return state
    return None


def clear_states(context):
    for state in REGISTRATION_STATES:
        context.user_data[state] = False


async def add_magnesium(user_id, amount, reason=""):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO magnesium_balance (user_id, balance) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
            user_id)
        await conn.execute(
            "UPDATE magnesium_balance SET balance = balance + $1 WHERE user_id = $2",
            amount, user_id)
        await conn.execute(
            "INSERT INTO magnesium_log (user_id, change, reason) VALUES ($1, $2, $3)",
            user_id, amount, reason)

async def already_received_magnesium_this_week(user_id):
    week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT 1 FROM board_magnesium_log
            WHERE user_id = $1 AND week_start = $2
        """, user_id, week_start)
        return row is not None


async def get_magnesium(user_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM magnesium_balance WHERE user_id = $1",
                       user_id)
        return row['balance'] if row else 0

async def spend_magnesium(user_id: int, amount: float, reason: str = "") -> bool:
    """
    Списывает amount грамм магнезии. Возвращает True, если успешно.
    Пишет отрицательную запись в magnesium_log.
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM magnesium_balance WHERE user_id = $1", user_id)
        current = row['balance'] if row else 0.0
        if current < amount:
            return False

        # гарантируем наличие записи
        await conn.execute(
            "INSERT INTO magnesium_balance (user_id, balance) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
            user_id
        )
        await conn.execute("UPDATE magnesium_balance SET balance = balance - $1 WHERE user_id = $2", amount, user_id)
        await conn.execute(
            "INSERT INTO magnesium_log (user_id, change, reason) VALUES ($1, $2, $3)",
            user_id, -amount, reason or "Покупка Boost за магнезию"
        )
        return True


async def has_active_boost(user_id: int) -> bool:
    """Async version - проверяет активен ли Boost у пользователя (или Founder статус)"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT boost_expires_at, is_founder FROM users WHERE user_id = $1", user_id)
        if not row:
            return False
        # Founder имеет пожизненный доступ к Boost
        if row['is_founder']:
            return True
        # Обычная проверка буста
        if not row['boost_expires_at']:
            return False
        return row['boost_expires_at'] > datetime.now()

async def add_boost_emoji_to_name(name: str, user_id: int) -> str:
    """Добавляет эмодзи к имени: 💎 для Founder, 🗯 для Boost"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT is_founder, boost_expires_at FROM users WHERE user_id = $1", user_id)
        if not row:
            return name

        # Приоритет: Founder > Boost
        if row['is_founder']:
            return f"{name} 💎"
        elif row['boost_expires_at'] and row['boost_expires_at'] > datetime.now():
            return f"{name} 🗯"

        return name


async def boost_days_left(user_id: int) -> int:
    """Async version - количество дней до истечения Boost (Founder = бесконечность = 999999)"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT boost_expires_at, is_founder FROM users WHERE user_id = $1", user_id)
        if not row:
            return 0
        # Founder имеет пожизненный доступ
        if row['is_founder']:
            return 999999  # Бесконечность для Founder
        # Обычная проверка буста
        if not row['boost_expires_at']:
            return 0
        delta = row['boost_expires_at'] - datetime.now()
        return max(0, delta.days)


async def extend_boost_by_month(user_id: int) -> datetime:
    """
    Продлевает Boost на 30 дней от максимума(NOW, expires_at). Возвращает новую дату истечения.
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT boost_expires_at FROM users WHERE user_id = $1", user_id)
        now = datetime.now()
        base = row['boost_expires_at'] if row and row['boost_expires_at'] and row['boost_expires_at'] > now else now
        new_exp = base + timedelta(days=15)

        await conn.execute("UPDATE users SET boost_expires_at = $1 WHERE user_id = $2", new_exp, user_id)
        return new_exp



FEEDBACK_CHANNEL_ID = -1002628227420

# Сессии пользователей (временно в памяти)

user_sessions = {}

# ======== DATABASE MIGRATIONS (вызывается из main после prepare_db_init) ========
def run_migrations():
    """Выполняет все schema migrations. Вызывается ПОСЛЕ prepare_db_init()"""
    print("🔧 Running database migrations...")

    try:
        cursor.execute("ALTER TABLE chat_requests_log ADD COLUMN status TEXT DEFAULT 'pending'")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'status' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status_slug TEXT;")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'status_slug' уже существует или ошибка: {e}")

    try:
        cursor.execute("""
            ALTER TABLE search_filters
            ADD COLUMN weight_min INTEGER,
            ADD COLUMN weight_max INTEGER
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поля 'weight_min' и 'weight_max' уже существуют или ошибка: {e}")

    # Миграция: добавляем CASCADE для gym_session_participants
    try:
        cursor.execute("""
            ALTER TABLE gym_session_participants 
            DROP CONSTRAINT IF EXISTS gym_session_participants_session_id_fkey
        """)
        cursor.execute("""
            ALTER TABLE gym_session_participants 
            ADD CONSTRAINT gym_session_participants_session_id_fkey 
            FOREIGN KEY (session_id) REFERENCES gym_sessions(id) ON DELETE CASCADE
        """)
        conn.commit()
        print("✅ CASCADE для gym_session_participants")
    except Exception as e:
        print(f"⚠️ CASCADE migration: {e}")

    try:
        cursor.execute("ALTER TABLE hidden_users ADD COLUMN notified INTEGER DEFAULT 0")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'notified' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE user_chats ADD COLUMN notified_about_new_message BOOLEAN DEFAULT FALSE")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'notified_about_new_message' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE user_chats ADD COLUMN last_notified_at TIMESTAMP;")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'notified_about_new_message' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE user_chats ADD COLUMN is_archived BOOLEAN DEFAULT FALSE")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'is_archived' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE board_posts ADD COLUMN weight TEXT;")
        conn.commit()
    except Exception as e:
        print(f"Поле weight уже существует или ошибка при добавлении: {e}")

    try:
        cursor.execute("ALTER TABLE board_posts ADD COLUMN partner_gender TEXT;")
        conn.commit()
    except Exception as e:
        print(f"Поле partner_gender уже существует или ошибка при добавлении: {e}")

    try:
        cursor.execute("ALTER TABLE board_posts ADD COLUMN difficulty TEXT;")
        conn.commit()
    except Exception as e:
        print(f"Поле difficulty уже существует или ошибка при добавлении: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'registration_date' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE referrals ADD COLUMN activated INTEGER DEFAULT 0")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'activated' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN consent_accepted INTEGER DEFAULT 0")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'consent_accepted' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN boost_expires_at TIMESTAMP;")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'boost_expires_at' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN name_clean TEXT;")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'name_clean' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN has_real_photo BOOLEAN DEFAULT FALSE;")
        conn.commit()
        print("✅ Поле 'has_real_photo' добавлено")
    except Exception as e:
        print(f"⚠️ Поле 'has_real_photo' уже существует или ошибка: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_founder BOOLEAN DEFAULT FALSE;")
        conn.commit()
        print("✅ Поле 'is_founder' добавлено")
    except Exception as e:
        print(f"⚠️ Поле 'is_founder' уже существует или ошибка: {e}")

    try:
        cursor.execute("""
            ALTER TABLE search_filters
            ADD COLUMN has_photo BOOLEAN,
            ADD COLUMN status_slug TEXT,
            ADD COLUMN city_override TEXT,
            ADD COLUMN sort_popular BOOLEAN
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ Премиум-поля search_filters уже существуют или ошибка: {e}")

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS like_push_log (
                from_user_id BIGINT,
                to_user_id BIGINT,
                push_date DATE,
                PRIMARY KEY (from_user_id, to_user_id, push_date)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ Ошибка создания like_push_log: {e}")

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes_section_state (
                user_id BIGINT NOT NULL,
                section TEXT NOT NULL,
                last_open TIMESTAMP,
                PRIMARY KEY (user_id, section)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ Ошибка создания likes_section_state: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN likes_count INTEGER DEFAULT 0")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'likes_count' уже существует или ошибка: {e}")

    # Добавляем поле is_deleted для мягкого удаления (soft delete)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Поле 'is_deleted' уже существует или ошибка: {e}")


    # Таблица для отслеживания рассылок напоминаний о фото
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS photo_reminders_log (
                user_id BIGINT NOT NULL,
                reminder_day INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, reminder_day)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ Ошибка создания photo_reminders_log: {e}")

    # Создаём триггер для автоматического подсчёта лайков
    try:
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_likes_count()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE users SET likes_count = likes_count + 1 
                    WHERE user_id = NEW.to_user_id;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE users SET likes_count = GREATEST(likes_count - 1, 0) 
                    WHERE user_id = OLD.to_user_id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
        """)
        conn.commit()
        print("✅ Функция update_likes_count создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания функции триггера: {e}")

    try:
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_likes_count ON likes;
        """)
        cursor.execute("""
            CREATE TRIGGER trigger_update_likes_count
            AFTER INSERT OR DELETE ON likes
            FOR EACH ROW EXECUTE FUNCTION update_likes_count();
        """)
        conn.commit()
        print("✅ Триггер trigger_update_likes_count создан")
    except Exception as e:
        print(f"⚠️ Ошибка создания триггера: {e}")

    # Инициализируем likes_count для существующих пользователей (только если таблица не пуста)
    try:
        cursor.execute("""
            UPDATE users u
            SET likes_count = COALESCE(l.cnt, 0)
            FROM (
                SELECT to_user_id, COUNT(*) AS cnt
                FROM likes
                GROUP BY to_user_id
            ) l
            WHERE u.user_id = l.to_user_id
              AND u.likes_count = 0
        """)
        conn.commit()
        print("✅ Инициализированы likes_count для существующих пользователей")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации likes_count: {e}")

    # Добавляем поле created_at для отслеживания регистрации пользователя
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        print("✅ Поле 'created_at' добавлено")
    except Exception as e:
        print(f"⚠️ Поле 'created_at' уже существует или ошибка: {e}")

    # Инициализируем created_at для существующих пользователей (используем registration_date если он есть)
    try:
        cursor.execute("""
            UPDATE users 
            SET created_at = COALESCE(registration_date, CURRENT_TIMESTAMP)
            WHERE created_at IS NULL
        """)
        conn.commit()
        print("✅ Инициализирован created_at для существующих пользователей")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации created_at: {e}")

    # ✅ ШАГ 1: Устанавливаем FALSE для ИЗВЕСТНЫХ заглушек (по размеру)
    # PLACEHOLDER_SIZES = {230154, 243315, 241434, 223273, 239872}
    placeholder_sizes_str = ','.join(str(s) for s in PLACEHOLDER_SIZES)
    try:
        cursor.execute(f"""
            UPDATE users 
            SET has_real_photo = FALSE
            WHERE photo_bytes IS NOT NULL 
              AND length(photo_bytes) IN ({placeholder_sizes_str})
        """)
        placeholder_count = cursor.rowcount
        conn.commit()
        print(f"✅ Установлено has_real_photo=FALSE для {placeholder_count} заглушек (известные размеры: {list(PLACEHOLDER_SIZES)})")
    except Exception as e:
        print(f"⚠️ Ошибка обновления заглушек: {e}")

    # ✅ ШАГ 2: Устанавливаем TRUE для РЕАЛЬНЫХ фото (НЕ заглушки)
    try:
        cursor.execute(f"""
            UPDATE users 
            SET has_real_photo = TRUE
            WHERE photo_bytes IS NOT NULL 
              AND length(photo_bytes) > 0
              AND length(photo_bytes) NOT IN ({placeholder_sizes_str})
              AND (has_real_photo IS NULL OR has_real_photo = FALSE)
        """)
        updated_count = cursor.rowcount
        conn.commit()
        print(f"✅ Синхронизировано has_real_photo=TRUE для {updated_count} пользователей с реальными фото")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации has_real_photo=TRUE: {e}")

    # ✅ ШАГ 3: Сбрасываем has_real_photo в FALSE для пользователей БЕЗ фото (NULL)
    try:
        cursor.execute("""
            UPDATE users 
            SET has_real_photo = FALSE
            WHERE (photo_bytes IS NULL OR length(photo_bytes) = 0)
              AND (has_real_photo = TRUE OR has_real_photo IS NULL)
        """)
        corrected_count = cursor.rowcount
        conn.commit()
        print(f"✅ Скорректировано has_real_photo=FALSE для {corrected_count} пользователей без фото")
    except Exception as e:
        print(f"⚠️ Ошибка коррекции has_real_photo=FALSE: {e}")

    # Добавляем поле global_search_used для одноразового глобального поиска
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN global_search_used BOOLEAN DEFAULT FALSE")
        conn.commit()
        print("✅ Поле 'global_search_used' добавлено")
    except Exception as e:
        print(f"⚠️ Поле 'global_search_used' уже существует или ошибка: {e}")

    # ======== ТАБЛИЦЫ ДЛЯ ФИЧИ "ВСТРЕЧИ" (gym_sessions) ========

    # Таблица карточек тренировок
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gym_sessions (
                id SERIAL PRIMARY KEY,
                gym_id TEXT,
                gym_name TEXT,
                city_key TEXT NOT NULL,
                climb_type TEXT NOT NULL,
                session_date DATE NOT NULL,
                session_time TIME NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                created_by BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                timezone TEXT DEFAULT 'Europe/Moscow'
            )
        """)
        conn.commit()
        print("✅ Таблица gym_sessions создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания gym_sessions: {e}")

    # Таблица участников тренировок
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gym_session_participants (
                session_id INTEGER NOT NULL,
                user_id BIGINT NOT NULL,
                difficulty TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, user_id)
            )
        """)
        conn.commit()
        print("✅ Таблица gym_session_participants создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания gym_session_participants: {e}")

    # Таблица групповых чатов (ОТДЕЛЬНО от 1x1 чатов!)
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_chats (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                chat_name TEXT,
                is_board BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Таблица group_chats создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания group_chats: {e}")

    # Миграция: добавляем колонку is_board если её нет
    try:
        cursor.execute("""
            ALTER TABLE group_chats
            ADD COLUMN IF NOT EXISTS is_board BOOLEAN DEFAULT FALSE
        """)
        conn.commit()
        print("✅ Колонка is_board добавлена в group_chats")
    except Exception as e:
        print(f"⚠️ Колонка is_board уже существует: {e}")

    # Миграция: меняем UNIQUE constraint на составной (session_id, is_board)
    try:
        # Удаляем старый UNIQUE constraint на session_id если он есть
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'group_chats_session_id_key'
                ) THEN
                    ALTER TABLE group_chats DROP CONSTRAINT group_chats_session_id_key;
                END IF;
            END $$;
        """)
        # Добавляем составной UNIQUE constraint если его нет
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'group_chats_session_board_unique'
                ) THEN
                    ALTER TABLE group_chats ADD CONSTRAINT group_chats_session_board_unique UNIQUE (session_id, is_board);
                END IF;
            END $$;
        """)
        conn.commit()
        print("✅ UNIQUE constraint обновлен на (session_id, is_board)")
    except Exception as e:
        print(f"⚠️ Ошибка обновления constraint: {e}")

    # Таблица сообщений групповых чатов
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_chat_messages (
                id SERIAL PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                sender_id BIGINT NOT NULL,
                message_text TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Таблица group_chat_messages создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания group_chat_messages: {e}")

    # Таблица отзывов о тренировках
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_feedback (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                user_id BIGINT NOT NULL,
                rating TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (session_id, user_id)
            )
        """)
        conn.commit()
        print("✅ Таблица training_feedback создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания training_feedback: {e}")

    # Логи тренировок для статистики
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_logs (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                user_id BIGINT,
                city TEXT,
                gym_name TEXT,
                climb_type TEXT,
                session_date DATE,
                participants_count INTEGER DEFAULT 0,
                positive_feedback INTEGER DEFAULT 0,
                negative_feedback INTEGER DEFAULT 0,
                rewarded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Таблица training_logs создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания training_logs: {e}")

    # Миграция: добавляем user_id и rewarded если их нет
    try:
        cursor.execute("ALTER TABLE training_logs ADD COLUMN IF NOT EXISTS user_id BIGINT")
        cursor.execute("ALTER TABLE training_logs ADD COLUMN IF NOT EXISTS rewarded BOOLEAN DEFAULT FALSE")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_training_logs_user_session ON training_logs(user_id, session_id)")
        conn.commit()
    except Exception as e:
        print(f"⚠️ training_logs migration: {e}")

    # Миграция gym_sessions: добавляем gym_id и city_key, убираем NOT NULL с city
    try:
        cursor.execute("ALTER TABLE gym_sessions ADD COLUMN IF NOT EXISTS gym_id TEXT")
        cursor.execute("ALTER TABLE gym_sessions ADD COLUMN IF NOT EXISTS city_key TEXT")
        cursor.execute("ALTER TABLE gym_sessions ALTER COLUMN city DROP NOT NULL")
        conn.commit()
    except Exception as e:
        print(f"⚠️ gym_sessions migration: {e}")

    # Таблица участников групповых чатов (ИЗОЛИРОВАННАЯ от 1x1)
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetup_chat_members (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                chat_id INTEGER NOT NULL,
                session_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_read_ts TIMESTAMP,
                notified_once BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                UNIQUE(user_id, chat_id)
            )
        """)
        conn.commit()
        print("✅ Таблица meetup_chat_members создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания meetup_chat_members: {e}")

    # Таблица активности групповых чатов
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetup_chat_activity (
                chat_id INTEGER PRIMARY KEY,
                session_id INTEGER NOT NULL,
                last_message_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Таблица meetup_chat_activity создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания meetup_chat_activity: {e}")

    # Индексы для быстрого поиска
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gym_sessions_city_date ON gym_sessions(city_key, session_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gym_session_participants_user ON gym_session_participants(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_chat_messages_chat ON group_chat_messages(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetup_chat_members_user ON meetup_chat_members(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetup_chat_members_chat ON meetup_chat_members(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_chat_messages_sent ON group_chat_messages(chat_id, sent_at)")
        conn.commit()
        print("✅ Индексы для gym_sessions созданы")
    except Exception as e:
        print(f"⚠️ Ошибка создания индексов: {e}")

    # ===== МИГРАЦИЯ: Переделка board_posts под систему участников =====
    print("🔧 Запуск миграции board_posts → board_sessions...")

    try:
        # 1. Создаём новую таблицу board_sessions (аналог gym_sessions для board)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS board_sessions (
                id SERIAL PRIMARY KEY,
                creator_id BIGINT NOT NULL,
                gym_name TEXT,
                city_key TEXT,
                climb_type TEXT NOT NULL,
                session_date DATE NOT NULL,
                session_time TIME NOT NULL,
                is_custom BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        conn.commit()
        print("✅ Таблица board_sessions создана")
    except Exception as e:
        print(f"⚠️ Таблица board_sessions уже существует или ошибка: {e}")

    try:
        # 2. Создаём таблицу board_session_participants (аналог gym_session_participants)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS board_session_participants (
                session_id INTEGER REFERENCES board_sessions(id) ON DELETE CASCADE,
                user_id BIGINT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, user_id)
            )
        """)
        conn.commit()
        print("✅ Таблица board_session_participants создана")
    except Exception as e:
        print(f"⚠️ Таблица board_session_participants уже существует или ошибка: {e}")

    try:
        # 3. Мигрируем данные из старой board_posts в новые таблицы
        cursor.execute("""
            SELECT user_id, date, time, climb_type, gym, created_at, updated_at, status
            FROM board_posts
            WHERE status = 'active'
        """)
        old_posts = cursor.fetchall()

        migrated_count = 0
        for post in old_posts:
            user_id, date, time, climb_type, gym, created_at, updated_at, status = post

            # Определяем city_key по городу пользователя
            cursor.execute("SELECT city FROM users WHERE user_id = %s", (user_id,))
            user_row = cursor.fetchone()
            city_key = None
            if user_row:
                city = user_row[0]
                if city and ("Петербург" in city or "Petersburg" in city):
                    city_key = "spb"
                elif city and ("Москва" in city or "Moscow" in city):
                    city_key = "msk"

            # Проверяем, не мигрировано ли уже это объявление
            cursor.execute("""
                SELECT id FROM board_sessions
                WHERE creator_id = %s AND session_date = %s AND session_time = %s
            """, (user_id, date, time))

            existing = cursor.fetchone()
            if existing:
                continue  # Уже мигрировано, пропускаем

            # Вставляем в board_sessions
            cursor.execute("""
                INSERT INTO board_sessions
                (creator_id, gym_name, city_key, climb_type, session_date, session_time, is_custom, created_at, updated_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s, %s, %s)
                RETURNING id
            """, (user_id, gym, city_key, climb_type, date, time, created_at, updated_at, status))

            result = cursor.fetchone()
            if result:
                session_id = result[0]

                # Добавляем создателя как участника
                cursor.execute("""
                    INSERT INTO board_session_participants (session_id, user_id, joined_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (session_id, user_id, created_at))

                migrated_count += 1

        conn.commit()
        print(f"✅ Мигрировано {migrated_count} объявлений из board_posts в board_sessions")
    except Exception as e:
        print(f"⚠️ Ошибка миграции данных board_posts: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()

    try:
        # 4. Создаём индексы для производительности
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_board_sessions_gym_date
            ON board_sessions(gym_name, session_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_board_sessions_city_date
            ON board_sessions(city_key, session_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_board_sessions_creator
            ON board_sessions(creator_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_board_sessions_status
            ON board_sessions(status, session_date)
        """)
        conn.commit()
        print("✅ Индексы для board_sessions созданы")
    except Exception as e:
        print(f"⚠️ Ошибка создания индексов: {e}")

    print("✅ Database migrations completed")
# ======== /MIGRATIONS ========


def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            name TEXT,
            name_clean TEXT,
            language TEXT,
            difficulty TEXT,
            climb_type TEXT,
            country TEXT,
            country_other TEXT,
            city TEXT,
            city_other TEXT,
            photo_bytes BYTEA,
            gender TEXT,
            weight TEXT,
            bio TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            consent_accepted INTEGER DEFAULT 0,
            invited_by BIGINT,
            boost_expires_at TIMESTAMP
        )
    """)
    conn.commit()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS board_posts (
            user_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date TEXT,
            time TEXT,
            climb_type TEXT,
            difficulty TEXT,
            weight TEXT,
            gym TEXT,
            status TEXT  -- active, removed
            )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS board_magnesium_log (
        user_id BIGINT,
        week_start DATE,
        PRIMARY KEY (user_id, week_start)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_chats (
        user_id BIGINT,
        partner_id BIGINT,
        last_message_time TIMESTAMP DEFAULT NOW(),
        last_read_time TIMESTAMP,
        is_archived BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (user_id, partner_id)
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback_log (
            user_id BIGINT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registration_times (
        user_id BIGINT PRIMARY KEY,
        start_time TIMESTAMP,
        finish_time TIMESTAMP
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_logins (
        user_id BIGINT,
        login_date DATE
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        inviter_id BIGINT,
        invited_id BIGINT UNIQUE,
        activated INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS muted_users (
        user_id BIGINT,
        muted_user_id BIGINT,
        PRIMARY KEY (user_id, muted_user_id)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS magnesium_balance (
        user_id BIGINT PRIMARY KEY,
        balance REAL DEFAULT 0
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS city_push_log (
        city TEXT PRIMARY KEY,
        last_push_time TIMESTAMP
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS magnesium_log (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        change REAL,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        from_user_id BIGINT,
        to_user_id BIGINT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (from_user_id, to_user_id)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_reports (
        reporter_id BIGINT,
        reported_id BIGINT,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (reporter_id, reported_id)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_archive (
        user_id BIGINT,
        partner_id BIGINT,
        archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, partner_id)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hidden_users (
        user_id BIGINT,
        hidden_user_id BIGINT,
        hide_until TIMESTAMP,
        notified INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, hidden_user_id)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proxy_chats (
        user1_id BIGINT,
        user2_id BIGINT,
        active INTEGER DEFAULT 1,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user1_id, user2_id)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_requests_log (
        from_user_id BIGINT,
        to_user_id BIGINT,
        action TEXT,
        status TEXT DEFAULT 'pending',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (from_user_id, to_user_id, action)
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        chat_id TEXT,
        sender_id BIGINT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_filters (
            user_id BIGINT PRIMARY KEY,
            difficulty TEXT,
            climb_type TEXT,
            gender TEXT,
            weight TEXT,           
            weight_min INTEGER,
            weight_max INTEGER,
            has_photo BOOLEAN,
            status_slug TEXT,
            city_override TEXT,
            sort_popular BOOLEAN
        )
    """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS like_push_log (
            from_user_id BIGINT,
            to_user_id BIGINT,
            push_date DATE,
            PRIMARY KEY (from_user_id, to_user_id, push_date)
        )
    """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_request_logs (
            user_id BIGINT,
            request_date DATE,
            request_count INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, request_date)
        )
    """)
    conn.commit()



# Словари перевода значений для карточки
DIFFICULTY_LABELS = {"beginner": "3–5C", "advanced": "6A–6C", "pro": "7A–9C"}

async def get_username(user_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", user_id)
        return row['name'] if row and row['name'] else "—"

def get_weight_label(code, lang):
    if not code or code == "None":
        return TEXT2[lang]["not_specified"]
    try:
        weight_int = int(code)
        if 40 <= weight_int <= 150:
            return f"{weight_int} {TEXT2[lang]['kg']}"
    except:
        pass
    return TEXT2[lang].get(f"weight_{code}", TEXT2[lang]["not_specified"])


def get_climb_label(code, lang):
    if not code or code == "None":
        return TEXT2[lang]["not_specified"]
    return TEXT2[lang].get(f"climb_{code}", TEXT2[lang]["not_specified"])


def get_gender_label(code, lang):
    if not code or code == "None":
        return TEXT2[lang]["not_specified"]
    return TEXT2[lang].get(f"gender_{code}", TEXT2[lang]["not_specified"])


async def handle_language_choice(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang_", "")
    context.user_data["lang"] = lang_code

    await query.edit_message_text(f"✅ Language set to: {lang_code.upper()}")


async def show_user_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE, show_inline_button=True):
    query = update.callback_query if update.callback_query else None
    message = query.message if query else update.message

    if query:
        await query.answer()

    if not update.effective_user:
        return

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Берём текст без экранирования
    raw_text = USER_AGREEMENT_TEXT.get(lang, USER_AGREEMENT_TEXT["ru"])
    agreement_text = raw_text

    # Разбиваем текст по абзацам, чтобы не разрезать Markdown-теги
    MAX_LENGTH = 3900
    parts = []
    current_part = ""

    # Разбиваем по абзацам (двойной перенос строки)
    paragraphs = agreement_text.split("\n\n")

    for paragraph in paragraphs:
        # Если добавление параграфа превысит лимит - сохраняем текущую часть
        if len(current_part) + len(paragraph) + 2 > MAX_LENGTH and current_part:
            parts.append(current_part)
            current_part = paragraph + "\n\n"
        else:
            current_part += paragraph + "\n\n"

    # Добавляем последнюю часть
    if current_part:
        parts.append(current_part.rstrip())

    # Кнопки согласия (только на последней части)
    if show_inline_button:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXT2[lang]["btn_agree"], callback_data="consent_agree")],
            [InlineKeyboardButton(TEXT2[lang]["btn_decline"], callback_data="consent_decline")]
        ])
    else:
        reply_markup = None

    # Отправляем все части
    for idx, part in enumerate(parts):
        is_last = (idx == len(parts) - 1)
        await message.reply_text(
            part,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=reply_markup if is_last else None
        )


async def handle_consent_decline(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    await query.message.reply_text(TEXT2[lang]["consent_decline_text"])


async def handle_consent_agree(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if not context.user_data.get("awaiting_consent"):
        return

    context.user_data["awaiting_consent"] = False

    # ✅ Обновляем в базе согласие
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id)
        await conn.execute("UPDATE users SET consent_accepted = 1 WHERE user_id = $1",
                       user_id)

    # ✅ Сохраняем lang и username в профиль
    user_sessions[user_id] = user_sessions.get(user_id, {})
    user_sessions[user_id]["lang"] = lang
    user_sessions[user_id]["username"] = update.effective_user.username
    await save_partial_profile(user_id)

    # Сначала — сообщение без клавиатуры
    await query.message.reply_text(TEXT2[lang]["welcome_final"])


    # Затем — отдельной строкой inline-кнопка "📋 Заполнить"
    inline_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_fill_profile"],
                             callback_data="fill_profile")
    ]])

    await query.message.reply_text(TEXT2[lang]["welcome_fill_hint"],
                                   reply_markup=inline_markup)


def get_progress_keyboard(step: int, lang: str) -> ReplyKeyboardMarkup:
    """Генерирует кнопку прогресса регистрации (Шаг X из 8)"""
    return ReplyKeyboardMarkup(
        [[KeyboardButton(TEXTS[lang]["reg_progress"].format(step=step))]],
        resize_keyboard=True,
        one_time_keyboard=False
    )


async def handle_fill_profile(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    set_state(context, "awaiting_name")
    await query.message.reply_text(TEXT2[lang]["ask_name"],
                                   reply_markup=get_progress_keyboard(1, lang))


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    main_buttons = [
        TEXTS[lang]["menu_likes"], TEXTS[lang]["menu_search"],
        TEXTS[lang]["menu_chats"], TEXTS[lang]["menu_board"],
        TEXTS[lang]["menu_form"], TEXTS[lang]["menu_chalk"], TEXTS[lang]["menu_about"]
    ]


    if text in [TEXTS[lang]["search_back"], TEXTS[lang]["menu_home"], TEXTS[lang]["board_back"]]:
        # Сбрасываем режим встреч при выходе
        context.user_data["in_meetups_mode"] = False
        context.user_data["meetups_gym_index"] = 0

        markup = ReplyKeyboardMarkup([[
            KeyboardButton(main_buttons[0]),
            KeyboardButton(main_buttons[1])
        ], [
            KeyboardButton(main_buttons[2]),
            KeyboardButton(main_buttons[3])
        ], [KeyboardButton(main_buttons[4]), KeyboardButton(main_buttons[5]),
            KeyboardButton(main_buttons[6])]],
                                     resize_keyboard=True,
                                     one_time_keyboard=False)
        await update.message.reply_text(TEXT2[lang]["menu_main"],
                                        reply_markup=markup)
        return

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    if text == TEXTS[lang]["menu_chalk"]:
        keyboard = [[
            KeyboardButton(TEXTS[lang]["chalk_get"]),
            KeyboardButton(TEXTS[lang]["chalk_use"])
        ], [KeyboardButton(TEXTS[lang]["chalk_amount"]), KeyboardButton(TEXTS[lang]["chalk_status"])],
                    [KeyboardButton(TEXTS[lang]["chalk_back"])]]
        await update.message.reply_text(TEXT2[lang]["menu_chalk_title_hi"],
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard, resize_keyboard=True))
        return

    if text == TEXTS[lang]["menu_about"]:
        keyboard = [
            [KeyboardButton(TEXTS[lang]["about_rules"]), KeyboardButton(TEXTS[lang]["about_feedback"])],
            [KeyboardButton(TEXTS[lang]["about_home"])],
            [KeyboardButton(TEXTS[lang]["about_back"])]
        ]

        await update.message.reply_text(
            TEXT2[lang]["menu_about_title"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return



    if text == TEXTS[lang]["menu_form"]:
        await show_profile_preview(update, context)
        return




    if text == TEXTS[lang]["menu_chats"]:
        menu = [
            [KeyboardButton(TEXTS[lang]["chats_active"])],
            [KeyboardButton(TEXTS[lang]["offline_muted"])],
            [KeyboardButton(TEXTS[lang]["chats_back"])]
        ]
        markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)

        await update.message.reply_text(TEXT2[lang]["menu_chats_title"],
                                        reply_markup=markup)
        return

    if text == TEXTS[lang]["menu_search"]:
        keyboard = [
            [KeyboardButton(TEXTS[lang]["search_next_person"])],
            [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
            [KeyboardButton(TEXTS[lang]["search_back"])]
        ]

        await update.message.reply_text(TEXT2[lang]["menu_search_title"],
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard, resize_keyboard=True))
        await handle_search_command(update, context)
        return

    if text == TEXTS[lang]["search_filters"]:
        await handle_filters_entry_text(update, context)
        return

    if text == TEXTS[lang]["menu_likes"]:
        user_id = update.effective_user.id

        # 🔒 ПРОВЕРКА ДОСТУПА: Founder ИЛИ активный Boost ИЛИ есть реферал
        async with db_pool.acquire() as conn:
            # Проверяем реферал
            row = await conn.fetchrow(
                "SELECT 1 FROM referrals WHERE inviter_id = $1 AND activated = 1",
                user_id
            )
            has_referral = row is not None

        # Проверяем активный Boost (функция уже проверяет и Founder, и обычный Boost)
        has_boost = await has_active_boost(user_id)

        # Доступ разрешён если: Boost активен ИЛИ есть реферал
        if not has_referral and not has_boost:
            bot_username = context.bot.username
            ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"

            await update.message.reply_photo(
                photo='https://postimg.cc/5YVb1b2c',
                caption=TEXT2[lang]["menu_likes_locked_caption"],
                parse_mode=ParseMode.HTML
            )


            await asyncio.sleep(1)

            forward_text = TEXT2[lang]["menu_likes_message_to_share"].format(
                ref_link=ref_link
            )

            await update.message.reply_text(
                TEXT2[lang]["menu_likes_share_hint"],
                parse_mode=ParseMode.HTML
            )

            await update.message.reply_text(
                forward_text,
                parse_mode=ParseMode.HTML
            )

            return

        # 🔓 ЕСЛИ РЕФЕРАЛ ЕСТЬ — показываем новое меню лайков со счётчиками

        # Считаем лайки
        async with db_pool.acquire() as conn:
            my_likes_count = await conn.fetchval("SELECT COUNT(*) FROM likes WHERE from_user_id = $1", user_id)

            liked_me_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", user_id)

            mutual_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM likes l1
                JOIN likes l2
                  ON l1.to_user_id = l2.from_user_id
                 AND l1.from_user_id = l2.to_user_id
                WHERE l1.from_user_id = $1
            """, user_id)

        sent_label = TEXTS[lang]['likes_sent']
        received_label = TEXTS[lang]['likes_received']
        mutual_label = TEXTS[lang]['likes_mutual']

        keyboard = [
            [KeyboardButton(sent_label)],
            [KeyboardButton(received_label), KeyboardButton(mutual_label)],
            [KeyboardButton(TEXTS[lang]["likes_back"])]
        ]

        photo_url = "https://postimg.cc/CRTkdp7Y"
        await update.message.reply_photo(
            photo=photo_url,
            caption=TEXT2[lang]["menu_likes_title"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return




###################################################################################### TEST TEST
async def show_admin_menu(update: Update):
    """Главное меню админ-панели с группировкой функций"""
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск пользователя", callback_data="admin_search_user")],
        [InlineKeyboardButton("🚨 Модерация", callback_data="admin_moderation_menu")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats_menu")],
        [InlineKeyboardButton("📢 Рассылки", callback_data="admin_broadcast_menu")],
        [InlineKeyboardButton("✉️ Написать сообщение", callback_data="admin_send_message")],
        [InlineKeyboardButton("🗑️ Удалить профиль по ID", callback_data="admin_delete_profile_by_id")],
        [InlineKeyboardButton("🔙 Выйти из админки", callback_data="admin_exit")],
    ]
    await update.message.reply_text(
        "👑 Админ-панель:", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_moderation_menu(query):
    """Подменю модерации: жалобы, баны, последние регистрации"""
    keyboard = [
        [InlineKeyboardButton("🚨 Жалобы по категориям", callback_data="admin_reports_by_reason")],
        [InlineKeyboardButton("👥 Забаненные пользователи", callback_data="admin_banned_list")],
        [InlineKeyboardButton("👤 Последние 10 регистраций", callback_data="admin_recent_users")],
        [InlineKeyboardButton("🔎 Анкета по ID", callback_data="admin_view_profile")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back_to_main")],
    ]
    await query.message.edit_text(
        "🚨 Модерация:", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_stats_menu(query):
    """Подменю статистики"""
    keyboard = [
        [InlineKeyboardButton("🔥 DAU/WAU/MAU", callback_data="stats_dau")],
        [InlineKeyboardButton("📈 Retention", callback_data="stats_retention_new")],
        [InlineKeyboardButton("📅 По месяцам", callback_data="stats_monthly")],
        [InlineKeyboardButton("💬 Чаты", callback_data="stats_chats")],
        [InlineKeyboardButton("❤️ Лайки", callback_data="stats_likes_detailed")],
        [InlineKeyboardButton("📊 Регистрации", callback_data="admin_stats")],
        [InlineKeyboardButton("🤝 Встречи", callback_data="admin_meetups_stats")],
        [InlineKeyboardButton("📍 Топ городов", callback_data="admin_top_cities")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back_to_main")],
    ]
    await query.message.edit_text(
        "📊 Статистика:", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_broadcast_menu(query):
    """Подменю рассылок: массовая, локальная (Geoapify), RU"""
    keyboard = [
        [InlineKeyboardButton("📣 Массовая рассылка (все)", callback_data="admin_broadcast_all")],
        [InlineKeyboardButton("📢 Локальная рассылка (город)", callback_data="admin_broadcast_location")],
        [InlineKeyboardButton("🇷🇺 Рассылка RU", callback_data="admin_broadcast_ru")],
        [InlineKeyboardButton("📸 Напоминания о фото", callback_data="admin_send_reminders")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back_to_main")],
    ]
    await query.message.edit_text(
        "📢 Рассылки:", reply_markup=InlineKeyboardMarkup(keyboard))


async def reset_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    # Получаем список тех, кого пригласил этот пользователь
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT invited_id FROM referrals WHERE inviter_id = $1",
                       user_id)
        invited_users = [row['invited_id'] for row in rows]

        # Удаляем записи из таблицы referrals
        await conn.execute("DELETE FROM referrals WHERE inviter_id = $1 OR invited_id = $1",
                       user_id)

        # Очищаем поле invited_by в users
        await conn.execute("UPDATE users SET invited_by = NULL WHERE invited_by = $1",
                       user_id)

    for invited_id in invited_users:
        if invited_id in user_sessions:
            user_sessions[invited_id].pop("invited_by", None)

    await update.message.reply_text(
        "🔄 Все твои рефералы сброшены. У приглашённых пользователей удалена связь.")

async def reset_founder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для снятия статуса Founder (для тестирования)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    # Снимаем статус Founder с самого админа
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET is_founder = FALSE WHERE user_id = $1", user_id)

    await update.message.reply_text("💎 Статус Founder снят. Теперь ты обычный пользователь.")


async def reset_boost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для снятия Cragsy Boost (для тестирования)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    # Снимаем Boost с самого админа
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET boost_expires_at = NULL WHERE user_id = $1", user_id)

    await update.message.reply_text("⏰ Cragsy Boost снят. Теперь ты без премиума.")


async def reset_meetups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для выхода из всех тренировок (для тестирования)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    # Удаляем все записи пользователя на тренировки (и дефолтные, и кастомные)
    async with db_pool.acquire() as conn:
        # Удаляем из дефолтных тренировок (gym_sessions)
        gym_result = await conn.execute(
            "DELETE FROM gym_session_participants WHERE user_id = $1",
            user_id
        )

        # Удаляем из кастомных тренировок (board_sessions)
        board_result = await conn.execute(
            "DELETE FROM board_session_participants WHERE user_id = $1",
            user_id
        )

        # Удаляем из чатов тренировок
        await conn.execute(
            "DELETE FROM meetup_chat_members WHERE user_id = $1",
            user_id
        )

    await update.message.reply_text("🔄 Ты вышел из всех тренировок (дефолтных и кастомных) в меню Meetups.")


async def reset_user_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM user_reports WHERE reporter_id = $1", user_id)

    await update.message.reply_text(
        "🔄 Все твои жалобы были сброшены. Можешь тестировать заново.")

###################################################################################### PROFILE


async def handle_difficulty(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    difficulty = query.data.replace("diff_", "")
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]["difficulty"] = difficulty
    await save_partial_profile(user_id)

    await query.message.reply_text(TEXT2[lang]["difficulty_saved"].format(
        label=DIFFICULTY_LABELS.get(difficulty, difficulty)),
                                   reply_markup=get_progress_keyboard(5, lang))

    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"],
                             callback_data="type_difficulty"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"],
                             callback_data="type_bouldering")
    ],
                [
                    InlineKeyboardButton(
                        INLINE_TEXTS[lang]["btn_search_type_any"],
                        callback_data="type_both")
                ]]

    await query.message.reply_text(TEXT2[lang]["ask_climb_type"],
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_climb_type(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    climb_type = query.data.replace("type_", "")

    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]["climb_type"] = climb_type
    await save_partial_profile(user_id)

    # ✅ Подтверждение выбора (с заменой)
    await query.message.reply_text(TEXT2[lang]["climb_type_saved"].format(
        label=get_climb_label(climb_type, lang)),
                                   reply_markup=get_progress_keyboard(4, lang))

    # 🧗 Запрос уровня после выбора типа
    await query.message.reply_text(
        TEXT2[lang]["ask_difficulty"],
        reply_markup=get_difficulty_keyboard(page=1, lang=lang, prefix="diffval_")
    )



async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # 🔹 Пагинация стран
    if query.data.startswith("country_page_"):
        page = int(query.data.split("_")[-1])
        new_markup = get_country_keyboard(context, page)
        try:
            if query.message.reply_markup != new_markup:
                await query.message.edit_reply_markup(reply_markup=new_markup)
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                raise
        return

    # 🔹 Локальная рассылка
    if context.user_data.get("broadcast_stage") == "select_country":
        country = query.data.replace("country_", "")
        context.user_data["broadcast_country"] = country
        context.user_data["broadcast_stage"] = "select_city"
        await query.message.reply_text(
            f"🏙 Вы выбрали страну: {country}. Теперь выберите город:",
            reply_markup=get_city_keyboard(context, country))
        return

    # 🌍 Выбранная страна
    country = query.data.replace("country_", "")

    if country == "🌍 Other":
        context.user_data["awaiting_custom_country"] = True
        if context.user_data.get("editing_location"):
            context.user_data["editing_custom_country"] = True
        await query.message.reply_text(TEXT2[lang]["ask_custom_country"])
        return

    # Обновляем user_sessions
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]["country"] = country
    user_sessions[user_id]["selected_country"] = country
    context.user_data["selected_country"] = country

    if context.user_data.get("editing_location"):
        await save_partial_profile(user_id, context)
        await query.message.reply_text(TEXT2[lang]["ask_city_again"],
                                       reply_markup=get_city_keyboard(context, country))
        return

    # Регистрация
    await save_partial_profile(user_id, context)
    await query.message.reply_text(TEXT2[lang]["country_saved"].format(country=country))
    await query.message.reply_text(TEXT2[lang]["ask_city"])
    await asyncio.sleep(1)
    await query.message.reply_text(TEXT2[lang]["ask_city_choose"],
                                   reply_markup=get_city_keyboard(context, country))

async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # --- Рассылка: выбор города для broadcast ---
    if context.user_data.get("broadcast_stage") == "select_city":
        city = query.data.replace("city_", "")
        context.user_data["broadcast_city"] = city
        context.user_data["broadcast_stage"] = "awaiting_media"
        await query.message.reply_text("📨 Пришли текст объявления (можно с фото).")
        return

    # --- Пагинация списка городов ---
    if query.data.startswith("city_page_"):
        page = int(query.data.split("_")[-1])
        country = context.user_data.get("selected_country", "🌍 Other")
        await query.message.edit_reply_markup(reply_markup=get_city_keyboard(context, country, page))
        return

    # --- Кастомный город ---
    if query.data == "city_custom":
        # ВЕТКА ФИЛЬТРОВ: своя механика кастомного города
        if context.user_data.get("filters_city_flow"):
            context.user_data["filters_city_wait_custom"] = True
            await query.message.reply_text(TEXT2[lang]["ask_custom_city"])
            return
        # Обычная (регистрация/редактирование профиля)
        context.user_data["awaiting_custom_city"] = True
        await query.message.reply_text(TEXT2[lang]["ask_custom_city"])
        return

    # --- Скип фото (не трогаем) ---
    if query.data == "skip_photo":
        context.user_data["awaiting_photo"] = False
        await query.message.reply_text(TEXT2[lang]["skip_photo_notice"])

        type_keyboard = [[
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"], callback_data="type_difficulty"),
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"], callback_data="type_bouldering")
        ], [
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_any"], callback_data="type_both")
        ]]

        await query.message.reply_text(
            TEXT2[lang]["ask_climb_type"],
            reply_markup=InlineKeyboardMarkup(type_keyboard)
        )
        return

    # 🏙️ Обычный выбор города
    city = query.data.replace("city_", "")

    # === ВЕТКА ФИЛЬТРОВ ПОИСКА (filters_city_flow): НЕ трогаем профиль ===
    if context.user_data.get("filters_city_flow"):
        # Если выбран конкретный город — сохраняем в фильтры и возвращаемся к меню фильтров
        await upsert_search_filters(user_id, city_override=city)
        context.user_data["filters_city_flow"] = False
        context.user_data.pop("filters_city_wait_custom", None)
        context.user_data.pop("filters_city_country", None)

        # БЕЗ удаления сообщений! Просто отправляем новое сообщение с обновленным меню фильтров
        # Максимально быстро и удобно
        keyboard = [
            [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
            [KeyboardButton(TEXTS[lang]["search_back"])]
        ]
        search_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await show_filters_menu(query.message, context, user_id, lang, force_new=True, reply_keyboard_markup=search_keyboard)
        return

    # === ДАЛЬШЕ — СТАРАЯ МЕХАНИКА (регистрация/редактирование профиля) ===
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]["city"] = city
    user_sessions[user_id]["selected_city"] = city
    context.user_data["selected_city"] = city

    if context.user_data.get("editing_location"):
        await save_partial_profile(user_id, context)
        context.user_data["editing_location"] = False

        keyboard = [
            [KeyboardButton(TEXTS[lang]["form_edit"])],
            [KeyboardButton(TEXTS[lang]["form_delete"])],
            [KeyboardButton(TEXTS[lang]["form_back"])]
        ]

        await query.message.reply_text(
            TEXT2[lang]["city_saved_again"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        # ✅ Затем форсим меню профиля с сохранённой локацией
        from types import SimpleNamespace
        fake_update = SimpleNamespace(effective_user=update.effective_user, message=query.message, callback_query=None)
        await edit_profile_menu(fake_update, context, force_new=True)
        return

    # Регистрация
    await save_partial_profile(user_id, context)
    await query.message.reply_text(TEXT2[lang]["city_saved"])

    # 🔽 Кнопки выбора типа лазания
    type_keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"], callback_data="type_difficulty"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"], callback_data="type_bouldering")
    ], [
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_any"], callback_data="type_both")
    ]]

    await query.message.reply_text(
        TEXT2[lang]["ask_climb_type"],
        reply_markup=InlineKeyboardMarkup(type_keyboard)
    )

# ✨ УНИВЕРСАЛЬНЫЙ HANDLER: Выбор города из результатов Geoapify (регистрация/редактирование/фильтры)
async def handle_city_geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора города из результатов Geoapify (city_geo_0, city_geo_1, etc.)
    Поддерживает 3 сценария: регистрация, редактирование локации, фильтр города
    """
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass  # Игнорируем "Query is too old"
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Ручной ввод города
    if query.data == "city_geo_manual":
        # Сохраняем флаги редактирования/фильтрации перед переходом
        if context.user_data.get("editing_location_via_geo"):
            context.user_data["editing_location_manual"] = True
        elif context.user_data.get("filtering_city_via_geo"):
            context.user_data["filtering_city_manual"] = True

        set_state(context, "awaiting_custom_city")
        await query.message.reply_text(TEXT2[lang]["ask_custom_city"])
        return

    # Выбор города из результатов (city_geo_0, city_geo_1, etc.)
    try:
        idx = int(query.data.replace("city_geo_", ""))
        cities = context.user_data.get("city_search_results", [])

        if not cities or idx >= len(cities):
            await query.message.reply_text(TEXT2[lang]["city_search_error"])
            set_state(context, "awaiting_city_search")
            await query.message.reply_text(TEXT2[lang]["ask_city_search"])
            return

        selected = cities[idx]

        # ========== СЦЕНАРИЙ 1: РЕГИСТРАЦИЯ (default) ==========
        if not context.user_data.get("editing_location_via_geo") and not context.user_data.get("filtering_city_via_geo"):
            if user_id not in user_sessions:
                user_sessions[user_id] = {}

            user_sessions[user_id]["city"] = selected["city"]
            user_sessions[user_id]["country"] = selected["country"]
            user_sessions[user_id]["selected_city"] = selected["city"]
            user_sessions[user_id]["selected_country"] = selected["country"]
            context.user_data["selected_city"] = selected["city"]
            context.user_data["selected_country"] = selected["country"]

            context.user_data.pop("city_search_results", None)

            await save_partial_profile(user_id, context)

            await query.message.reply_text(
                TEXT2[lang].get("city_saved_geo", TEXT2[lang]["city_saved"]).format(
                    city=selected["display_name"]
                ),
                reply_markup=get_progress_keyboard(3, lang)
            )

            # Следующий шаг — выбор типа лазания
            type_keyboard = [[
                InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"], callback_data="type_difficulty"),
                InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"], callback_data="type_bouldering")
            ], [
                InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_any"], callback_data="type_both")
            ]]

            await query.message.reply_text(
                TEXT2[lang]["ask_climb_type"],
                reply_markup=InlineKeyboardMarkup(type_keyboard)
            )

        # ========== СЦЕНАРИЙ 2: РЕДАКТИРОВАНИЕ ЛОКАЦИИ ==========
        elif context.user_data.get("editing_location_via_geo"):
            async with db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users SET city = $1, country = $2 WHERE user_id = $3
                """, selected["city"], selected["country"], user_id)

                # 🔄 СИНХРОНИЗАЦИЯ: если Boost неактивен, обновляем city_override
                boost_row = await conn.fetchrow(
                    "SELECT boost_expires_at FROM users WHERE user_id = $1", user_id
                )
                boost_active = boost_row and boost_row['boost_expires_at'] and boost_row['boost_expires_at'] > datetime.now()
                if not boost_active:
                    await conn.execute(
                        "UPDATE search_filters SET city_override = $1 WHERE user_id = $2",
                        selected["city"], user_id
                    )

            context.user_data["editing_location_via_geo"] = False
            context.user_data.pop("city_search_results", None)

            # ✅ Сначала отправляем сообщение "Город сохранён" с форсированием меню кнопок
            keyboard = [
                [KeyboardButton(TEXTS[lang]["form_edit"])],
                [KeyboardButton(TEXTS[lang]["form_delete"])],
                [KeyboardButton(TEXTS[lang]["form_back"])]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await query.message.reply_text(
                TEXT2[lang].get("city_saved", "✅ Город сохранён!"),
                reply_markup=reply_markup
            )

            # ✅ Затем форсим меню профиля с сохранённой локацией
            from types import SimpleNamespace
            fake_update = SimpleNamespace(effective_user=update.effective_user, message=query.message, callback_query=None)
            await edit_profile_menu(fake_update, context, force_new=True)

        # ========== СЦЕНАРИЙ 3: ФИЛЬТР ГОРОДА ==========
        elif context.user_data.get("filtering_city_via_geo"):
            await upsert_search_filters(user_id, city_override=selected["city"])
            context.user_data["filtering_city_via_geo"] = False
            context.user_data.pop("city_search_results", None)

            # Отправляем сообщение "Город сохранён" с форсированием меню кнопок
            keyboard = [
                [KeyboardButton(TEXTS[lang]["search_next_person"])],
                [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
                [KeyboardButton(TEXTS[lang]["search_back"])]
            ]
            search_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await query.message.reply_text(
                TEXT2[lang].get("city_saved", "✅ Город сохранён!"),
                reply_markup=search_keyboard
            )

            # Отправляем меню фильтров с инлайн кнопками
            await show_filters_menu(query.message, context, user_id, lang, force_new=True, reply_keyboard_markup=None)

    except (ValueError, IndexError) as e:
        print(f"❌ Ошибка выбора города: {e}")
        await query.message.reply_text(TEXT2[lang]["city_search_error"])
        set_state(context, "awaiting_city_search")
        await query.message.reply_text(TEXT2[lang]["ask_city_search"])

async def handle_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # ✅ Установка заглушки по полу
    gender = user_sessions[user_id].get("gender", "other")
    from random import choice
    selected_url = choice(PLACEHOLDER_URLS.get(gender, PLACEHOLDER_URLS["other"]))
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(selected_url)
        if response.status_code == 200:
            user_sessions[user_id]["photo_bytes"] = response.content
            user_sessions[user_id]["has_real_photo"] = False  # ✅ Это заглушка!
    except Exception as e:
        print(f"⚠️ Ошибка при загрузке заглушки: {e}")

    await save_partial_profile(user_id)

    # ✅ Следующий шаг — выбор веса
    await query.message.reply_text(TEXT2[lang]["ask_weight"],
       reply_markup=get_weight_keyboard(page=2, lang=lang, prefix="weightval_"))



async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    gender = query.data.replace("gender_", "")

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    if gender == "skip":
        user_sessions[user_id]["gender"] = "other"
    else:
        user_sessions[user_id]["gender"] = gender
        await query.message.reply_text(TEXT2[lang]["gender_saved"].format(
            gender=get_gender_label(gender, lang)),
                                       reply_markup=get_progress_keyboard(6, lang))

    await save_partial_profile(user_id)

    # 📸 После выбора пола — спрашиваем фото с кнопкой пропуска
    keyboard = [[
        InlineKeyboardButton(TEXT2[lang]["btn_skip"],
                             callback_data="skip_photo_registration")
    ]]
    await query.message.reply_text(
        TEXT2[lang]["ask_photo"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    set_state(context, "awaiting_photo")


async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    weight = query.data.replace("weight_", "")

    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]["weight"] = weight
    await save_partial_profile(user_id)

    weight_display = get_weight_label(weight, lang)
    await query.message.reply_text(
        TEXT2[lang]["weight_saved"].format(weight=weight_display),
        reply_markup=get_progress_keyboard(8, lang))

    context.user_data["awaiting_bio"] = True

    keyboard = [[
        InlineKeyboardButton(TEXT2[lang]["btn_skip"],
                             callback_data="skip_bio")
    ]]
    await query.message.reply_text(TEXT2[lang]["ask_bio"],
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_skip_weight(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]["weight"] = None

    await save_partial_profile(user_id)

    context.user_data["awaiting_bio"] = True

    keyboard = [[
        InlineKeyboardButton(TEXT2[lang]["btn_skip"],
                             callback_data="skip_bio")
    ]]
    await query.message.reply_text(TEXT2[lang]["ask_bio"],
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_skip_photo_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск фото при регистрации - загружает заглушку"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    context.user_data["awaiting_photo"] = False

    # Загружаем заглушку
    user_sessions[user_id] = user_sessions.get(user_id, {})
    gender = user_sessions[user_id].get("gender", "other").lower()
    from random import choice
    selected_url = choice(PLACEHOLDER_URLS.get(gender, PLACEHOLDER_URLS["other"]))
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(selected_url)
        if response.status_code == 200:
            user_sessions[user_id]["photo_bytes"] = response.content
            user_sessions[user_id]["has_real_photo"] = False  # ✅ Это заглушка!
    except Exception as e:
        print(f"⚠️ Ошибка при загрузке заглушки: {e}")

    await save_partial_profile(user_id)
    await query.message.reply_text(TEXT2[lang]["skip_photo_notice"])

    # Переходим на вес
    await query.message.reply_text(TEXT2[lang]["ask_weight"],
       reply_markup=get_weight_keyboard(page=2, lang=lang, prefix="weightval_"))


async def handle_skip_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    user_sessions[user_id] = user_sessions.get(user_id, {})
    user_sessions[user_id]["bio"] = None
    await save_partial_profile(user_id)

    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_finish_registration"],
                             callback_data="finish_registration")
    ]]

    await query.message.reply_text(TEXT2[lang]["bio_skipped"],
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_finish_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ Завершение регистрации вызвано")
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    invited_by = context.user_data.get("invited_by")  # <-- критическая строка
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    data = user_sessions.get(user_id, {})

    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE registration_times SET finish_time = NOW() WHERE user_id = $1",
            user_id
        )

    await save_partial_profile(user_id, context)

    await query.message.reply_text(TEXT2[lang]["registration_done"])

    # 🎁 Рефералка — начисляем ТОЛЬКО если пользователь регистрируется впервые
    async with db_pool.acquire() as conn:
        already_referred = await conn.fetchval("SELECT COUNT(*) FROM referrals WHERE invited_id = $1",
                       user_id)

    if invited_by and invited_by != user_id and already_referred == 0:
        print(f"🎁 User {invited_by} пригласил {user_id} — активирован")
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO referrals (inviter_id, invited_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                invited_by, user_id
            )
            await conn.execute(
                "UPDATE referrals SET activated = 1 WHERE invited_id = $1",
                user_id
            )

            daily_total = await conn.fetchval(
                """
                SELECT SUM(change)
                FROM magnesium_log
                WHERE user_id = $1
                  AND reason LIKE 'Приглашение пользователя %%'
                  AND timestamp >= DATE_TRUNC('day', NOW())
                """,
                invited_by
            ) or 0

        if daily_total + 10 <= 50:
            await add_magnesium(invited_by,
                          10,
                          reason=f"Приглашение пользователя {user_id}")
            try:
                current_balance = await get_magnesium(invited_by)
                await context.bot.send_message(
                    chat_id=invited_by,
                    text=TEXT2[lang]["magnesium_gift"].format(
                        balance=current_balance
                    )
                )
            except Exception as e:
                print("⚠️ Ошибка отправки магнезии:", e)
        else:
            print(
                f"❌ {invited_by} превысил лимит магнезии за день ({daily_total} г)"
            )

        try:
            await context.bot.send_message(
                chat_id=invited_by,
                text=TEXT2[lang]["referral_thanks"]
            )
        except Exception as e:
            print("⚠️ Не удалось отправить сообщение пригласившему:", e)

    # 🖼️ Анкета — формат как в show_profile_preview
    from io import BytesIO

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

    if not row:
        await query.message.reply_text(TEXT2[lang]["profile_not_found"])
    else:
        data_db = dict(row)

        # --- те же расчёты, что и в edit_profile_menu/show_profile_preview ---

        difficulty_raw = DIFFICULTY_LABELS.get(
            data_db.get("difficulty"),
            data_db.get("difficulty") or TEXT2[lang]["not_specified"]
        )
        difficulty_display = escape_markdown(difficulty_raw)

        climb_type_raw = get_climb_label(
            data_db.get("climb_type", ""),
            lang
        ) if data_db.get("climb_type") else TEXT2[lang]["not_specified"]
        climb_type_display = escape_markdown(climb_type_raw)

        gender_raw = get_gender_label(
            data_db.get("gender", ""),
            lang
        ) if data_db.get("gender") else TEXT2[lang]["not_specified"]
        gender_display = escape_markdown(gender_raw)

        weight_raw = get_weight_label(
            data_db.get("weight", ""),
            lang
        ) if data_db.get("weight") else TEXT2[lang]["not_specified"]
        weight_display = escape_markdown(weight_raw)

        country_display = escape_markdown(data_db.get("country") or "—")
        city_value = (
            data_db.get("city_other")
            if data_db.get("city") == "Другой"
            else data_db.get("city", "—")
        )
        city_display = (
            escape_markdown(city_value)
            if city_value else TEXT2[lang]["not_specified"]
        )

        # Лайки (используем денормализованное поле)
        async with db_pool.acquire() as conn:
            likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", user_id)
        likes_count = likes_count or 0  # Fallback на 0 если NULL
        likes_display_raw = (
            "1M+" if likes_count >= 1_000_000
            else f"{likes_count // 1000}K+" if likes_count >= 1000
            else str(likes_count)
        )
        likes_display = escape_markdown(likes_display_raw)

        # Статус
        async with db_pool.acquire() as conn:
            row_status = await conn.fetchrow("SELECT status_slug FROM users WHERE user_id = $1", user_id)
        status_slug = row_status['status_slug'] if row_status else None

        def render_status_line_local(lang: str, slug: str | None) -> str:
            if not slug:
                return ""
            opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
            raw = opts_map.get(slug, "")
            return f"*{escape_markdown(raw)}*" if raw else ""

        # Имя + эмодзи Boost
        name_raw = data_db.get("name", "—")
        name_with_boost = await add_boost_emoji_to_name(name_raw, user_id)

        caption_lines = [
            f"{TEXT2[lang]['profile_user']}: *{escape_markdown(name_with_boost)}*",
            f"{TEXT2[lang]['field_type']}: {climb_type_display} I {difficulty_display}",
            f"{TEXT2[lang]['field_country']}: {country_display}",
            f"{TEXT2[lang]['field_city']}: {city_display or TEXT2[lang]['not_specified']}",
            f"{TEXT2[lang]['field_gender']}: {gender_display}",
            f"{TEXT2[lang]['field_weight']}: {weight_display}\n",
            f"❤️ {likes_display}"
        ]

        # Убираем пустые строки
        caption_lines = [line for line in caption_lines if line]

        if data_db.get("bio"):
            caption_lines.append(f"📝 {escape_markdown(data_db['bio'])}")

        caption = "\n".join(caption_lines)

        try:
            photo_bytes = data_db.get("photo_bytes")

            if photo_bytes:
                image_io = BytesIO(photo_bytes)
                image_io.name = "photo.jpg"
                image_io.seek(0)

                await query.message.reply_photo(
                    photo=image_io,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    protect_content=True
                )
            else:
                await query.message.reply_text(
                    caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        except Exception as e:
            print("⚠️ Ошибка при отправке анкеты (finish_registration):", e)
            await query.message.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )

    await asyncio.sleep(1)

    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search"],
                             callback_data="go_to_search_menu")
    ]]

    # Главное меню кнопок — прикрепляем к этому сообщению
    menu_buttons = [
        [
            KeyboardButton(TEXTS[lang]["menu_likes"]),
            KeyboardButton(TEXTS[lang]["menu_search"])
        ],
        [
            KeyboardButton(TEXTS[lang]["menu_chats"]),
            KeyboardButton(TEXTS[lang]["menu_board"])
        ],
        [
            KeyboardButton(TEXTS[lang]["menu_form"]),
            KeyboardButton(TEXTS[lang]["menu_chalk"]),
            KeyboardButton(TEXTS[lang]["menu_about"])
        ]
    ]

    await query.message.reply_text(
        TEXT2[lang]["go_to_search"],
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.message.reply_text(
        TEXT2[lang]["menu_main"],
        reply_markup=ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    )

    reset_user_flags(context, user_id)

    user_city = data.get("city_other") if data.get("city") == "Другой" else data.get("city")
    if user_city:
        await send_city_push_if_needed(context, user_id, user_city)
    else:
        # Fallback: берём город из БД
        async with db_pool.acquire() as conn:
            db_city = await conn.fetchval("SELECT city FROM users WHERE user_id = $1", user_id)
        if db_city:
            await send_city_push_if_needed(context, user_id, db_city)

    reset_user_context(context)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    text = update.message.text.strip()
    state = get_state(context)

    # === АДМИН: Локальная рассылка - ввод города через Geoapify ===
    if context.user_data.get("broadcast_stage") == "awaiting_broadcast_city":
        # Запрос к Geoapify
        cities = await geoapify_search_city(text, limit=5, user_id=None)

        if not cities:
            await update.message.reply_text(
                "❌ Города не найдены. Попробуйте другое название."
            )
            return

        # Показываем результаты с кнопками выбора
        keyboard = []
        for idx, city_data in enumerate(cities):
            city = city_data["city"]
            country = city_data["country"]
            flag = city_data.get("flag", "")

            button_text = f"{flag} {city}, {country}"
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=f"admin_broadcast_city_{idx}")
            ])

        # Сохраняем результаты в context
        context.user_data["broadcast_city_results"] = cities

        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="admin_broadcast_menu")])

        await update.message.reply_text(
            "📢 Выберите город для рассылки:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # === АДМИН: Локальная рассылка - ввод текста сообщения ===
    if context.user_data.get("broadcast_stage") == "awaiting_broadcast_message":
        city = context.user_data.get("broadcast_city")

        # Получаем всех пользователей из этого города
        async with db_pool.acquire() as conn:
            users = await conn.fetch("""
                SELECT user_id FROM users
                WHERE city = $1
            """, city)

        if not users:
            await update.message.reply_text(f"❌ В городе {city} нет пользователей.")
            context.user_data["broadcast_stage"] = None
            return

        # Рассылка сообщения
        success_count = 0
        fail_count = 0

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=f"📢 Сообщение для вашего города:\n\n{text}"
                )
                success_count += 1
                await asyncio.sleep(0.05)  # Защита от rate limit
            except Exception as e:
                fail_count += 1
                print(f"❌ Ошибка отправки сообщения пользователю {user['user_id']}: {e}")

        await update.message.reply_text(
            f"✅ Рассылка завершена!\n\n"
            f"📊 Город: {city}\n"
            f"✅ Отправлено: {success_count}\n"
            f"❌ Ошибок: {fail_count}"
        )

        context.user_data["broadcast_stage"] = None
        context.user_data.pop("broadcast_city", None)
        context.user_data.pop("broadcast_city_results", None)
        return

    # === ФИЛЬТРЫ ПОИСКА: кастомный город после выбора "Другой" ===
    if context.user_data.get("filters_city_flow") and context.user_data.get("filters_city_wait_custom"):
        error = validate_text(text, lang=lang, max_length=40)
        if error:
            await update.message.reply_text(error)
            return

        await upsert_search_filters(user_id, city_override=text)

        # завершаем поток выбора города для фильтров
        context.user_data["filters_city_flow"] = False
        context.user_data["filters_city_wait_custom"] = False
        context.user_data.pop("filters_city_country", None)

        # БЕЗ удаления сообщений! Просто отправляем новое сообщение с обновленным меню фильтров
        keyboard = [
            [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
            [KeyboardButton(TEXTS[lang]["search_back"])]
        ]
        search_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await show_filters_menu(update.message, context, user_id, lang, force_new=True, reply_keyboard_markup=search_keyboard)
        return

    if state == "awaiting_name2":
        error = validate_text(text, lang=lang, max_length=30)
        if error:
            await update.message.reply_text(error)
            return

        if contains_emoji(text):
            await update.message.reply_text(TEXT2[lang]["err_emoji_in_name"])
            return

        clear_states(context)

        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET name = $1 WHERE user_id = $2",
                           text, user_id)

        # ✅ Форсируем кнопки меню Профиль
        keyboard = [
            [KeyboardButton(TEXTS[lang]["form_edit"])],
            [KeyboardButton(TEXTS[lang]["form_delete"])],
            [KeyboardButton(TEXTS[lang]["form_back"])]
        ]

        # ✅ Отправляем отбивку И форсируем меню профиля
        await update.message.reply_text(TEXT2[lang].get("saved"), reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

        from types import SimpleNamespace
        fake_update = SimpleNamespace(effective_user=update.effective_user, message=update.message, callback_query=None)
        await edit_profile_menu(fake_update, context, force_new=True)

    if state == "awaiting_name":
        error = validate_text(text, lang=lang, max_length=30)
        if error:
            await update.message.reply_text(error)
            return

        if contains_emoji(text):
            await update.message.reply_text(TEXT2[lang]["err_emoji_in_name"])
            return

        user_sessions[user_id] = user_sessions.get(user_id, {})
        user_sessions[user_id]["name"] = text
        await save_partial_profile(user_id)
        clear_states(context)

        await update.message.reply_text(TEXT2[lang]["name_saved"],
                                        reply_markup=get_progress_keyboard(2, lang))

        # ✨ НОВАЯ МЕХАНИКА: Geoapify автокомплит вместо выбора страны/города
        set_state(context, "awaiting_city_search")
        await update.message.reply_text(TEXT2[lang]["ask_city_search"])
        return

    # ✨ НОВЫЙ STATE: Поиск города через Geoapify (регистрация)
    if state == "awaiting_city_search":
        clear_states(context)

        if len(text) < 2:
            await update.message.reply_text(TEXT2[lang]["city_search_too_short"])
            set_state(context, "awaiting_city_search")
            return

        # Вызов Geoapify API с rate limiting
        cities = await geoapify_search_city(text, limit=5, user_id=user_id)

        if not cities:
            await update.message.reply_text(TEXT2[lang]["city_search_no_results"])
            set_state(context, "awaiting_city_search")
            return

        # Сохраняем результаты в context для последующего выбора
        context.user_data["city_search_results"] = cities

        # Формируем кнопки
        keyboard = []
        for idx, city_data in enumerate(cities):
            keyboard.append([InlineKeyboardButton(
                city_data["display_name"], 
                callback_data=f"city_geo_{idx}"
            )])

        # Кнопка "Ввести вручную" на случай если не нашли нужный город
        keyboard.append([InlineKeyboardButton(
            TEXT2[lang]["city_search_manual"], 
            callback_data="city_geo_manual"
        )])

        await update.message.reply_text(
            TEXT2[lang]["city_search_results"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if state == "awaiting_custom_country":
        error = validate_text(text, lang=lang, max_length=40)
        if error:
            await update.message.reply_text(error)
            return

        user_sessions[user_id] = user_sessions.get(user_id, {})
        user_sessions[user_id]["country"] = text
        user_sessions[user_id]["country_other"] = text
        user_sessions[user_id]["selected_country"] = text
        context.user_data["selected_country"] = text

        if context.user_data.get("editing_custom_country"):
            # продолжаем как редактирование
            context.user_data["editing_custom_country"] = False
            context.user_data["editing_location"] = True
            set_state(context, "awaiting_custom_city")
            await update.message.reply_text(TEXT2[lang]["ask_custom_city"])
        else:
            # регистрация
            set_state(context, "awaiting_custom_city")
            await update.message.reply_text(
                TEXT2[lang]["country_saved"].format(country=text))
            await update.message.reply_text(TEXT2[lang]["ask_custom_city"])

        await save_partial_profile(user_id, context)
        return


    # ✨ НОВЫЙ STATE: Редактирование локации через Geoapify
    if state == "awaiting_edit_location_search":
        clear_states(context)

        if len(text) < 2:
            await update.message.reply_text(TEXT2[lang]["city_search_too_short"])
            set_state(context, "awaiting_edit_location_search")
            return

        # Вызов Geoapify API с rate limiting
        cities = await geoapify_search_city(text, limit=5, user_id=user_id)

        if not cities:
            await update.message.reply_text(TEXT2[lang]["city_search_no_results"])
            set_state(context, "awaiting_edit_location_search")
            return

        # Сохраняем результаты и помечаем что это редактирование
        context.user_data["city_search_results"] = cities
        context.user_data["editing_location_via_geo"] = True

        # Формируем кнопки
        keyboard = []
        for idx, city_data in enumerate(cities):
            keyboard.append([InlineKeyboardButton(
                city_data["display_name"], 
                callback_data=f"city_geo_{idx}"
            )])

        keyboard.append([InlineKeyboardButton(
            TEXT2[lang]["city_search_manual"], 
            callback_data="city_geo_manual"
        )])

        await update.message.reply_text(
            TEXT2[lang]["city_search_results"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ✨ НОВЫЙ STATE: Фильтр города через Geoapify
    if state == "awaiting_filter_city_search":
        clear_states(context)

        if len(text) < 2:
            await update.message.reply_text(TEXT2[lang]["city_search_too_short"])
            set_state(context, "awaiting_filter_city_search")
            return

        # Вызов Geoapify API с rate limiting
        cities = await geoapify_search_city(text, limit=5, user_id=user_id)

        if not cities:
            await update.message.reply_text(TEXT2[lang]["city_search_no_results"])
            set_state(context, "awaiting_filter_city_search")
            return

        # Сохраняем результаты и помечаем что это фильтр
        context.user_data["city_search_results"] = cities
        context.user_data["filtering_city_via_geo"] = True

        # Формируем кнопки
        keyboard = []
        for idx, city_data in enumerate(cities):
            keyboard.append([InlineKeyboardButton(
                city_data["display_name"], 
                callback_data=f"city_geo_{idx}"
            )])

        # Кнопка очистки фильтра
        keyboard.append([InlineKeyboardButton(
            TEXT2[lang].get("filters_city_clear", "Очистить фильтр"), 
            callback_data="filters_city_clear"
        )])

        await update.message.reply_text(
            TEXT2[lang]["city_search_results"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if state == "awaiting_custom_city":
        error = validate_text(text, lang=lang, max_length=40)
        if error:
            await update.message.reply_text(error)
            return

        # ========== СЦЕНАРИЙ 1: РЕДАКТИРОВАНИЕ ЛОКАЦИИ (ручной ввод) ==========
        if context.user_data.get("editing_location_manual"):
            async with db_pool.acquire() as conn:
                # Определяем страну через Geoapify
                cities = await geoapify_search_city(text, limit=1, user_id=user_id)
                country = cities[0]["country"] if cities else "—"

                # Сохраняем в БД
                await conn.execute("""
                    UPDATE users SET city = $1, country = $2 WHERE user_id = $3
                """, text, country, user_id)

                # 🔄 СИНХРОНИЗАЦИЯ: если Boost неактивен, обновляем city_override
                boost_row = await conn.fetchrow(
                    "SELECT boost_expires_at FROM users WHERE user_id = $1", user_id
                )
                boost_active = boost_row and boost_row['boost_expires_at'] and boost_row['boost_expires_at'] > datetime.now()
                if not boost_active:
                    await conn.execute(
                        "UPDATE search_filters SET city_override = $1 WHERE user_id = $2",
                        text, user_id
                    )

            context.user_data["editing_location_manual"] = False

            # Возвращаемся к меню редактирования профиля
            keyboard = [
                [KeyboardButton(TEXTS[lang]["form_edit"])],
                [KeyboardButton(TEXTS[lang]["form_delete"])],
                [KeyboardButton(TEXTS[lang]["form_back"])]
            ]
            await update.message.reply_text(
                TEXT2[lang].get("city_saved_again", "✅ Ваш город сохранён."),
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )

            clear_states(context)
            return

        # ========== СЦЕНАРИЙ 2: ФИЛЬТР ГОРОДА (ручной ввод) ==========
        elif context.user_data.get("filtering_city_manual"):
            await upsert_search_filters(user_id, city_override=text)
            context.user_data["filtering_city_manual"] = False

            await update.message.reply_text(
                TEXT2[lang].get("filter_city_saved", "✅ Фильтр города сохранён!")
            )

            # Возвращаемся к меню поиска
            keyboard = [
                [KeyboardButton(TEXTS[lang]["search_next_person"])],
                [KeyboardButton(TEXTS[lang]["search_location"])],
                [KeyboardButton(TEXTS[lang]["search_back"])]
            ]
            await update.message.reply_text(
                TEXT2[lang].get("menu_search", "🔍 Меню поиска"),
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            clear_states(context)
            return

        # ========== СЦЕНАРИЙ 3: РЕГИСТРАЦИЯ (default) ==========
        user_sessions[user_id] = user_sessions.get(user_id, {})
        user_sessions[user_id]["city"] = text
        user_sessions[user_id]["city_other"] = text
        user_sessions[user_id]["selected_city"] = text
        context.user_data["selected_city"] = text

        # ✅ ФИКС: Пытаемся определить страну через Geoapify при ручном вводе
        cities = await geoapify_search_city(text, limit=1, user_id=user_id)
        if cities:
            # Берём первый результат и сохраняем страну
            user_sessions[user_id]["country"] = cities[0]["country"]
            user_sessions[user_id]["selected_country"] = cities[0]["country"]
            context.user_data["selected_country"] = cities[0]["country"]
            print(f"✅ Город {text} → страна {cities[0]['country']}")
        else:
            # Если не нашли - ставим прочерк
            user_sessions[user_id]["country"] = "—"
            user_sessions[user_id]["selected_country"] = "—"
            context.user_data["selected_country"] = "—"
            print(f"⚠️ Город {text} не найден в Geoapify, страна не определена")

        await save_partial_profile(user_id, context)

        await update.message.reply_text(TEXT2[lang]["city_saved"])

        # ⬇️ Переход к выбору типа лазания (вместо фото)
        clear_states(context)  # сбрасываем состояние кастомного ввода

        type_keyboard = [[
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"], callback_data="type_difficulty"),
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"], callback_data="type_bouldering")
        ], [
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_any"], callback_data="type_both")
        ]]

        await update.message.reply_text(
            TEXT2[lang]["ask_climb_type"],
            reply_markup=InlineKeyboardMarkup(type_keyboard)
        )
        return


    if state == "awaiting_bio":
        error = validate_text(text, lang=lang, max_length=130)
        if error:
            keyboard = [[
                InlineKeyboardButton(TEXT2[lang]["btn_skip"],
                                     callback_data="skip_bio")
            ]]
            await update.message.reply_text(error)
            await update.message.reply_text(
                TEXT2[lang]["ask_bio_again"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        user_sessions[user_id]["bio"] = text.strip()
        await save_partial_profile(user_id)
        clear_states(context)

        keyboard = [[
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_finish_registration"],
                                 callback_data="finish_registration")
        ]]
        await update.message.reply_text(
            TEXT2[lang]["bio_saved"],
            reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if state == "awaiting_admin_password":
        context.user_data["awaiting_admin_password"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            ADMIN_IDS.append(update.effective_user.id)
            await update.message.reply_text("✅ Доступ разрешён.")
            await show_admin_menu(update)
        else:
            await update.message.reply_text("❌ Неверный пароль.")
        return

    if text == TEXTS[lang]["about_rules"]:
        await show_user_agreement(update, context, show_inline_button=False)
        return

    if text == TEXTS[lang]["about_home"]:
        await update.message.reply_text(TEXT2[lang]["start_returned"])
        await start(update, context)
        return

    if text == TEXTS[lang]["about_feedback"]:
        context.user_data["awaiting_feedback"] = True
        await update.message.reply_text(TEXT2[lang]["feedback_intro"])
        return

    if text == TEXTS[lang]["likes_mutual"]:
        await handle_mutual_likes(update, context)
        return

    if text == TEXTS[lang]["likes_received"]:
        await handle_liked_me(update, context)
        return

    if text == TEXTS[lang]["chalk_amount"]:
        balance = await get_magnesium(user_id)
        await update.message.reply_text(
            TEXT2[lang]["chalk_balance"].format(balance=balance))
        return

    if text == TEXTS[lang]["chalk_get"]:
        await update.message.reply_text(TEXT2[lang]["chalk_get"])
        return

    if text in [
            TEXTS[lang]["menu_form"], TEXTS[lang]["menu_search"],
            TEXTS[lang]["menu_likes"], TEXTS[lang]["menu_chats"],
            TEXTS[lang]["menu_chalk"], TEXTS[lang]["menu_about"],
            TEXTS[lang]["search_back"], TEXTS[lang]["menu_home"]
    ]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["form_edit"]:
        await edit_profile_menu(update, context)
        return

    if text == TEXTS[lang]["form_delete"]:
        await confirm_delete_profile(update, context)
        return

    # --- Ввод города для премиум-фильтра (🗯 Город) ---
    if context.user_data.get("sp_awaiting_city"):
        context.user_data["sp_awaiting_city"] = False
        city_text = text.strip()
        if city_text == "-":
            await upsert_search_filters(user_id, city_override=None)
            await update.message.reply_text(TEXT2[lang]["sp_city_cleared"])
        else:
            err = validate_text(city_text, lang=lang, max_length=40)
            if err:
                await update.message.reply_text(err)
                await update.message.reply_text(TEXT2[lang]["sp_city_prompt"])
                context.user_data["sp_awaiting_city"] = True
                return
            await upsert_search_filters(user_id, city_override=city_text)
            await update.message.reply_text(TEXT2[lang]["sp_city_saved"].format(city=city_text))
        await show_filters_menu(update.message, context, user_id, lang)
        return


    await handle_menu(update, context)


###################################################################################### SEARCH CRITERIA

async def handle_search_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    raw = q.data.replace("search_diff_", "")
    new_value = None if raw == "any" else raw

    f = await get_search_filters_row(user_id)
    old_value = f.get("difficulty")

    force_new = new_value == old_value
    if new_value != old_value:
        await upsert_search_filters(user_id, difficulty=new_value)
        context.user_data["filters_dirty"] = True

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)


async def handle_search_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    new_value = q.data.replace("search_type_", "")

    f = await get_search_filters_row(user_id)
    old_value = f.get("climb_type")

    force_new = new_value == old_value
    if new_value != old_value:
        await upsert_search_filters(user_id, climb_type=new_value)
        context.user_data["filters_dirty"] = True

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)


async def handle_search_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    new_value = q.data.replace("search_gender_", "")

    f = await get_search_filters_row(user_id)
    old_value = f.get("gender")

    force_new = new_value == old_value
    if new_value != old_value:
        await upsert_search_filters(user_id, gender=new_value)
        context.user_data["filters_dirty"] = True

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)


async def handle_search_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    value = q.data.replace("search_weight_", "")

    f = await get_search_filters_row(user_id)
    old_min, old_max = f.get("weight_min"), f.get("weight_max")

    if value == "any":
        new_min, new_max = None, None
    else:
        try:
            new_min, new_max = map(int, value.split("_"))
        except:
            new_min, new_max = old_min, old_max

    force_new = (new_min, new_max) == (old_min, old_max)
    if (new_min, new_max) != (old_min, old_max):
        await upsert_search_filters(user_id, weight_min=new_min, weight_max=new_max)
        context.user_data["filters_dirty"] = True

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)


async def load_search_batch_background(user_id: int, context: ContextTypes.DEFAULT_TYPE, batch_size: int = 100):
    """🔄 ФОНОВАЯ загрузка всех оставшихся анкет (агрессивная предзагрузка)"""
    start_time = asyncio.get_event_loop().time()
    max_duration = 300  # 5 минут максимум
    max_results = 500  # Максимум анкет для загрузки (защита от перегрузки памяти)

    try:
        # 🚀 АГРЕССИВНАЯ ПРЕДЗАГРУЗКА: загружаем ВСЕ оставшиеся анкеты сразу
        # Не ждём пока буфер опустеет — добавляем напрямую в search_results
        await asyncio.sleep(0.3)  # Небольшая задержка чтобы первая анкета успела отрисоваться

        while not context.user_data.get("search_exhausted", False):
            # ⏱ Проверяем таймаут
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_duration:
                print(f"⏱ Фоновая загрузка для {user_id} завершена по таймауту ({elapsed:.0f}с)")
                break

            # 🛡️ Проверяем лимит памяти
            current_results = context.user_data.get("search_results", [])
            if len(current_results) >= max_results:
                print(f"📦 Фоновая загрузка для {user_id} завершена по лимиту ({len(current_results)} анкет)")
                context.user_data["search_exhausted"] = True
                break

            search_params = context.user_data.get("search_params", {})

            try:
                async with db_pool.acquire() as conn:
                    query = search_params.get("query_template", "")
                    params = search_params.get("params", [])

                    # 🛡️ ИСКЛЮЧАЕМ уже показанные анкеты
                    seen_ids = context.user_data.get("search_seen_ids", set())

                    if seen_ids:
                        order_pos = query.upper().find("ORDER BY")
                        if order_pos > 0:
                            seen_list = ",".join(str(uid) for uid in seen_ids)
                            exclude_condition = f" AND u.user_id NOT IN ({seen_list}) "
                            query = query[:order_pos] + exclude_condition + query[order_pos:]

                    # Загружаем большой батч
                    params_with_limit = params + [0, batch_size]
                    raw_batch = await conn.fetch(query, *params_with_limit)

                    if raw_batch:
                        # Добавляем новые ID в seen_ids
                        for row in raw_batch:
                            seen_ids.add(row['user_id'])
                        context.user_data["search_seen_ids"] = seen_ids

                        # 🚀 НАПРЯМУЮ добавляем в results (не в буфер!)
                        context.user_data["search_results"].extend(list(raw_batch))

                        # Если загрузили меньше чем запросили — БД исчерпана
                        if len(raw_batch) < batch_size:
                            context.user_data["search_exhausted"] = True
                            break
                    else:
                        context.user_data["search_exhausted"] = True
                        break

            except Exception as e:
                print(f"❌ Ошибка в фоновой загрузке: {e}")
                context.user_data["search_exhausted"] = True
                break

            await asyncio.sleep(0.1)  # Минимальная пауза между батчами

    except asyncio.CancelledError:
        print(f"🛑 Фоновая загрузка для {user_id} отменена")
    except Exception as e:
        print(f"❌ Ошибка в задаче фоновой загрузки: {e}")


async def handle_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        await ensure_lang(context, user_id)
        lang = context.user_data["lang"]

        # 🔄 КРИТИЧНО: Сбрасываем кэш поиска при каждом новом запуске
        # Это гарантирует актуальные данные (новые регистрации, восстановленные профили, обновлённые фото)
        old_task = context.user_data.pop("search_background_task", None)
        if old_task and not old_task.done():
            old_task.cancel()
        context.user_data["search_results"] = []
        context.user_data["search_buffer"] = []
        context.user_data["search_page"] = 0
        context.user_data["search_exhausted"] = False
        context.user_data["search_loading"] = False
        context.user_data["search_seen_ids"] = set()

        async with db_pool.acquire() as conn:
            # 🚀 ОПТИМИЗАЦИЯ: 1 запрос вместо 3 (бан + город + фильтры + boost)
            init_row = await conn.fetchrow("""
                SELECT 
                    u.city, u.city_other, u.boost_expires_at,
                    sf.difficulty, sf.climb_type, sf.gender, sf.weight_min, sf.weight_max,
                    sf.has_photo, sf.status_slug, sf.city_override, sf.sort_popular,
                    EXISTS(SELECT 1 FROM hidden_users WHERE user_id = 0 AND hidden_user_id = $1 
                           AND (hide_until IS NULL OR hide_until > CURRENT_TIMESTAMP)) AS is_banned
                FROM users u
                LEFT JOIN search_filters sf ON sf.user_id = u.user_id
                WHERE u.user_id = $1
            """, user_id)

            if not init_row:
                await update.message.reply_text(TEXT2[lang]["search_needs_profile"])
                return

            if init_row['is_banned']:
                await update.message.reply_text(TEXT2[lang]["search_blocked"])
                return

            loading_msg = await update.message.reply_text(TEXT2[lang]["search_loading"])

            city, city_other = init_row['city'], init_row['city_other']
            user_city = city_other if city == "Другой" else city
            boost_expires_at = init_row['boost_expires_at']

            difficulty = init_row['difficulty']
            climb_type = init_row['climb_type']
            gender = init_row['gender']
            weight_min = init_row['weight_min']
            weight_max = init_row['weight_max']
            has_photo = init_row['has_photo']
            status_slug = init_row['status_slug']
            city_override = init_row['city_override']
            sort_popular = init_row['sort_popular']

            # 🔄 СИНХРОНИЗАЦИЯ: если Boost истёк, сбрасываем city_override на город профиля
            boost_active = boost_expires_at and boost_expires_at > datetime.now()
            if not boost_active and city_override and city_override != user_city:
                await conn.execute(
                    "UPDATE search_filters SET city_override = $1 WHERE user_id = $2",
                    user_city, user_id
                )
                city_override = user_city  # Используем город профиля

            search_city = city_override if city_override else user_city

            # 🚀 ОПТИМИЗИРОВАННЫЙ запрос: загружаем лайки и фото сразу
            base_where = """
                WHERE (u.city = $1 OR u.city_other = $1) AND u.user_id != $2
                  AND u.is_deleted = FALSE
                  AND u.user_id NOT IN (
                      SELECT hidden_user_id FROM hidden_users
                      WHERE user_id = $2 AND (hide_until IS NULL OR hide_until > CURRENT_TIMESTAMP)
                  )
            """
            params = [search_city, user_id]
            param_idx = 3

            if climb_type and climb_type.strip() != "any":
                base_where += f" AND u.climb_type = ${param_idx}"
                params.append(climb_type.strip())
                param_idx += 1

            if gender and gender.strip() != "any":
                base_where += f" AND u.gender = ${param_idx}"
                params.append(gender.strip())
                param_idx += 1

            # Фото-фильтр (три состояния: True — только с фото, False — только без фото, None — любое)
            if has_photo is True:
                base_where += " AND u.has_real_photo = TRUE"
            elif has_photo is False:
                base_where += " AND (u.has_real_photo = FALSE OR u.has_real_photo IS NULL)"

            # Премиум: статус
            if status_slug:
                base_where += f" AND u.status_slug = ${param_idx}"
                params.append(status_slug)
                param_idx += 1

            # Вес
            if weight_min is not None and weight_max is not None:
                base_where += f" AND u.weight ~ E'^\\\\d+$' AND CAST(u.weight AS INTEGER) BETWEEN ${param_idx} AND ${param_idx+1}"
                params.extend([weight_min, weight_max])
                param_idx += 2

            # 🚀 ШАБЛОН для фоновой загрузки (БЕЗ photo_bytes — ленивая загрузка!)
            sort_order = "COALESCE(u.likes_count, 0) DESC, RANDOM()" if sort_popular else "RANDOM()"
            query_template = f"""
                SELECT u.user_id, u.name, u.difficulty, u.climb_type, u.gender, u.weight, u.bio, u.status_slug,
                       COALESCE(u.likes_count, 0) AS likes_count, u.boost_expires_at, u.is_founder, u.has_real_photo
                FROM users u
                {base_where}
                ORDER BY {sort_order}
                OFFSET $({param_idx}) LIMIT $({param_idx + 1})
            """

            # 1️⃣ БЫСТРАЯ загрузка ПЕРВЫХ 5 анкет (минимум для моментальной выдачи)
            first_query = query_template.replace(f"$({param_idx})", "$" + str(param_idx)).replace(f"$({param_idx + 1})", "$" + str(param_idx + 1))
            first_params = params + [0, 5]
            raw_matches = await conn.fetch(first_query, *first_params)

        # Доп. фильтр по корзинам сложности (bucket)
        matches = raw_matches
        if difficulty and difficulty.strip() != "any":
            allowed = set(DIFFICULTY_BUCKETS.get(difficulty.strip(), []))
            if allowed:
                matches = [row for row in raw_matches if (row['difficulty'] is not None and row['difficulty'] in allowed)]

        if not matches:
            try:
                await loading_msg.delete()
            except Exception:
                pass

            # 🌍 ГЛОБАЛЬНЫЙ ПОИСК: проверяем, использовал ли пользователь эту возможность
            global_search_used = False
            async with db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT global_search_used FROM users WHERE user_id = $1", user_id
                )
                if row:
                    global_search_used = row['global_search_used'] or False

            if not global_search_used:
                # Первый раз видит search_empty — предлагаем глобальный поиск
                keyboard = [[InlineKeyboardButton(
                    TEXT2[lang]["search_empty_first_time_btn"],
                    callback_data="btn_global_search"
                )]]
                await update.message.reply_photo(
                    photo="https://postimg.cc/R6zWQySf",
                    caption=TEXT2[lang]["search_empty_first_time_offer"],
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                # Уже использовал — обычное сообщение
                await update.message.reply_photo(
                    photo="https://postimg.cc/R6zWQySf",
                    caption=TEXT2[lang]["search_empty"],
                    parse_mode=ParseMode.MARKDOWN
                )
            return

        # 🛑 ОТМЕНЯЕМ предыдущую фоновую задачу (предотвращаем накопление)
        old_task = context.user_data.get("search_background_task")
        if old_task and not old_task.done():
            old_task.cancel()
            print(f"🛑 Отменена предыдущая фоновая задача поиска для {user_id}")

        # 📦 ИНИЦИАЛИЗИРУЕМ структуру поиска
        context.user_data["search_results"] = matches
        context.user_data["search_page"] = 0
        context.user_data["search_buffer"] = []
        context.user_data["search_exhausted"] = False
        context.user_data["search_loading"] = False

        # 🛡️ ОТСЛЕЖИВАНИЕ ПОКАЗАННЫХ АНКЕТ (для предотвращения повторов)
        context.user_data["search_seen_ids"] = set(m['user_id'] for m in matches)

        # ✅ СОХРАНЯЕМ фильтры (включая все поля для проверки изменений)
        context.user_data["search_filters"] = {
            "weight_min": weight_min,
            "weight_max": weight_max,
            "has_photo": has_photo,
            "difficulty": difficulty,
            "climb_type": climb_type,
            "gender": gender,
            "city_override": city_override,
            "status_slug": status_slug
        }

        # 💾 СОХРАНЯЕМ параметры для фоновой загрузки
        context.user_data["search_params"] = {
            "query_template": first_query,
            "params": params,
            "offset": 5  # Следующая партия с offset 5
        }

        # ⚡ ПОКАЗЫВАЕМ первую анкету СРАЗУ (skip_init=True чтобы не было рекурсии!)
        await show_next_search_result(update, context, skip_init=True)

        # ✅ Удаляем сообщение "⏳ Ищу..."
        try:
            await loading_msg.delete()
        except Exception:
            pass

        # 🔄 ЗАПУСКАЕМ фоновую загрузку батчей (не ждём, идёт параллельно)
        task = asyncio.create_task(load_search_batch_background(user_id, context))
        context.user_data["search_background_task"] = task  # Сохраняем для отмены
    except Exception as e:
        print(f"❌ Ошибка в handle_search_command: {e}")
        pass  # Молча игнорируем (возможно expired query)


async def handle_global_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    🌍 ГЛОБАЛЬНЫЙ ПОИСК: показывает 10 профилей из разных стран (минимум 2).
    Используется только один раз для пользователей с пустым результатом поиска.
    """
    query = update.callback_query
    await query.answer()

    # 🗑 Удаляем сообщение с кнопкой "Show" чтобы предотвратить повторные нажатия
    try:
        await query.message.delete()
    except Exception:
        pass

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    try:
        async with db_pool.acquire() as conn:
            # 🌍 SQL: выбираем по 1 профилю из каждой страны (DISTINCT ON)
            global_profiles = await conn.fetch("""
                SELECT DISTINCT ON (country) 
                    user_id, name, city, country, difficulty, climb_type, 
                    gender, weight, bio, status_slug, 
                    COALESCE(likes_count, 0) AS likes_count, 
                    boost_expires_at, is_founder, has_real_photo
                FROM users 
                WHERE has_real_photo = TRUE 
                  AND is_deleted = FALSE
                  AND user_id != $1
                  AND country IS NOT NULL
                  AND city IS NOT NULL
                ORDER BY country, RANDOM()
                LIMIT 10
            """, user_id)

            # Проверяем минимум 5 стран
            countries = set(row['country'] for row in global_profiles)
            if len(countries) < 5 or len(global_profiles) < 5:
                # Недостаточно разнообразия — fallback на обычный search_empty
                await query.message.reply_photo(
                    photo="https://postimg.cc/R6zWQySf",
                    caption=TEXT2[lang]["search_empty"],
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # ✅ Отмечаем что пользователь использовал глобальный поиск
            await conn.execute(
                "UPDATE users SET global_search_used = TRUE WHERE user_id = $1", user_id
            )

        # 📦 ИНИЦИАЛИЗИРУЕМ глобальный поиск
        context.user_data["global_search_mode"] = True
        context.user_data["global_search_results"] = list(global_profiles)
        context.user_data["global_search_page"] = 0

        # 🚀 Показываем вступительное сообщение + первый профиль
        await query.message.reply_text(TEXT2[lang]["search_global_intro"])
        await show_global_search_result(update, context)

    except Exception as e:
        print(f"❌ Ошибка в handle_global_search: {e}")
        await query.message.reply_text("❌ Ошибка загрузки профилей.")


async def show_global_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает следующую анкету из глобального поиска.
    Формат идентичен обычному поиску (search_find) + город/страна с флагом.
    После последней анкеты показывает финальное сообщение с реферальной ссылкой.
    """
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id

    profiles = context.user_data.get("global_search_results", [])
    page = context.user_data.get("global_search_page", 0)

    # Проверяем, закончились ли профили
    if page >= len(profiles):
        # 🏁 ФИНАЛ: показываем реферальную ссылку
        context.user_data["global_search_mode"] = False

        keyboard = [[InlineKeyboardButton(
            TEXT2[lang]["search_global_finished_btn"],
            callback_data="btn_global_referral"
        )]]

        target = update.callback_query.message if update.callback_query else update.message
        await target.reply_text(
            TEXT2[lang]["search_global_finished"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # 📋 ПОКАЗЫВАЕМ ПРОФИЛЬ (формат как в show_next_search_result)
    row = profiles[page]
    uid = row['user_id']
    name = row['name']
    city = row['city']
    country = row['country']
    diff = row['difficulty']
    ctype = row['climb_type']
    gen = row['gender']
    w = row['weight']
    bio = row['bio']
    status_slug = row['status_slug']
    likes_count = row['likes_count']
    boost_expires_at = row['boost_expires_at']
    is_founder = row['is_founder']
    has_real_photo = row.get('has_real_photo', True)

    # Форматируем лайки
    likes_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
    likes_esc = escape_markdown(likes_raw)

    # 🚀 Имя с бейджами (как в обычном поиске)
    name_with_boost = name
    if is_founder:
        name_with_boost = f"{name} 💎"
    elif boost_expires_at and boost_expires_at > datetime.now():
        name_with_boost = f"{name} 🗯"

    # Поля с экранированием (MARKDOWN_V2)
    name_esc = escape_markdown(name_with_boost)
    diff_esc = escape_markdown(DIFFICULTY_LABELS.get(diff, diff) if diff else TEXT2[lang]["not_specified"])
    ctype_esc = escape_markdown(get_climb_label(ctype, lang) if ctype else TEXT2[lang]["not_specified"])
    gen_esc = escape_markdown(get_gender_label(gen, lang) if gen else TEXT2[lang]["not_specified"])
    weight_esc = display_weight_md(w, lang)

    bio_line = f"\n📝 {escape_markdown(bio)}" if bio else ""

    # Статус
    def render_status_line_local(lang: str, slug: str | None) -> str:
        if not slug:
            return ""
        opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
        raw = opts_map.get(slug, "")
        return f"*{escape_markdown(raw)}*\n" if raw else ""

    status_line = render_status_line_local(lang, status_slug)

    # 🌍 Город и страна с флагом (маппинг по названию страны)
    COUNTRY_TO_CODE = {
        "Russia": "RU", "Germany": "DE", "Spain": "ES", "France": "FR", 
        "Italy": "IT", "USA": "US", "United States": "US", "UK": "GB",
        "United Kingdom": "GB", "Poland": "PL", "Ukraine": "UA", "Turkey": "TR",
        "Austria": "AT", "Switzerland": "CH", "Netherlands": "NL", "Belgium": "BE",
        "Czech Republic": "CZ", "Czechia": "CZ", "Portugal": "PT", "Greece": "GR",
        "Norway": "NO", "Sweden": "SE", "Finland": "FI", "Denmark": "DK",
        "Argentina": "AR", "Brazil": "BR", "Mexico": "MX", "Chile": "CL",
        "Colombia": "CO", "Peru": "PE", "Japan": "JP", "China": "CN",
        "South Korea": "KR", "India": "IN", "Australia": "AU", "New Zealand": "NZ",
        "Canada": "CA", "Thailand": "TH", "Indonesia": "ID", "Malaysia": "MY",
        "Singapore": "SG", "Israel": "IL", "South Africa": "ZA", "Morocco": "MA",
        "Egypt": "EG", "Croatia": "HR", "Slovenia": "SI", "Slovakia": "SK",
        "Hungary": "HU", "Romania": "RO", "Bulgaria": "BG", "Serbia": "RS",
        "Kazakhstan": "KZ", "Georgia": "GE", "Armenia": "AM", "Azerbaijan": "AZ",
        "Belarus": "BY", "Lithuania": "LT", "Latvia": "LV", "Estonia": "EE",
        "Ireland": "IE", "Iceland": "IS", "Luxembourg": "LU", "Malta": "MT",
        "Cyprus": "CY", "Albania": "AL", "North Macedonia": "MK", "Montenegro": "ME",
        "Bosnia and Herzegovina": "BA", "Moldova": "MD", "Vietnam": "VN",
        "Philippines": "PH", "Pakistan": "PK", "Bangladesh": "BD", "Nepal": "NP",
        "Sri Lanka": "LK", "Taiwan": "TW", "Hong Kong": "HK"
    }
    country_code = COUNTRY_TO_CODE.get(country, "")
    flag = get_flag_emoji(country_code) if country_code else "🌍"
    location_line = f"📍 {escape_markdown(city)}, {escape_markdown(country)} {flag}\n"

    # Формируем текст (как search_find + локация)
    text = (
        f"{TEXT2[lang]['profile_user']}: *{name_esc}*\n"
        f"{location_line}"
        f"{TEXT2[lang]['field_type']}: {ctype_esc} I {diff_esc}\n"
        f"{TEXT2[lang]['field_gender']}: {gen_esc}\n"
        f"{TEXT2[lang]['field_weight']}: {weight_esc}\n\n"
        f"{status_line}"
        f"❤️ {likes_esc}{bio_line}"
    )

    # 4 КНОПКИ (как в обычном поиске: лайк, написать, скрыть, жалоба)
    buttons = [
        [
            InlineKeyboardButton("❤️", callback_data=f"like_{uid}"),
            InlineKeyboardButton("✉️", callback_data=f"open_chat_{uid}"),
            InlineKeyboardButton("🙈", callback_data=f"hide_{uid}"),
            InlineKeyboardButton("🚫", callback_data=f"report_{uid}")
        ]
    ]
    markup = InlineKeyboardMarkup(buttons)

    target = update.callback_query.message if update.callback_query else update.message

    # 📸 Загружаем фото из БД (только реальные фото в глобальном поиске)
    photo_source = None
    try:
        async with db_pool.acquire() as conn:
            photo_row = await conn.fetchrow("SELECT photo_bytes FROM users WHERE user_id = $1", uid)
            if photo_row and photo_row['photo_bytes']:
                photo_bytes = bytes(photo_row['photo_bytes'])
                image_io = BytesIO(photo_bytes)
                image_io.name = "photo.jpg"
                image_io.seek(0)
                photo_source = image_io
    except Exception as e:
        print(f"⚠️ Ошибка загрузки фото для {uid}: {e}")

    try:
        if photo_source:
            sent = await target.reply_photo(
                photo=photo_source,
                caption=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup,
                protect_content=True
            )
        else:
            sent = await target.reply_text(
                text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup
            )

        context.user_data["last_card_message_id"] = sent.message_id
        context.user_data["global_search_page"] = page + 1

    except Exception as e:
        print(f"❌ Ошибка отправки глобальной анкеты: {e}")


async def handle_global_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает реферальную ссылку после глобального поиска"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"

    # Используем существующие тексты
    await query.message.reply_markdown(TEXT2[lang]["chalk_invite_intro"])
    await asyncio.sleep(1)

    message_text_2 = TEXT2[lang]["menu_likes_message_to_share"].format(ref_link=ref_link)
    await query.message.reply_html(message_text_2, disable_web_page_preview=True)


async def handle_go_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏠 Возврат в главное меню из рассылки"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    menu_buttons = [
        [KeyboardButton(TEXTS[lang]["menu_likes"]), KeyboardButton(TEXTS[lang]["menu_search"])],
        [KeyboardButton(TEXTS[lang]["menu_chats"]), KeyboardButton(TEXTS[lang]["menu_board"])],
        [KeyboardButton(TEXTS[lang]["menu_form"]), KeyboardButton(TEXTS[lang]["menu_chalk"]), KeyboardButton(TEXTS[lang]["menu_about"])]
    ]

    await query.message.reply_text(
        TEXT2[lang]["menu_main"],
        reply_markup=ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    )


async def show_next_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE, skip_init: bool = False):
    """
    Показывает следующую анкету из результатов поиска.
    skip_init=True когда вызывается из handle_search_command (результаты уже загружены)
    """
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id

    # Если skip_init=False, проверяем нужно ли переинициализировать поиск
    if not skip_init:
        # ✅ БЫСТРАЯ ПРОВЕРКА: если фильтры изменились (флаг устанавливается при сохранении фильтров)
        if context.user_data.get("filters_dirty", False):
            context.user_data["filters_dirty"] = False
            context.user_data["search_results"] = []
            context.user_data["search_buffer"] = []
            context.user_data["search_page"] = 0
            context.user_data["search_seen_ids"] = set()
            await handle_search_command(update, context)
            return

        # ✅ ЕСЛИ РЕЗУЛЬТАТОВ НЕТ - делаем новый поиск
        raw_matches = context.user_data.get("search_results", [])
        if not raw_matches:
            await handle_search_command(update, context)
            return

    page = context.user_data.get("search_page", 0)
    raw_matches = context.user_data.get("search_results", [])
    exhausted = context.user_data.get("search_exhausted", False)
    filters = context.user_data.get("search_filters", {})
    wmin = filters.get("weight_min")
    wmax = filters.get("weight_max")
    difficulty = filters.get("difficulty")

    def is_weight_ok(w):
        try:
            w_int = int(w)
            if wmin is not None and w_int < wmin:
                return False
            if wmax is not None and w_int > wmax:
                return False
        except:
            return False if wmin or wmax else True
        return True

    def apply_difficulty_filter(rows):
        """Применяет фильтр сложности к списку"""
        if not difficulty or difficulty.strip() == "any":
            return rows
        allowed = set(DIFFICULTY_BUCKETS.get(difficulty.strip(), []))
        if not allowed:
            return rows
        return [r for r in rows if r['difficulty'] is not None and r['difficulty'] in allowed]

    # Применяем фильтры к результатам
    matches = apply_difficulty_filter(raw_matches)
    matches = [m for m in matches if is_weight_ok(m['weight'])]

    if page >= len(matches):
        # Проверяем идёт ли ещё загрузка
        if not exhausted:
            # Даём шанс фоновой загрузке добавить анкеты
            await asyncio.sleep(0.5)
            raw_matches = context.user_data.get("search_results", [])
            matches = apply_difficulty_filter(raw_matches)
            matches = [m for m in matches if is_weight_ok(m['weight'])]
            exhausted = context.user_data.get("search_exhausted", False)

        if page >= len(matches):
            await update.effective_message.reply_text(TEXT2[lang]["search_no_more"])
            return

    # 🚀 ОПТИМИЗАЦИЯ: метаданные уже загружены (фото — лениво!)
    row = matches[page]
    uid = row['user_id']
    name = row['name']
    diff = row['difficulty']
    ctype = row['climb_type']
    gen = row['gender']
    w = row['weight']
    bio = row['bio']
    status_slug = row['status_slug']
    likes_count = row['likes_count']
    boost_expires_at = row['boost_expires_at']
    is_founder = row['is_founder']
    has_real_photo = row.get('has_real_photo', None)

    # Форматируем лайки
    likes_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
    likes_esc = escape_markdown(likes_raw)

    # 🚀 ОПТИМИЗАЦИЯ: добавляем эмодзи из уже загруженных полей (БЕЗ доп запроса)
    name_with_boost = name
    if is_founder:
        name_with_boost = f"{name} 💎"
    elif boost_expires_at and boost_expires_at > datetime.now():
        name_with_boost = f"{name} 🗯"

    # Поля с экранированием (MARKDOWN_V2)
    name_esc = escape_markdown(name_with_boost)
    diff_esc = escape_markdown(DIFFICULTY_LABELS.get(diff, diff) if diff else TEXT2[lang]["not_specified"])
    ctype_esc = escape_markdown(get_climb_label(ctype, lang) if ctype else TEXT2[lang]["not_specified"])
    gen_esc = escape_markdown(get_gender_label(gen, lang) if gen else TEXT2[lang]["not_specified"])
    weight_esc = display_weight_md(w, lang)

    bio_line = f"\n📝 {escape_markdown(bio)}" if bio else ""

    def render_status_line_local(lang: str, slug: str | None) -> str:
        if not slug:
            return ""
        opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
        raw = opts_map.get(slug, "")
        return f"*{escape_markdown(raw)}*\n" if raw else ""

    status_line = render_status_line_local(lang, status_slug)

    text = (
        f"{TEXT2[lang]['profile_user']}: *{name_esc}*\n"
        f"{TEXT2[lang]['field_type']}: {ctype_esc} I {diff_esc}\n"
        f"{TEXT2[lang]['field_gender']}: {gen_esc}\n"
        f"{TEXT2[lang]['field_weight']}: {weight_esc}\n\n"
        f"{status_line}"
        f"❤️ {likes_esc}{bio_line}"
    )



    buttons = [
        [
            InlineKeyboardButton("❤️", callback_data=f"like_{uid}"),
            InlineKeyboardButton("✉️", callback_data=f"open_chat_{uid}"),
            InlineKeyboardButton("🙈", callback_data=f"hide_{uid}"),
            InlineKeyboardButton("🚫", callback_data=f"report_{uid}")
        ]
    ]

    markup = InlineKeyboardMarkup(buttons)

    # Где отправить: если это callback, берём message из него
    target = update.callback_query.message if update.callback_query else update.message

    # 📸 ВСЕГДА загружаем актуальное фото из БД (решает проблему устаревшего кэша)
    # Кэш has_real_photo может быть устаревшим, если пользователь загрузил фото после попадания в кэш
    photo_source = None  # URL или BytesIO

    try:
        async with db_pool.acquire() as conn:
            # Загружаем актуальные данные: фото + текущий флаг has_real_photo
            photo_row = await conn.fetchrow(
                "SELECT photo_bytes, has_real_photo FROM users WHERE user_id = $1", uid
            )

            if photo_row and photo_row['photo_bytes']:
                photo_bytes = bytes(photo_row['photo_bytes'])
                actual_has_real_photo = photo_row['has_real_photo']

                # Проверяем не заглушка ли это по размеру
                if len(photo_bytes) in PLACEHOLDER_SIZES:
                    # Это заглушка — используем CDN URL
                    from random import choice
                    photo_source = choice(PLACEHOLDER_URLS.get(gen, PLACEHOLDER_URLS["other"]))

                    # Автокоррекция БД: если флаг неверный, исправляем
                    if actual_has_real_photo is True:
                        await conn.execute(
                            "UPDATE users SET has_real_photo = FALSE WHERE user_id = $1", uid
                        )
                else:
                    # Реальное фото!
                    image_io = BytesIO(photo_bytes)
                    image_io.name = "photo.jpg"
                    image_io.seek(0)
                    photo_source = image_io

                    # Автокоррекция БД: если флаг неверный, исправляем
                    if actual_has_real_photo is not True:
                        await conn.execute(
                            "UPDATE users SET has_real_photo = TRUE WHERE user_id = $1", uid
                        )
            else:
                # Нет фото — заглушка
                from random import choice
                photo_source = choice(PLACEHOLDER_URLS.get(gen, PLACEHOLDER_URLS["other"]))
    except Exception as e:
        print(f"⚠️ Ошибка загрузки фото для {uid}: {e}")
        # Fallback на заглушку
        from random import choice
        photo_source = choice(PLACEHOLDER_URLS.get(gen, PLACEHOLDER_URLS["other"]))

    try:
        if photo_source:
            sent = await target.reply_photo(
                photo=photo_source,
                caption=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup,
                protect_content=True
            )
        else:
            sent = await target.reply_text(
                text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup
            )

        context.user_data["last_card_message_id"] = sent.message_id
        context.user_data["search_page"] = page + 1

    except Exception as e:
        print(f"⚠️ Ошибка при отправке анкеты из поиска: {e}")

async def save_partial_profile(user_id, context: ContextTypes.DEFAULT_TYPE = None):
    """✅ ASYNC VERSION - сохраняет частичный профиль в БД"""
    data = user_sessions.get(user_id, {})
    if not data:
        return

    # Попытка взять selected_country/city из context, если их нет в user_sessions
    if context:
        if "selected_country" not in data and context.user_data.get("selected_country"):
            data["selected_country"] = context.user_data["selected_country"]
        if "selected_city" not in data and context.user_data.get("selected_city"):
            data["selected_city"] = context.user_data["selected_city"]

    async with db_pool.acquire() as conn:
        existing = await conn.fetchrow(
            """
            SELECT username, language, name, difficulty, climb_type,
                   country, country_other, city, city_other, photo_bytes,
                   gender, weight, bio, has_real_photo
            FROM users WHERE user_id = $1
        """, user_id)

    if existing:
        existing = tuple(existing.values())
    else:
        existing = (None,) * 14

    selected_country = data.get("selected_country") or ("🌍 Other" if data.get("country_other") else data.get("country"))
    selected_city = data.get("selected_city") or ("Другой" if data.get("city_other") else data.get("city"))

    country = selected_country if selected_country != "🌍 Other" else "🌍 Other"
    country_other = data.get("country") if selected_country == "🌍 Other" else None

    city = selected_city if selected_city != "Другой" else "Другой"
    city_other = data.get("city") if selected_city == "Другой" else None

    # ✅ Если фото не задано (ни в data, ни в existing), подставляем заглушку
    if "photo_bytes" not in data and not existing[9]:
        gender = data.get("gender", existing[10]) or "other"
        from random import choice
        selected_url = choice(PLACEHOLDER_URLS.get(gender, PLACEHOLDER_URLS["other"]))
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(selected_url)
                if response.status_code == 200:
                    data["photo_bytes"] = response.content
                    data["has_real_photo"] = False  # Это заглушка
                    print(f"📥 Заглушка подставлена для {user_id}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки заглушки для {user_id}: {type(e).__name__}: {e}")
    elif "photo_bytes" in data and "has_real_photo" not in data:
        # ✅ Только если has_real_photo не был установлен явно - значит это реальное фото
        data["has_real_photo"] = True

    # 🛡 Безопасное определение photo_bytes
    photo_bytes = data.get("photo_bytes")
    if photo_bytes is None and "photo_bytes" not in data:
        photo_bytes = existing[9]

    values = [
        data.get("username", existing[0]),
        data.get("lang", existing[1]),
        data.get("name", existing[2]),
        data.get("difficulty", existing[3]),
        data.get("climb_type", existing[4]),
        country or existing[5],
        country_other or existing[6],
        city or existing[7],
        city_other or existing[8],
        photo_bytes,
        data.get("gender", existing[10]),
        data.get("weight", existing[11]),
        data.get("bio", existing[12]),
        data.get("has_real_photo", existing[13]),
    ]

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (
                user_id, username, language, name, difficulty,
                climb_type, country, country_other, city, city_other,
                photo_bytes, gender, weight, bio, has_real_photo
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                language = EXCLUDED.language,
                name = EXCLUDED.name,
                difficulty = EXCLUDED.difficulty,
                climb_type = EXCLUDED.climb_type,
                country = EXCLUDED.country,
                country_other = EXCLUDED.country_other,
                city = EXCLUDED.city,
                city_other = EXCLUDED.city_other,
                photo_bytes = EXCLUDED.photo_bytes,
                gender = EXCLUDED.gender,
                weight = EXCLUDED.weight,
                bio = EXCLUDED.bio,
                has_real_photo = EXCLUDED.has_real_photo,
                is_deleted = FALSE
        """, user_id, *values)



def reset_user_flags(context, user_id):
    flags = [
        "awaiting_bio", "awaiting_name", "awaiting_custom_city",
        "awaiting_custom_country"
    ]
    for flag in flags:
        context.user_data[flag] = False


async def confirm_delete_profile(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_yes"],
                             callback_data="confirm_delete_profile")
    ],
                [
                    InlineKeyboardButton(INLINE_TEXTS[lang]["btn_no"],
                                         callback_data="cancel_delete_profile")
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(TEXT2[lang]["confirm_delete_profile"],
                                    reply_markup=reply_markup)


async def route_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Игнорировать нажатия на кнопку прогресса регистрации (неинтерактивная кнопка)
    text = update.message.text if update.message and update.message.text else ""
    if text.startswith("📋") and "Шаг" in text and "из 8" in text:
        return
    if text.startswith("📋") and "Step" in text and "of 8" in text:
        return
    if text.startswith("📋") and "Paso" in text and "de 8" in text:
        return
    if text.startswith("📋") and "Schritt" in text and "von 8" in text:
        return

    # Групповой чат встреч (должен быть ПЕРЕД chat_with)
    if context.user_data.get("current_group_chat_session"):
        handled = await handle_group_chat_message(update, context)
        if handled:
            return

    if context.user_data.get("chat_with"):
        return await handle_proxy_message(update, context)

    if update.message and update.message.text:
        text = update.message.text.strip()

        user_id = update.message.from_user.id
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)

        lang = row['language'] if row and row['language'] else "ru"

        end_chat_label = TEXTS[lang]["btn_end_chat"]
        if text == end_chat_label:
            return await handle_proxy_message(update, context)

    if context.user_data.get("broadcast_stage") == "broadcast_all":
        await admin_handle_broadcast_all(update, context)
        return

    if context.user_data.get("broadcast_stage") == "awaiting_media":
        await handle_admin_broadcast_message(update, context)
        return

    if context.user_data.get("awaiting_bio_again"):
        if not update.message or not update.message.text:
            return  # Игнорируем сообщения без текста
        text = update.message.text.strip()
        error = validate_text(text, lang=lang, max_length=130)
        if error:
            await update.message.reply_text(error)
            return

        context.user_data["awaiting_bio_again"] = False
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE users SET bio = $1 WHERE user_id = $2", text, user_id)

        keyboard = [
            [KeyboardButton(TEXTS[lang]["form_edit"])],
            [KeyboardButton(TEXTS[lang]["form_delete"])],
            [KeyboardButton(TEXTS[lang]["form_back"])]
        ]

        # ✅ Отправляем отбивку И профиль с кнопками
        await update.message.reply_text(TEXT2[lang].get("saved"), reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        await send_profile_menu(update.message, user_id, context)
        return

    if context.user_data.get("awaiting_custom_board_date"):
        if not update.message or not update.message.text:
            return  # Игнорируем сообщения без текста
        lang = context.user_data.get("lang", "ru")
        text = update.message.text.strip()
        user_id = update.effective_user.id
        try:
            date_obj = datetime.strptime(text, "%d.%m.%Y")
            selected_date = date_obj.date()

            # Проверяем, не участвует ли уже пользователь в тренировке на эту дату
            async with db_pool.acquire() as conn:
                # Проверяем и кастомные (board_sessions), и дефолтные (gym_sessions) тренировки
                existing_board = await conn.fetchrow("""
                    SELECT bs.id FROM board_session_participants bsp
                    JOIN board_sessions bs ON bsp.session_id = bs.id
                    WHERE bsp.user_id = $1 AND bs.session_date = $2
                """, user_id, selected_date)

                existing_gym = await conn.fetchrow("""
                    SELECT gs.id FROM gym_session_participants gsp
                    JOIN gym_sessions gs ON gsp.session_id = gs.id
                    WHERE gsp.user_id = $1 AND gs.session_date = $2
                """, user_id, selected_date)

                if existing_board or existing_gym:
                    await update.message.reply_text(TEXT2[lang]["meetups_already_joined"])
                    # Возвращаем пользователя к выбору даты через инлайн кнопки
                    context.user_data["awaiting_custom_board_date"] = False
                    context.user_data["awaiting_board_date"] = True

                    today = datetime.now()
                    tomorrow = today + timedelta(days=1)
                    buttons = [[
                        InlineKeyboardButton(TEXT2[lang]["board_date_today"].format(
                            date=today.strftime("%d.%m (%a)")), callback_data="board_date_today")
                    ], [
                        InlineKeyboardButton(TEXT2[lang]["board_date_tomorrow"].format(
                            date=tomorrow.strftime("%d.%m (%a)")), callback_data="board_date_tomorrow")
                    ], [
                        InlineKeyboardButton(TEXT2[lang]["board_date_custom"],
                                             callback_data="board_date_custom")
                    ]]

                    await update.message.reply_text(
                        TEXT2[lang].get("board_date_choose_another", "📅 Выберите другую дату:"),
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                    return

            context.user_data["board"]["date"] = date_obj.strftime("%Y-%m-%d")
            context.user_data["awaiting_custom_board_date"] = False
            context.user_data["awaiting_board_time"] = True
            context.user_data["time_page"] = 0

            keyboard = [
                [KeyboardButton(TEXTS[lang]["board_city"])],
                [KeyboardButton(TEXTS[lang]["board_create"]),
                 KeyboardButton(TEXTS[lang]["board_my"])],
                [KeyboardButton(TEXTS[lang]["board_back"])]
            ]

            await update.message.reply_text(TEXTS[lang]["board_date_saved"],
                                            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            await show_time_page(update, context)
        except ValueError:
            await update.message.reply_text(TEXTS[lang]["board_custom_date_invalid"])
        return

    if context.user_data.get("awaiting_edit_photo"):
        context.user_data["awaiting_edit_photo"] = False

        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()

            is_safe = check_image_for_harm_base64(photo_bytes)
            if not is_safe:
                await update.message.reply_text(TEXT2[lang]["err_photo_prohibited"])
                return

            async with db_pool.acquire() as conn:
                await conn.execute("UPDATE users SET photo_bytes = $1, has_real_photo = TRUE WHERE user_id = $2", photo_bytes, user_id)
        else:
            gender = get_gender_label(user_id, lang).lower()
            from random import choice
            selected_url = choice(PLACEHOLDER_URLS.get(gender, PLACEHOLDER_URLS["other"]))
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(selected_url)
                if response.status_code == 200:
                    async with db_pool.acquire() as conn:
                        await conn.execute("UPDATE users SET photo_bytes = $1, has_real_photo = FALSE WHERE user_id = $2", response.content, user_id)
                else:
                    await update.message.reply_text(TEXT2[lang]["err_photo_required"])
                    return
            except Exception as e:
                print(f"⚠️ Ошибка при загрузке заглушки фото: {e}")
                await update.message.reply_text(TEXT2[lang]["err_photo_required"])
                return

        # ✅ Отправляем отбивку И профиль с кнопками
        await update.message.reply_text(TEXT2[lang].get("saved"))
        await send_profile_menu(update.message, user_id, context)
        return

    if context.user_data.get("awaiting_bio"):
        if not update.message or not update.message.text:
            return  # Игнорируем сообщения без текста (стикеры, фото и т.д.)
        bio_text = update.message.text.strip()
        error = validate_text(bio_text, lang=lang, max_length=130)
        if error:
            keyboard = [[InlineKeyboardButton(TEXT2[lang]["btn_skip"], callback_data="skip_bio")]]
            await update.message.reply_text(error)
            await update.message.reply_text(TEXT2[lang]["ask_bio"], reply_markup=InlineKeyboardMarkup(keyboard))
            return

        context.user_data["awaiting_bio"] = False
        user_sessions[user_id] = user_sessions.get(user_id, {})
        user_sessions[user_id]["bio"] = bio_text
        await save_partial_profile(user_id)

        keyboard = [[InlineKeyboardButton(INLINE_TEXTS[lang]["btn_finish_registration"], callback_data="finish_registration")]]
        await update.message.reply_text(TEXT2[lang]["bio_saved"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if context.user_data.get("chat_with"):
        await handle_proxy_message(update, context)
        return

    # ГЛАВНАЯ ПРОВЕРКА: Админское удаление по ID — ДО admin_action!
    if context.user_data.get("awaiting_admin_delete_id"):
        context.user_data["awaiting_admin_delete_id"] = False
        try:
            target_id = int(update.message.text.strip())
            async with db_pool.acquire() as conn:
                # 1. Лайки + лог пушей по лайкам
                await conn.execute(
                    "DELETE FROM like_push_log WHERE from_user_id = $1 OR to_user_id = $1",
                    target_id
                )
                await conn.execute("DELETE FROM likes WHERE from_user_id = $1", target_id)
                await conn.execute("DELETE FROM likes WHERE to_user_id = $1", target_id)

                # 2. Чаты, архив, сообщения, мьюты
                await conn.execute(
                    "DELETE FROM chat_requests_log WHERE from_user_id = $1 OR to_user_id = $1",
                    target_id
                )
                await conn.execute(
                    "DELETE FROM proxy_chats WHERE user1_id = $1 OR user2_id = $1",
                    target_id
                )
                await conn.execute(
                    "DELETE FROM user_chats WHERE user_id = $1 OR partner_id = $1",
                    target_id
                )
                await conn.execute(
                    "DELETE FROM chat_archive WHERE user_id = $1 OR partner_id = $1",
                    target_id
                )
                await conn.execute("DELETE FROM chat_messages WHERE sender_id = $1", target_id)
                await conn.execute(
                    "DELETE FROM chat_messages WHERE chat_id LIKE $1",
                    f"{target_id}_%"
                )
                await conn.execute(
                    "DELETE FROM chat_messages WHERE chat_id LIKE $1",
                    f"%_{target_id}"
                )
                await conn.execute(
                    "DELETE FROM muted_users WHERE user_id = $1 OR muted_user_id = $1",
                    target_id
                )

                # 3. Скрытые пользователи (личные), но сохраняем глобальные блокировки (user_id = 0)
                await conn.execute(
                    """
                    DELETE FROM hidden_users
                    WHERE user_id = $1
                       OR (hidden_user_id = $1 AND user_id <> 0)
                    """,
                    target_id
                )

                # 4. Поисковые фильтры
                await conn.execute("DELETE FROM search_filters WHERE user_id = $1", target_id)

                # 5. Логи и вспомогательные таблицы
                await conn.execute("DELETE FROM user_logins WHERE user_id = $1", target_id)
                await conn.execute("DELETE FROM registration_times WHERE user_id = $1", target_id)
                await conn.execute("DELETE FROM feedback_log WHERE user_id = $1", target_id)
                await conn.execute("DELETE FROM board_magnesium_log WHERE user_id = $1", target_id)

                # 6. Объявления пользователя
                await conn.execute("DELETE FROM board_posts WHERE user_id = $1", target_id)

                # 7. МЯГКОЕ УДАЛЕНИЕ профиля (soft delete) — очищаем данные, сохраняем платежи
                await conn.execute("""
                    UPDATE users SET
                        is_deleted = TRUE,
                        name = '[Deleted]',
                        gender = NULL,
                        difficulty = NULL,
                        climb_type = NULL,
                        weight = NULL,
                        city = NULL,
                        city_other = NULL,
                        country = NULL,
                        country_other = NULL,
                        photo_bytes = NULL,
                        has_real_photo = FALSE,
                        bio = NULL
                    WHERE user_id = $1
                """, target_id)

                # ✅ СОХРАНЯЕМ платежные данные:
                # - is_founder (статус Founder 💎)
                # - boost_expires_at (дата окончания Boost)
                # - magnesium_balance (магнезия)
                # - magnesium_log (история магнезии)
                # - referrals (реферальная система)

            await update.message.reply_text(f"🗑️ Профиль ID {target_id} удалён (мягкое удаление, платежи сохранены).")
        except ValueError:
            await update.message.reply_text(f"❌ Введи корректный числовой ID.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при удалении: {e}")
            print(f"❌ Ошибка при админском удалении профиля {target_id}: {e}")
        return

    if context.user_data.get("admin_action"):
        await admin_handle_text(update, context)
        return

    if context.user_data.get("admin_target_id"):
        await admin_handle_message_text(update, context)
        return

    if get_state(context):
        await handle_text_message(update, context)
        return

    if context.user_data.get("awaiting_feedback"):
        context.user_data["awaiting_feedback"] = False

        async with db_pool.acquire() as conn:
            feedback_count = await conn.fetchval("""
                SELECT COUNT(*) FROM feedback_log
                WHERE user_id = $1 AND DATE(timestamp) = CURRENT_DATE
            """, user_id)

            if feedback_count >= 5:
                await update.message.reply_text(TEXT2[lang]["feedback_limit_exceeded"])
                return

            await conn.execute("INSERT INTO feedback_log (user_id) VALUES ($1)", user_id)

        feedback_message = f"📝 Отзыв от @{update.message.from_user.username or 'без ника'} (ID: {user_id}):\n\n{update.message.text}"
        await context.bot.send_message(chat_id=FEEDBACK_CHANNEL_ID, text=feedback_message)

        keyboard = [[KeyboardButton(TEXTS[lang]["about_feedback"])],
                    [KeyboardButton(TEXTS[lang]["about_rules"])],
                    [KeyboardButton(TEXTS[lang]["about_back"])]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(TEXT2[lang]["feedback_thanks"], reply_markup=reply_markup)
        return

    if context.user_data.get("awaiting_board_gym_custom"):
        lang = context.user_data.get("lang", "ru")
        context.user_data["awaiting_board_gym_custom"] = False
        context.user_data["board"]["gym"] = update.message.text.strip()

        keyboard = [
            [KeyboardButton(TEXTS[lang]["board_city"])],
            [KeyboardButton(TEXTS[lang]["board_create"]),
             KeyboardButton(TEXTS[lang]["board_my"])],
            [KeyboardButton(TEXTS[lang]["board_back"])]
        ]
        await update.message.reply_text(TEXTS[lang]["board_gym_saved"],
                                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        await show_board_preview(update, context)
        return

    # Обратная совместимость со старым способом ввода зала
    if context.user_data.get("awaiting_board_gym"):
        lang = context.user_data.get("lang", "ru")
        context.user_data["awaiting_board_gym"] = False
        context.user_data["board"]["gym"] = update.message.text.strip()

        keyboard = [
            [KeyboardButton(TEXTS[lang]["board_city"])],
            [KeyboardButton(TEXTS[lang]["board_create"]),
             KeyboardButton(TEXTS[lang]["board_my"])],
            [KeyboardButton(TEXTS[lang]["board_back"])]
        ]
        await update.message.reply_text(TEXTS[lang]["board_gym_saved"],
                                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        await show_board_preview(update, context)
        return

    await handle_buttons(update, context)


async def confirm_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    partner_id = context.user_data.get("chat_with")

    # Архивируем для обоих пользователей
    if partner_id:
        async with db_pool.acquire() as conn:
            for uid, pid in [(user_id, partner_id), (partner_id, user_id)]:
                await conn.execute("""
                    UPDATE user_chats SET is_archived = TRUE
                    WHERE user_id = $1 AND partner_id = $2
                """, uid, pid)

            context.user_data["chat_with"] = None

            # Получаем язык второго пользователя
            row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", partner_id)
            partner_lang = row['language'] if row and row['language'] else "ru"

        # Меню для второго пользователя
        partner_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(TEXTS[partner_lang]["chats_active"]),
             KeyboardButton(TEXTS[partner_lang]["offline_muted"])],
            [KeyboardButton(TEXTS[partner_lang]["chats_back"])]
        ], resize_keyboard=True)

        # Отправляем второму уведомление
        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text=TEXT2[partner_lang]["chat_ended_notice"],
                reply_markup=partner_keyboard
            )
        except Exception as e:
            print(f"⚠️ Ошибка отправки partner_id={partner_id}: {e}")

    # Меню для текущего пользователя
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(TEXTS[lang]["chats_active"]),
         KeyboardButton(TEXTS[lang]["offline_muted"])],
        [KeyboardButton(TEXTS[lang]["chats_back"])]
    ], resize_keyboard=True)

    reset_user_flags(context, user_id)

    await query.message.reply_text(TEXT2[lang]["chat_ended_self"],
                                   reply_markup=keyboard)


async def handle_back_to_main(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    user_sessions[user_id] = user_sessions.get(user_id, {})
    user_sessions[user_id]["lang"] = lang

    menu = [
        TEXTS[lang]["menu_likes"], TEXTS[lang]["menu_search"],
        TEXTS[lang]["menu_chats"], TEXTS[lang]["menu_board"],
        TEXTS[lang]["menu_form"], TEXTS[lang]["menu_chalk"], TEXTS[lang]["menu_about"]
    ]

    markup = ReplyKeyboardMarkup(
        [[KeyboardButton(menu[0]),
          KeyboardButton(menu[1])],
         [KeyboardButton(menu[2]),
          KeyboardButton(menu[3])],
         [KeyboardButton(menu[4]),
          KeyboardButton(menu[5])]],
        resize_keyboard=True,
        one_time_keyboard=False)

    await update.message.reply_text(TEXT2[lang]["back_to_main"],
                                    reply_markup=markup)



async def debug_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📡 Chat ID:", update.effective_chat.id)


async def handle_view_profile_from_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_user_id = int(query.data.replace("profile_", ""))
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    key = f"profile_msg_{target_user_id}"
    old_msg_id = context.user_data.get(key)

    # Если анкета уже показывалась — удаляем сообщение-переключатель
    if old_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=old_msg_id)
        except Exception as e:
            print("⚠️ Не удалось удалить сообщение анкеты:", e)
        context.user_data.pop(key, None)
        return

    # Загружаем профиль
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", target_user_id)
        if not row:
            await query.message.reply_text(TEXT2[lang]["profile_not_found"])
            return

        data = dict(row)

        # Лейблы (с экранированием)
        difficulty_display = display_difficulty_md(data.get("difficulty"), lang)
        climb_type_display = escape_markdown(get_climb_label(data.get("climb_type"), lang) if data.get("climb_type") else TEXT2[lang]["not_specified"])
        gender_display = escape_markdown(get_gender_label(data.get("gender"), lang) if data.get("gender") else TEXT2[lang]["not_specified"])
        weight_display = display_weight_md(data.get("weight"), lang)

        country_display = escape_markdown(data.get("country") or TEXT2[lang]["not_specified"])
        city_val = data.get("city_other") if data.get("city") == "Другой" else (data.get("city") or TEXT2[lang]["not_specified"])
        city_display = escape_markdown(city_val)

        likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", target_user_id)
        likes_count = likes_count or 0  # Fallback на 0 если NULL
        likes_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
        likes_display = escape_markdown(likes_raw)

    # статус берём из загруженной строки users (SELECT * ...), если колонки нет — будет None
    status_slug = data.get("status_slug")

    # локальный рендер строки статуса (жирным, безопасно для MarkdownV2)
    def render_status_line_local(lang: str, slug: str | None) -> str:
        if not slug:
            return ""
        opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
        raw = opts_map.get(slug, "")
        return f"*{escape_markdown(raw)}*" if raw else ""

    name_raw = data.get('name', '—')
    name_with_boost = await add_boost_emoji_to_name(name_raw, target_user_id)

    caption_lines = [
        f"{TEXT2[lang]['profile_user']}: *{escape_markdown(name_with_boost)}*",
        f"{TEXT2[lang]['field_type']}: {climb_type_display} I {difficulty_display}",
        f"{TEXT2[lang]['field_country']}: {country_display}",
        f"{TEXT2[lang]['field_city']}: {city_display or TEXT2[lang]['not_specified']}",
        f"{TEXT2[lang]['field_gender']}: {gender_display}",
        f"{TEXT2[lang]['field_weight']}: {weight_display}\n",
        render_status_line_local(lang, status_slug),  # ← ✅ новая строка статуса под блоком с полями
        f"❤️ {likes_display}",
    ]
    if data.get("bio"):
        caption_lines.append(f"📝 {escape_markdown(data['bio'])}")

    caption = "\n".join([line for line in caption_lines if line])  # убираем пустую строку, если статуса нет


    buttons = [[
        InlineKeyboardButton("❤️", callback_data=f"like_{target_user_id}"),
        InlineKeyboardButton("🚫", callback_data=f"report_{target_user_id}")
    ]]

    photo_bytes = data.get("photo_bytes")
    try:
        if photo_bytes:
            image_io = BytesIO(photo_bytes)
            image_io.name = "photo.jpg"
            image_io.seek(0)
            sent = await query.message.reply_photo(
                photo=image_io,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(buttons),
                protect_content=True
            )
        else:
            sent = await query.message.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        context.user_data[key] = sent.message_id
    except Exception as e:
        print("⚠️ Ошибка при отправке анкеты (из чата):", e)
        await query.message.reply_text(caption, parse_mode=ParseMode.MARKDOWN_V2)


async def handle_archive_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    to_user = int(query.data.replace("archive_chat_", ""))

    # 🔹 Добавляем в архив ТОЛЬКО для user_id
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO chat_archive (user_id, partner_id, archived_at)
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, partner_id) DO UPDATE SET
                archived_at = EXCLUDED.archived_at
        """, user_id, to_user)

    # 🔹 НЕ удаляем из proxy_chats!
    # Только из памяти — локально
    active_chats.pop(user_id, None)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(TEXT2[lang]["chat_archived"])

async def handle_chat_archive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        archived = await conn.fetch("""
            SELECT partner_id FROM user_chats
            WHERE user_id = $1 AND is_archived = TRUE
            ORDER BY last_message_time DESC
        """, user_id)

        if not archived:
            await update.message.reply_text(TEXT2[lang]["chat_archive_empty"])
            return

        buttons = []
        for row in archived:
            partner_id = row['partner_id']
            partner_row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", partner_id)
            name = partner_row['name'] if partner_row and partner_row['name'] else TEXT2[lang]["default_user"]
            buttons.append([InlineKeyboardButton(f"✉️ {name}", callback_data=f"restore_chat_{partner_id}")])

    await update.message.reply_text(
        TEXT2[lang]["chat_archive_title"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_restore_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    partner_id = int(query.data.replace("restore_chat_", ""))

    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE user_chats SET is_archived = FALSE
            WHERE user_id = $1 AND partner_id = $2
        """, user_id, partner_id)

        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

    await query.message.reply_text(TEXT2[lang]["chat_restored"])


async def handle_hide_prompt(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    target_id = int(query.data.replace("hide_", ""))

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO hidden_users (user_id, hidden_user_id, hide_until)
            VALUES ($1, $2, NULL)
            ON CONFLICT (user_id, hidden_user_id) DO UPDATE SET
                hide_until = EXCLUDED.hide_until
        """, user_id, target_id)

    try:
        await query.message.delete()
    except:
        await query.message.edit_reply_markup(reply_markup=None)

    await context.bot.send_message(chat_id=query.message.chat_id,
                                   text=TEXT2[lang]["user_hidden"])


async def handle_hide_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    match = re.match(r"hide_(\d+)_(\d+)d", query.data)
    if not match:
        await query.message.reply_text(TEXT2[lang]["invalid_hide_format"])
        return

    hidden_user_id = int(match.group(1))
    days = int(match.group(2))
    user_id = query.from_user.id
    hide_until = datetime.now() + timedelta(days=days)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO hidden_users (user_id, hidden_user_id, hide_until)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, hidden_user_id) DO UPDATE SET
                hide_until = EXCLUDED.hide_until
        """, user_id, hidden_user_id, hide_until.isoformat())

    try:
        if "last_card_message_id" in context.user_data:
            await context.bot.delete_message(
                chat_id=query.message.chat_id,
                message_id=context.user_data["last_card_message_id"])
        if "hide_prompt_message_id" in context.user_data:
            await context.bot.delete_message(
                chat_id=query.message.chat_id,
                message_id=context.user_data["hide_prompt_message_id"])
    except Exception as e:
        print("❌ Не удалось удалить одно из сообщений:", e)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=TEXT2[lang]["user_hidden_days"].format(days=days))

async def handle_go_to_search_menu(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    keyboard = [
        [KeyboardButton(TEXTS[lang]["search_next_person"])],
        [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
        [KeyboardButton(TEXTS[lang]["search_back"])]
    ]


    await query.message.reply_text("🔍",
                                   reply_markup=ReplyKeyboardMarkup(
                                       keyboard, resize_keyboard=True))

    # 👉 Создаём фейковое сообщение и update
    class FakeMessage:

        def __init__(self, from_user, chat_id):
            self.from_user = from_user
            self.chat_id = chat_id

        async def reply_text(self, text, **kwargs):
            kwargs.pop("chat_id", None)
            return await context.bot.send_message(chat_id=self.chat_id,
                                                  text=text,
                                                  **kwargs)

        async def reply_photo(self, photo, **kwargs):
            return await context.bot.send_photo(chat_id=self.chat_id,
                                                photo=photo,
                                                **kwargs)

    class FakeUser:

        def __init__(self, user_id):
            self.id = user_id

    fake_message = FakeMessage(from_user=FakeUser(query.from_user.id),
                               chat_id=query.message.chat.id)
    fake_update = Update(update.update_id, message=fake_message)

    # 🚀 Показываем анкеты
    await handle_search_command(fake_update, context)


async def handle_hidden_users(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Показывает список скрытых пользователей с пагинацией"""
    await show_hidden_users_page(update, context, page=0, is_first=True)


async def handle_unhide_user(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """Восстанавливает скрытого пользователя из списка"""
    query = update.callback_query
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    target_id = int(query.data.replace("unhide_", ""))

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM hidden_users
            WHERE user_id = $1 AND hidden_user_id = $2
            """, user_id, target_id)

    # Отправляем отбивку с сообщением об успехе
    await query.answer(TEXT2[lang]["unhide_success"])

    # Обновляем меню - пересчитываем список скрытых с пагинацией
    # Сохраняем текущую страницу из context если была
    page = context.user_data.get("hidden_users_page", 0)
    await show_hidden_users_page(update, context, page=page, is_first=False)


async def handle_like_callback(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    from_user_id = update.effective_user.id
    await ensure_lang(context, from_user_id)
    lang = context.user_data["lang"]
    to_user_id = int(query.data.replace("like_", ""))

    if from_user_id == to_user_id:
        await context.bot.send_message(chat_id=from_user_id,
                                       text=TEXT2[lang]["like_self_error"])
        return

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT hide_until FROM hidden_users
            WHERE user_id = 0 AND hidden_user_id = $1 AND (hide_until IS NULL OR hide_until > CURRENT_TIMESTAMP)
            """, from_user_id)

        if row:
            await context.bot.send_message(chat_id=from_user_id,
                                           text=TEXT2[lang]["like_blocked_error"])
            return

        # Проверяем: есть ли уже лайк
        already_liked = await conn.fetchrow(
            "SELECT 1 FROM likes WHERE from_user_id = $1 AND to_user_id = $2",
            from_user_id, to_user_id)

        if already_liked:
            # РАЗЛАЙК: убираем лайк из БД
            await conn.execute(
                "DELETE FROM likes WHERE from_user_id = $1 AND to_user_id = $2",
                from_user_id, to_user_id)

            # ОТМЕНЯЕМ отложенный пуш, если он есть
            push_key = (from_user_id, to_user_id)
            if push_key in pending_like_pushes:
                task_info = pending_like_pushes[push_key]
                task = task_info.get('task') if isinstance(task_info, dict) else task_info
                if task and not task.done():
                    task.cancel()
                del pending_like_pushes[push_key]

            await context.bot.send_message(chat_id=from_user_id,
                                           text=TEXT2[lang]["like_removed"])
        else:
            # ЛАЙК: добавляем в БД
            await conn.execute(
                "INSERT INTO likes (from_user_id, to_user_id) VALUES ($1, $2)",
                from_user_id, to_user_id)

            # ЗАПУСКАЕМ отложенный пуш через 1 минуту
            push_key = (from_user_id, to_user_id)
            # Отменяем предыдущую задачу, если она есть (на всякий случай)
            if push_key in pending_like_pushes:
                task_info = pending_like_pushes[push_key]
                task = task_info.get('task') if isinstance(task_info, dict) else task_info
                if task and not task.done():
                    task.cancel()

            # Создаём новую задачу
            task = asyncio.create_task(send_delayed_like_push(from_user_id, to_user_id))
            pending_like_pushes[push_key] = {
                'task': task,
                'created_at': datetime.now()
            }

            await context.bot.send_message(chat_id=from_user_id,
                                           text=TEXT2[lang]["like_sent"])


async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    reported_id = int(query.data.replace("report_", ""))
    context.user_data["reported_id"] = reported_id

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    reasons = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_abuse"],
                             callback_data="reason_abuse")
    ],
               [
                   InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_photo"],
                                        callback_data="reason_photo")
               ],
               [
                   InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_spam"],
                                        callback_data="reason_spam")
               ],
               [
                   InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_ads"],
                                        callback_data="reason_ads")
               ],
               [
                   InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_ok"],
                                        callback_data="reason_ok")
               ]]

    await query.message.reply_text(TEXT2[lang]["report_select_reason"],
                                   reply_markup=InlineKeyboardMarkup(reasons))


async def handle_report_reason(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    reporter_id = query.from_user.id
    reported_id = context.user_data.get("reported_id")
    reason_code = query.data.replace("reason_", "")

    if not reported_id:
        await query.message.reply_text(TEXT2[lang]["report_missing_id"])
        return

    reason_map = {
        "abuse": TEXT2[lang]["report_reason_abuse"],
        "photo": TEXT2[lang]["report_reason_photo"],
        "spam": TEXT2[lang]["report_reason_spam"],
        "ads": TEXT2[lang]["report_reason_ads"]
    }
    reason_text = reason_map.get(reason_code,
                                 TEXT2[lang]["report_reason_unspecified"])

    if reason_code == "ok":
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except:
            pass
        await query.message.reply_text(TEXT2[lang]["report_cancelled"])
        return

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT 1 FROM user_reports WHERE reporter_id = $1 AND reported_id = $2",
            reporter_id, reported_id)
    if row:
        await query.message.reply_text(TEXT2[lang]["report_already_sent"])
        return

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_reports (reporter_id, reported_id, reason)
            VALUES ($1, $2, $3)
            """, reporter_id, reported_id, reason_text)

    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(TEXT2[lang]["report_sent"])

    # Автосанкции
    sanction = await check_user_reports_and_apply_sanctions(reported_id)
    if sanction == "isolation":
        await context.bot.send_message(
            chat_id=reported_id, text=TEXT2[lang]["report_sanction_isolation"])
    elif sanction == "ban":
        await context.bot.send_message(chat_id=reported_id,
                                       text=TEXT2[lang]["report_sanction_ban"])
    elif sanction == "hard_ban":
        await context.bot.send_message(
            chat_id=reported_id, text=TEXT2[lang]["report_sanction_hard"])


async def handle_unhide_all(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Получаем всех, кого пользователь скрывал
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT hidden_user_id FROM hidden_users WHERE user_id = $1",
            user_id)
    hidden_ids = [row['hidden_user_id'] for row in rows]

    # Удаляем скрытие и жалобы параллельно
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM hidden_users WHERE user_id = $1", user_id)

        # Удаляем жалобы на тех же пользователей
        for reported_id in hidden_ids:
            await conn.execute(
                "DELETE FROM user_reports WHERE reporter_id = $1 AND reported_id = $2",
                user_id, reported_id)

    await update.message.reply_text(
        "🔓 Все пользователи восстановлены, жалобы обнулены.")


async def handle_write_prompt(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    to_user_id = int(query.data.replace("write_", ""))
    context.user_data["pending_write"] = to_user_id
    context.user_data["write_prompt_message_id"] = query.message.message_id

    confirm_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_yes"],
                             callback_data="confirm_write"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_no"],
                             callback_data="cancel_write")
    ]])

    sent = await query.message.reply_text(TEXT2[lang]["write_prompt"],
                                          reply_markup=confirm_keyboard)

    context.user_data["confirm_message_id"] = sent.message_id


async def handle_write_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    from_user_id = query.from_user.id
    to_user_id = context.user_data.get("pending_write")

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", from_user_id)
        lang = row['language'] if row and row['language'] else "ru"

    try:
        msg_id = context.user_data.get("confirm_message_id")
        if msg_id:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
    except:
        pass

    context.user_data.pop("pending_write", None)
    context.user_data.pop("confirm_message_id", None)

    # 1. Начинаем чат
    await start_chat(from_user_id, to_user_id, context)

    # 2. Сохраняем контекст
    context.user_data["chat_with"] = to_user_id
    context.user_data["offset"] = 0

    # 3. Показываем интерфейс чата сразу (как open_chat)
    await show_chat_history(query.message.chat_id, from_user_id, to_user_id, context, first_time=True)


async def handle_write_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

    try:
        msg_id = context.user_data.get("confirm_message_id")
        if msg_id:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
    except:
        pass

    context.user_data.pop("pending_write", None)
    context.user_data.pop("confirm_message_id", None)

    await query.message.reply_text(TEXT2[lang]["write_cancelled"])


async def handle_delete_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if query.data == "confirm_delete_profile":
        async with db_pool.acquire() as conn:
            # 1. Лайки + лог пушей по лайкам
            await conn.execute(
                "DELETE FROM like_push_log WHERE from_user_id = $1 OR to_user_id = $1",
                user_id
            )
            await conn.execute("DELETE FROM likes WHERE from_user_id = $1", user_id)
            await conn.execute("DELETE FROM likes WHERE to_user_id = $1", user_id)

            # 2. Чаты, архив, сообщения, мьюты
            await conn.execute(
                "DELETE FROM chat_requests_log WHERE from_user_id = $1 OR to_user_id = $1",
                user_id
            )
            await conn.execute(
                "DELETE FROM proxy_chats WHERE user1_id = $1 OR user2_id = $1",
                user_id
            )
            await conn.execute(
                "DELETE FROM user_chats WHERE user_id = $1 OR partner_id = $1",
                user_id
            )
            await conn.execute(
                "DELETE FROM chat_archive WHERE user_id = $1 OR partner_id = $1",
                user_id
            )
            await conn.execute("DELETE FROM chat_messages WHERE sender_id = $1", user_id)
            await conn.execute(
                "DELETE FROM chat_messages WHERE chat_id LIKE $1",
                f"{user_id}_%"
            )
            await conn.execute(
                "DELETE FROM chat_messages WHERE chat_id LIKE $1",
                f"%_{user_id}"
            )
            await conn.execute(
                "DELETE FROM muted_users WHERE user_id = $1 OR muted_user_id = $1",
                user_id
            )

            # 3. Скрытые пользователи (личные), но сохраняем глобальные блокировки (user_id = 0)
            await conn.execute(
                """
                DELETE FROM hidden_users
                WHERE user_id = $1
                   OR (hidden_user_id = $1 AND user_id <> 0)
                """,
                user_id
            )

            # 4. Поисковые фильтры
            await conn.execute("DELETE FROM search_filters WHERE user_id = $1", user_id)

            # 5. Логи и вспомогательные таблицы (без магнезии)
            await conn.execute("DELETE FROM user_logins WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM registration_times WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM feedback_log WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM board_magnesium_log WHERE user_id = $1", user_id)

            # 6. Объявления пользователя
            await conn.execute("DELETE FROM board_posts WHERE user_id = $1", user_id)

            # 7. МЯГКОЕ УДАЛЕНИЕ профиля (soft delete) — очищаем данные, сохраняем платежи
            await conn.execute("""
                UPDATE users SET
                    is_deleted = TRUE,
                    name = '[Deleted]',
                    gender = NULL,
                    difficulty = NULL,
                    climb_type = NULL,
                    weight = NULL,
                    city = NULL,
                    city_other = NULL,
                    country = NULL,
                    country_other = NULL,
                    photo_bytes = NULL,
                    has_real_photo = FALSE,
                    bio = NULL,
                    status_slug = NULL
                WHERE user_id = $1
            """, user_id)

            # ✅ СОХРАНЯЕМ платежные данные:
            # - is_founder (статус Founder 💎)
            # - boost_expires_at (дата окончания Boost)
            # - magnesium_balance (магнезия)
            # - magnesium_log (история магнезии)
            # - referrals (реферальная система)

        # ❗ Жалобы и баны НЕ трогаем:
        # - user_reports оставляем как есть
        # - hidden_users с user_id = 0 (глобальные санкции) тоже сохранены
        # ✅ СОХРАНЯЕМ платежи и историю:
        # - is_founder, boost_expires_at (платежи)
        # - magnesium_balance, magnesium_log (магнезия)
        # - referrals (рефералы)

        await query.edit_message_text(TEXT2[lang]["profile_deleted"])

    elif query.data == "cancel_delete_profile":
        await query.edit_message_text(TEXT2[lang]["profile_delete_cancelled"])

async def handle_unlock_likes_prompt(update: Update,
                                     context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Проверяем статус Founder - автоматически открываем лайки
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT is_founder FROM users WHERE user_id = $1", user_id)
        if row and row['is_founder']:
            # Founder - сразу показываем лайки
            await handle_liked_me(update, context)
            return

    # Обычный пользователь - показываем подсказку с реферальной ссылкой
    inviter_id = query.from_user.id
    link = f"https://t.me/{context.bot.username}?start=ref{inviter_id}"

    await query.message.reply_text(
        TEXT2[lang]["likes_unlock_hint"].format(ref_link=link))


async def handle_my_likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Мои лайки - пагинация (первая страница)"""
    await show_sent_likes_page(update, context, page=0, is_first=True)


async def handle_get_magnesia(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Новое подменю получения магнезии"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Показываем новое меню с кнопками (1 строка - Друзья и Объявления вместе)
    menu = [
        [KeyboardButton(TEXTS[lang]["chalk_get_referral"]), KeyboardButton(TEXTS[lang]["chalk_get_board"])],
        [KeyboardButton(TEXTS[lang]["chalk_get_stars"]), KeyboardButton(TEXTS[lang]["chalk_get_founder"])],
        [KeyboardButton(TEXTS[lang]["chalk_get_back"])]
    ]
    markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    await update.message.reply_text(
        TEXT2[lang]["menu_chalk_title_hi"],
        reply_markup=markup
    )


async def handle_chalk_get_referral(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    """👥 Пригласить друга - отправляет сообщения про реферальную программу"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"

    # Определяем target для ответа (message или callback_query)
    query = update.callback_query
    if query:
        await query.answer()
        target = query.message
    else:
        target = update.message

    # Первое сообщение
    await target.reply_markdown(TEXT2[lang]["chalk_invite_intro"])
    await asyncio.sleep(1)

    # Второе сообщение с реферальной ссылкой
    message_text_2 = TEXT2[lang]["menu_likes_message_to_share"].format(ref_link=ref_link)
    await target.reply_html(message_text_2, disable_web_page_preview=True)


async def handle_chalk_get_board(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    """🧗 За объявления - про еженедельный бонус + кнопка к Встречам"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Инлайн-кнопка для быстрого перехода к Встречам прямо в сообщении
    keyboard = [[InlineKeyboardButton(TEXTS[lang]["menu_board"], callback_data="menu_board")]]
    await update.message.reply_markdown(
        TEXT2[lang]["chalk_board_weekly_bonus"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_chalk_get_stars(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    """⭐ Купить за Stars - показывает 3 тарифа"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Инлайн-кнопки с тарифами
    keyboard = [
        [InlineKeyboardButton("75 ⭐ - 10g 🗯", callback_data="buy_chalk_10")],
        [InlineKeyboardButton("150 ⭐ - 20g 🗯", callback_data="buy_chalk_20")],
        [InlineKeyboardButton("750 ⭐ - 100g 🗯", callback_data="buy_chalk_100")]
    ]

    await update.message.reply_html(
        TEXT2[lang]["chalk_stars_title"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


async def handle_chalk_get_founder(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    """💎 Поддержать проект - Founder статус за 5000 Stars"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Инлайн-кнопка с оплатой (мультиязычная через TEXT2)
    button_text = TEXT2[lang]["chalk_founder_button"]
    keyboard = [[InlineKeyboardButton(button_text, callback_data="buy_founder")]]

    await update.message.reply_html(
        TEXT2[lang]["chalk_founder_title"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


async def send_city_push_if_needed(context, user_id: int, city: str):
    """✅ ASYNC VERSION - отправка пуша новому пользователю в городе"""
    from datetime import datetime, timedelta

    now = datetime.now()

    # Проверка времени последнего пуша
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT last_push_time FROM city_push_log WHERE city = $1", city)

    should_push = False
    if not row:
        should_push = True
    else:
        last_push = row['last_push_time']
        if last_push is None or now - last_push > timedelta(hours=4):
            should_push = True

    if not should_push:
        return

    # Обновляем лог пушей
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO city_push_log (city, last_push_time)
            VALUES ($1, $2)
            ON CONFLICT (city) DO UPDATE SET last_push_time = EXCLUDED.last_push_time
            """, city, now)

    # Отправка уведомлений другим пользователям
    await asyncio.sleep(2)
    async with db_pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT user_id, language FROM users WHERE city = $1 AND user_id != $2 AND is_deleted = FALSE",
            city, user_id)

    if not users:
        return

    for user_row in users:
        other_user_id = user_row['user_id']
        lang = user_row['language'] or "ru"
        try:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(TEXTS[lang]["menu_search"], callback_data="go_to_search_menu")]
            ])
            await context.bot.send_message(
                chat_id=other_user_id, 
                text=TEXT2[lang]["city_new_user_push"],
                reply_markup=keyboard
            )
        except Exception as e:
            print(
                f"⚠️ Не удалось отправить пуш пользователю {other_user_id}: {e}"
            )


# 📋 Основная команда вызова админки
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if user_id not in ADMIN_IDS:
        await update.message.reply_text(TEXT2[lang]["admin_no_access"])
        return

    # Если уже авторизован
    if user_id in ADMIN_IDS:
        await show_admin_menu(update)
        return

    # Запрашиваем пароль
    context.user_data["awaiting_admin_password"] = True
    await update.message.reply_text("🔐 Введите пароль для доступа к админке:")


# 🌐 Функция миграции городов на Geoapify
async def migrate_cities_to_geoapify(message, context):
    """
    Миграция всех пользователей со старой системы городов на Geoapify.
    Для каждого уникального города делает запрос к Geoapify и обновляет БД.
    """
    try:
        # 1. Получаем всех пользователей с их городами
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT DISTINCT city, country 
                FROM users 
                WHERE city IS NOT NULL AND city != ''
                ORDER BY city
            """)

        if not rows:
            await message.reply_text("✅ Нет пользователей для миграции.")
            return

        total_cities = len(rows)
        await message.reply_text(f"📊 Найдено уникальных городов: {total_cities}\n\n🔄 Начинаю обработку...")

        # 2. Обрабатываем каждый город
        success_count = 0
        error_count = 0
        skipped_count = 0

        for idx, row in enumerate(rows, 1):
            old_city = row['city']
            old_country = row['country']

            # Пропускаем пустые города
            if not old_city or not old_city.strip():
                skipped_count += 1
                continue

            try:
                # Запрос к Geoapify (без user_id, чтобы не учитывать rate limit)
                cities = await geoapify_search_city(old_city, limit=1, user_id=None)

                if cities and len(cities) > 0:
                    new_city = cities[0]["city"]
                    new_country = cities[0]["country"]

                    # Обновляем всех пользователей с этим старым городом
                    async with db_pool.acquire() as conn:
                        result = await conn.execute("""
                            UPDATE users 
                            SET city = $1, country = $2 
                            WHERE city = $3
                        """, new_city, new_country, old_city)

                    success_count += 1

                    # Показываем прогресс каждые 10 городов
                    if idx % 10 == 0:
                        progress_text = (
                            f"📍 Прогресс: {idx}/{total_cities}\n"
                            f"✅ Обновлено: {success_count}\n"
                            f"❌ Ошибок: {error_count}\n"
                            f"⏭ Пропущено: {skipped_count}"
                        )
                        await message.reply_text(progress_text)

                    # Задержка для соблюдения rate limit Geoapify (3000/день = 2 req/sec макс)
                    await asyncio.sleep(0.5)

                else:
                    # Город не найден в Geoapify
                    error_count += 1
                    print(f"⚠️ Город '{old_city}' не найден в Geoapify")

            except Exception as e:
                error_count += 1
                print(f"❌ Ошибка обработки города '{old_city}': {e}")
                continue

        # 3. Итоговая статистика
        final_report = (
            f"🎉 Миграция завершена!\n\n"
            f"📊 Статистика:\n"
            f"• Всего городов: {total_cities}\n"
            f"• ✅ Успешно обновлено: {success_count}\n"
            f"• ❌ Ошибок: {error_count}\n"
            f"• ⏭ Пропущено: {skipped_count}\n\n"
            f"🌍 Теперь все пользователи используют нормализованные города из Geoapify!"
        )
        await message.reply_text(final_report)

    except Exception as e:
        await message.reply_text(f"❌ Критическая ошибка миграции: {e}")
        print(f"❌ Критическая ошибка migrate_cities_to_geoapify: {e}")


# 🔄 Функция сброса фильтров поиска для всех пользователей
async def reset_all_search_filters(message, context):
    """
    Безопасно сбрасывает фильтры поиска для всех активных пользователей.
    Устанавливает все фильтры на "любой"/"всех", город остаётся из профиля.
    """
    try:
        # 1. Получаем общее количество пользователей
        async with db_pool.acquire() as conn:
            total_users = await conn.fetchval("""
                SELECT COUNT(*) FROM users WHERE is_deleted = FALSE
            """)

        if total_users == 0:
            await message.reply_text("✅ Нет активных пользователей для сброса.")
            return

        await message.reply_text(f"📊 Найдено активных пользователей: {total_users}\n\n🔄 Начинаю сброс фильтров...")

        # 2. Сбрасываем все фильтры в NULL (по умолчанию = "любой/всех")
        async with db_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE search_filters SET
                    difficulty = NULL,
                    climb_type = NULL,
                    gender = NULL,
                    weight_min = NULL,
                    weight_max = NULL,
                    has_photo = NULL,
                    status_slug = NULL,
                    city_override = NULL,
                    sort_popular = NULL
                WHERE user_id IN (SELECT user_id FROM users WHERE is_deleted = FALSE)
            """)

        # 3. Подсчитываем, сколько фильтров было обновлено
        async with db_pool.acquire() as conn:
            reset_count = await conn.fetchval("""
                SELECT COUNT(*) FROM search_filters 
                WHERE difficulty IS NULL AND climb_type IS NULL AND gender IS NULL
                  AND weight_min IS NULL AND weight_max IS NULL AND has_photo IS NULL
                  AND status_slug IS NULL AND city_override IS NULL AND sort_popular IS NULL
            """)

        # 4. Отправляем успешный результат
        final_report = (
            f"🎉 Сброс фильтров завершён!\n\n"
            f"📊 Статистика:\n"
            f"• Всего пользователей: {total_users}\n"
            f"• ✅ Фильтров обнулено: {reset_count}\n\n"
            f"🔍 Фильтры установлены на:\n"
            f"• Уровень сложности: Любой\n"
            f"• Тип лазания: Любой\n"
            f"• Пол: Любой\n"
            f"• Вес: Любой\n"
            f"• Фото: Всех\n"
            f"• Статус: Любой\n"
            f"• Город: (из профиля каждого пользователя)\n"
            f"• Популярность: Не сортировать\n\n"
            f"✨ Все пользователи получат правильные фильтры по умолчанию!"
        )
        await message.reply_text(final_report)
        print(f"✅ Сброс фильтров завершён. Обновлено: {reset_count} фильтров из {total_users} пользователей")

    except Exception as e:
        await message.reply_text(f"❌ Ошибка при сбросе фильтров: {e}")
        print(f"❌ Ошибка reset_all_search_filters: {e}")


# 📩 Обработка нажатий по кнопкам админки
async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print("⚙️ admin_callback_handler triggered:", query.data)
    await query.answer()
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.message.reply_text("⛔ Нет доступа.")
        return

    action = query.data
    context.user_data["admin_action"] = action

    # ========== НАВИГАЦИЯ ПО ПОДМЕНЮ ==========

    # Показать подменю модерации
    if action == "admin_moderation_menu":
        await show_moderation_menu(query)
        return

    # Показать подменю статистики
    if action == "admin_stats_menu":
        await show_stats_menu(query)
        return

    # Показать подменю рассылок
    if action == "admin_broadcast_menu":
        await show_broadcast_menu(query)
        return

    # Возврат в главное меню
    if action == "admin_back_to_main":
        keyboard = [
            [InlineKeyboardButton("🔍 Поиск пользователя", callback_data="admin_search_user")],
            [InlineKeyboardButton("🚨 Модерация", callback_data="admin_moderation_menu")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats_menu")],
            [InlineKeyboardButton("📢 Рассылки", callback_data="admin_broadcast_menu")],
            [InlineKeyboardButton("✉️ Написать сообщение", callback_data="admin_send_message")],
            [InlineKeyboardButton("🗑️ Удалить профиль по ID", callback_data="admin_delete_profile_by_id")],
            [InlineKeyboardButton("🔙 Выйти из админки", callback_data="admin_exit")],
        ]
        await query.message.edit_text(
            "👑 Админ-панель:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ========== НОВЫЕ ФУНКЦИИ ==========

    # Поиск пользователя
    if action == "admin_search_user":
        await query.message.reply_text(
            "🔍 Введите имя пользователя или город для поиска:"
        )
        context.user_data["admin_action"] = "admin_search_user"
        return

    # Последние 10 зарегистрированных
    if action == "admin_recent_users":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, name, city, country, registration_date
                FROM users
                WHERE registration_date IS NOT NULL
                ORDER BY registration_date DESC
                LIMIT 10
            """)

        if not rows:
            await query.message.reply_text("📭 Пока нет зарегистрированных пользователей.")
            return

        buttons = []
        for row in rows:
            user_id = row['user_id']
            name = row['name'] or "Без имени"
            city = row['city'] or "Неизвестно"
            country = row['country'] or ""
            reg_date = row['registration_date'].strftime("%d.%m.%Y") if row['registration_date'] else "?"

            label = f"{name} ({city}, {country}) - {reg_date}"
            buttons.append([
                InlineKeyboardButton(label, callback_data=f"admin_view_user_{user_id}")
            ])

        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_moderation_menu")])

        await query.message.edit_text(
            "👤 Последние 10 регистраций:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Мои скрытые пользователи (для диагностики 117→95)
    if action == "admin_my_hidden_count":
        admin_id = query.from_user.id
        async with db_pool.acquire() as conn:
            # Получаем город админа и его фильтры
            admin_row = await conn.fetchrow("""
                SELECT u.city, u.city_other,
                       sf.difficulty, sf.climb_type, sf.gender, sf.weight_min, sf.weight_max,
                       sf.has_photo, sf.status_slug, sf.city_override
                FROM users u
                LEFT JOIN search_filters sf ON sf.user_id = u.user_id
                WHERE u.user_id = $1
            """, admin_id)
            if not admin_row:
                await query.message.reply_text("❌ Профиль не найден")
                return

            admin_city = admin_row['city_other'] if admin_row['city'] == "Другой" else admin_row['city']
            search_city = admin_row['city_override'] if admin_row['city_override'] else admin_city

            # Считаем пользователей в городе
            total_in_city = await conn.fetchval("""
                SELECT COUNT(*) FROM users 
                WHERE (city = $1 OR city_other = $1) AND is_deleted = FALSE
            """, search_city)

            # Считаем скрытых мной
            my_hidden = await conn.fetchval("""
                SELECT COUNT(*) FROM hidden_users 
                WHERE user_id = $1 AND (hide_until IS NULL OR hide_until > CURRENT_TIMESTAMP)
            """, admin_id)

            # Скрытых в этом городе
            hidden_in_city = await conn.fetchval("""
                SELECT COUNT(*) FROM hidden_users hu
                JOIN users u ON hu.hidden_user_id = u.user_id
                WHERE hu.user_id = $1 
                  AND (u.city = $2 OR u.city_other = $2)
                  AND u.is_deleted = FALSE
                  AND (hu.hide_until IS NULL OR hu.hide_until > CURRENT_TIMESTAMP)
            """, admin_id, search_city)

            # Проверяем другие исключения
            # 1. Пользователи без числового веса (если фильтр веса активен)
            weight_excluded = 0
            if admin_row['weight_min'] is not None and admin_row['weight_max'] is not None:
                weight_excluded = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE (city = $1 OR city_other = $1) AND is_deleted = FALSE
                      AND user_id != $2
                      AND (weight IS NULL OR weight !~ E'^\\d+$' 
                           OR CAST(weight AS INTEGER) NOT BETWEEN $3 AND $4)
                """, search_city, admin_id, admin_row['weight_min'], admin_row['weight_max'])

            # 2. Фильтр climb_type
            climb_excluded = 0
            if admin_row['climb_type'] and admin_row['climb_type'].strip() != "any":
                climb_excluded = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE (city = $1 OR city_other = $1) AND is_deleted = FALSE
                      AND user_id != $2
                      AND (climb_type IS NULL OR climb_type != $3)
                """, search_city, admin_id, admin_row['climb_type'].strip())

            # 3. Фильтр gender
            gender_excluded = 0
            if admin_row['gender'] and admin_row['gender'].strip() != "any":
                gender_excluded = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE (city = $1 OR city_other = $1) AND is_deleted = FALSE
                      AND user_id != $2
                      AND (gender IS NULL OR gender != $3)
                """, search_city, admin_id, admin_row['gender'].strip())

            # 4. Фильтр has_photo
            photo_excluded = 0
            if admin_row['has_photo'] is True:
                photo_excluded = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE (city = $1 OR city_other = $1) AND is_deleted = FALSE
                      AND user_id != $2
                      AND (has_real_photo IS NULL OR has_real_photo = FALSE)
                """, search_city, admin_id)

            # 5. Фильтр status_slug
            status_excluded = 0
            if admin_row['status_slug']:
                status_excluded = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE (city = $1 OR city_other = $1) AND is_deleted = FALSE
                      AND user_id != $2
                      AND (status_slug IS NULL OR status_slug != $3)
                """, search_city, admin_id, admin_row['status_slug'])

            # Доступно для поиска (минус я сам)
            available = total_in_city - hidden_in_city - 1

        report = (
            f"🔍 Диагностика поиска:\n\n"
            f"📍 Город поиска: {search_city}\n"
            f"👥 Всего в городе: {total_in_city}\n"
            f"➖ Минус я сам: 1\n"
            f"🙈 Скрыто мной: {hidden_in_city}\n\n"
            f"📊 Базовый расчёт: {available}\n\n"
            f"⚙️ Активные фильтры:\n"
        )

        filters_active = []
        if admin_row['climb_type'] and admin_row['climb_type'].strip() != "any":
            filters_active.append(f"• Тип: {admin_row['climb_type']} (исключает ~{climb_excluded})")
        if admin_row['gender'] and admin_row['gender'].strip() != "any":
            filters_active.append(f"• Пол: {admin_row['gender']} (исключает ~{gender_excluded})")
        if admin_row['weight_min'] is not None:
            filters_active.append(f"• Вес: {admin_row['weight_min']}-{admin_row['weight_max']}кг (исключает ~{weight_excluded})")
        if admin_row['has_photo'] is True:
            filters_active.append(f"• Только с фото (исключает ~{photo_excluded})")
        if admin_row['status_slug']:
            filters_active.append(f"• Статус: {admin_row['status_slug']} (исключает ~{status_excluded})")
        if admin_row['difficulty'] and admin_row['difficulty'].strip() != "any":
            filters_active.append(f"• Сложность: {admin_row['difficulty']} (Python-фильтр)")

        if filters_active:
            report += "\n".join(filters_active)
        else:
            report += "Все фильтры = 'любой'"

        await query.message.reply_text(report)
        return

    # Топ городов
    if action == "admin_top_cities":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT city, country, COUNT(*) as user_count
                FROM users
                WHERE city IS NOT NULL AND city != '' AND is_deleted = FALSE
                GROUP BY city, country
                ORDER BY user_count DESC
            """)

        if not rows:
            await query.message.reply_text("📭 Нет данных по городам.")
            return

        total_users = sum(row['user_count'] for row in rows)
        report = f"📍 Все города ({len(rows)} городов, {total_users} чел.):\n\n"
        for idx, row in enumerate(rows, 1):
            city = row['city']
            country = row['country'] or "?"
            count = row['user_count']
            report += f"{idx}. {city}, {country} — {count}\n"

        # Telegram лимит 4096 символов — разбиваем на части
        if len(report) > 4000:
            parts = []
            current = ""
            for line in report.split("\n"):
                if len(current) + len(line) + 1 > 4000:
                    parts.append(current)
                    current = line + "\n"
                else:
                    current += line + "\n"
            if current:
                parts.append(current)

            for part in parts:
                await query.message.reply_text(part)
        else:
            await query.message.reply_text(report)
        return

    # Статистика встреч
    if action == "admin_meetups_stats":
        async with db_pool.acquire() as conn:
            # Общая статистика
            total_sessions = await conn.fetchval("SELECT COUNT(*) FROM gym_sessions") or 0
            total_participants = await conn.fetchval("SELECT COUNT(*) FROM gym_session_participants") or 0
            unique_users = await conn.fetchval("SELECT COUNT(DISTINCT user_id) FROM gym_session_participants") or 0

            # Отзывы
            positive = await conn.fetchval("SELECT COUNT(*) FROM training_feedback WHERE rating = 'good'") or 0
            negative = await conn.fetchval("SELECT COUNT(*) FROM training_feedback WHERE rating = 'bad'") or 0

            # Награды выданы
            rewards_given = await conn.fetchval("SELECT COUNT(*) FROM training_logs WHERE rewarded = TRUE") or 0
            total_chalk = rewards_given * 2

            # Топ залов по участникам
            top_gyms = await conn.fetch("""
                SELECT gs.gym_name, COUNT(gsp.id) as participant_count
                FROM gym_sessions gs
                LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                WHERE gs.gym_name IS NOT NULL
                GROUP BY gs.gym_name
                ORDER BY participant_count DESC
                LIMIT 5
            """)

        report = (
            f"🤝 Статистика встреч:\n\n"
            f"📅 Всего сессий: {total_sessions}\n"
            f"👥 Участий: {total_participants}\n"
            f"🧑 Уникальных участников: {unique_users}\n\n"
            f"📊 Отзывы:\n"
            f"👍 Позитивных: {positive}\n"
            f"👎 Негативных: {negative}\n\n"
            f"🏆 Награды:\n"
            f"💳 Выдано наград: {rewards_given}\n"
            f"📦 Магнезии выдано: {total_chalk}г\n\n"
        )

        if top_gyms:
            report += "🏟 Топ залов:\n"
            for i, gym in enumerate(top_gyms, 1):
                report += f"{i}. {gym['gym_name']} — {gym['participant_count']} чел.\n"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")]]
        await query.message.reply_text(report, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ========== СУЩЕСТВУЮЩИЕ ФУНКЦИИ ==========

    # Админ Локальная рассылка (через Geoapify)
    if action == "admin_broadcast_location":
        context.user_data["broadcast_stage"] = "awaiting_broadcast_city"
        context.user_data.pop("broadcast_city", None)
        await query.message.reply_text(
            "📢 Локальная рассылка\n\n"
            "🌍 Введите название города для рассылки (например, Москва, Санкт-Петербург):"
        )
        return

    # Выбор города для локальной рассылки из Geoapify
    if action.startswith("admin_broadcast_city_"):
        try:
            idx = int(action.replace("admin_broadcast_city_", ""))
            cities = context.user_data.get("broadcast_city_results", [])

            if idx < 0 or idx >= len(cities):
                await query.message.reply_text("❌ Неверный выбор города.")
                return

            selected_city = cities[idx]
            city = selected_city["city"]
            country = selected_city["country"]

            # Сохраняем выбранный город
            context.user_data["broadcast_city"] = city
            context.user_data["broadcast_stage"] = "awaiting_broadcast_message"

            # Получаем количество пользователей в этом городе
            async with db_pool.acquire() as conn:
                user_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM users WHERE city = $1 AND is_deleted = FALSE
                """, city)

            await query.message.edit_text(
                f"📢 Локальная рассылка\n\n"
                f"Город: {city}, {country}\n"
                f"Пользователей: {user_count} чел.\n\n"
                f"✏️ Введите текст сообщения для рассылки:"
            )

        except Exception as e:
            await query.message.reply_text(f"❌ Ошибка выбора города: {e}")
            print(f"❌ Ошибка admin_broadcast_city: {e}")
        return

    # Просмотр пользователя по ID из кнопки
    if action.startswith("admin_view_user_"):
        target_user_id = int(action.replace("admin_view_user_", ""))

        async with db_pool.acquire() as conn:
            user_row = await conn.fetchrow("""
                SELECT user_id, name, city, country, climb_type, difficulty, gender, weight, bio, status_slug, photo_bytes
                FROM users
                WHERE user_id = $1
            """, target_user_id)

        if not user_row:
            await query.message.reply_text("❌ Пользователь не найден.")
            return

        # Формируем профиль
        profile_text = (
            f"👤 Профиль пользователя\n\n"
            f"ID: {user_row['user_id']}\n"
            f"Имя: {user_row['name'] or 'Не указано'}\n"
            f"Город: {user_row['city'] or 'Не указано'}, {user_row['country'] or ''}\n"
            f"Тип лазания: {user_row['climb_type'] or 'Не указано'}\n"
            f"Уровень: {user_row['difficulty'] or 'Не указано'}\n"
            f"Пол: {user_row['gender'] or '?'}\n"
            f"Вес: {user_row['weight'] or '?'} кг\n"
            f"Статус: {user_row['status_slug'] or 'Не указан'}\n\n"
            f"О себе: {user_row['bio'] or 'Не заполнено'}"
        )

        # Если есть фото - отправляем с фото
        from io import BytesIO
        if user_row['photo_bytes']:
            try:
                photo_io = BytesIO(user_row['photo_bytes'])
                photo_io.name = "profile.jpg"
                photo_io.seek(0)

                await query.message.reply_photo(
                    photo=photo_io,
                    caption=profile_text,
                    has_spoiler=False
                )
            except Exception as e:
                print(f"❌ Ошибка отправки фото: {e}")
                await query.message.reply_text(profile_text)
        else:
            await query.message.reply_text(profile_text)

        return

    # Анкета по ID
    if action == "admin_view_profile":
        await query.message.reply_text("✏️ Введите ID пользователя:")
        context.user_data["admin_action"] = "admin_view_profile"
        return

    # Жалобы по категориям
    if action == "admin_reports_by_reason":
        async with db_pool.acquire() as conn:
            reasons = await conn.fetch("""
                SELECT DISTINCT reason FROM user_reports
                WHERE reason IS NOT NULL
                ORDER BY reason
            """)

        if not reasons:
            await query.message.reply_text("🙈 Жалоб пока нет.")
            return

        buttons = [[
            InlineKeyboardButton(row['reason'], callback_data=f"admin_report_group_{row['reason']}")
        ] for row in reasons]

        await query.message.reply_text("🚨 Выбери тип жалобы:",
                                       reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Просмотр пользователей по жалобе
    if action.startswith("admin_report_group_"):
        reason = action.replace("admin_report_group_", "")
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT reported_id, COUNT(*) as cnt
                FROM user_reports
                WHERE reason = $1
                GROUP BY reported_id
                ORDER BY cnt DESC
                LIMIT 30
            """, reason)

        if not rows:
            await query.message.reply_text("❌ Нет жалоб по этой категории.")
            return

        buttons = [[
            InlineKeyboardButton(f"ID {row['reported_id']} ({row['cnt']} жалоб)", callback_data=f"admin_view_ban_{row['reported_id']}")
        ] for row in rows]

        await query.message.reply_text(
            f"📋 Пользователи с жалобами типа \"{reason}\":",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Админ Массовая рассылка
    if action == "admin_broadcast_all":
        context.user_data["broadcast_stage"] = "broadcast_all"
        await query.message.reply_text(
            "📣 Пришли сообщение (можно с фото), которое хочешь отправить всем пользователям."
        )
        return

    # Админ Рассылка RU (только пользователям с lang=ru)
    if action == "admin_broadcast_ru":
        await query.answer()
        await query.message.reply_text("🇷🇺 Начинаю рассылку для русскоязычных пользователей...")
        await admin_broadcast_ru(query.message, context)
        return

    # Админ Миграция городов на Geoapify
    if action == "admin_migrate_cities":
        await query.message.reply_text("🌐 Запускаю миграцию городов на Geoapify...\n\n⏳ Это может занять несколько минут.")
        await migrate_cities_to_geoapify(query.message, context)
        return

    # Админ Сброс фильтров поиска всем пользователям
    if action == "admin_reset_filters":
        await query.message.reply_text("🔄 Запускаю сброс фильтров поиска всем пользователям...\n\n⏳ Обработка может занять время.")
        await reset_all_search_filters(query.message, context)
        return

    # Админ выход
    if action == "admin_exit":
        user_id = update.effective_user.id
        await ensure_lang(context, user_id)
        lang = context.user_data.get("lang", "ru")

        context.user_data["admin_action"] = None
        context.user_data.pop("awaiting_admin_password", None)
        reset_user_context(context)

        await query.message.reply_text("🔓 Вы вышли из админ-панели.")

        # Меню
        menu_buttons = [
            [KeyboardButton(TEXTS[lang]["menu_likes"]), KeyboardButton(TEXTS[lang]["menu_search"])],
            [KeyboardButton(TEXTS[lang]["menu_chats"]),   KeyboardButton(TEXTS[lang]["menu_board"])],
            [KeyboardButton(TEXTS[lang]["menu_form"]),    KeyboardButton(TEXTS[lang]["menu_chalk"]), KeyboardButton(TEXTS[lang]["menu_about"])]
        ]

        await query.message.reply_text(
            TEXT2[lang]["menu_main"],
            reply_markup=ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        )
        return


    # Админ Статистика
    if action == "admin_stats":
        keyboard = [
            [
                InlineKeyboardButton("1️⃣ Общее количество лайков", callback_data="stats_likes")
            ],
            [
                InlineKeyboardButton("2️⃣ Кол-во прокси-чатов", callback_data="stats_proxies")
            ],
            [
                InlineKeyboardButton("3️⃣ Нажали /start", callback_data="stats_start")
            ],
            [
                InlineKeyboardButton("4️⃣ Завершили регистрацию", callback_data="stats_registered")
            ],
            [
                InlineKeyboardButton("5️⃣ Среднее время регистрации", callback_data="stats_avg_time")
            ],
        ]
        await query.message.reply_text("📊 Выбери метрику:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Админ Список забаненных пользователей
    if action == "admin_banned_list":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT hidden_user_id, hide_until
                FROM hidden_users
                WHERE user_id = 0
                ORDER BY hide_until DESC
            """)

        if not rows:
            await query.message.reply_text("🙈 Пока никто не забанен.")
        else:
            banned_buttons = []
            for row in rows:
                user_id_row = row['hidden_user_id']
                banned_buttons.append([
                    InlineKeyboardButton(f"👁 Жалобы: {user_id_row}", callback_data=f"admin_view_ban_{user_id_row}"),
                    InlineKeyboardButton("🔓 Разблокировать", callback_data=f"admin_unban_{user_id_row}")
                ])
            banned_buttons.append([
                InlineKeyboardButton("🆕 Свежие баны (7 дней)", callback_data="admin_recent_banned")
            ])
            await query.message.reply_text(
                "👥 Забаненные пользователи (нажми 👁 чтобы увидеть жалобы или 🔓 чтобы разблокировать):",
                reply_markup=InlineKeyboardMarkup(banned_buttons))
        return

    # Админ Показать свежие баны (за 7 дней)
    if action == "admin_recent_banned":
        cutoff = datetime.now() - timedelta(days=7)

        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT hidden_user_id, hide_until
                FROM hidden_users
                WHERE user_id = 0 AND hide_until > $1
                ORDER BY hide_until DESC
            """, cutoff)

        if not rows:
            await query.message.reply_text("🙈 Свежих банов за последние 7 дней нет.")
        else:
            banned_buttons = []
            for row in rows:
                user_id_row = row['hidden_user_id']
                banned_buttons.append([
                    InlineKeyboardButton(f"👁 Жалобы: {user_id_row}", callback_data=f"admin_view_ban_{user_id_row}"),
                    InlineKeyboardButton("🔓 Разблокировать", callback_data=f"admin_unban_{user_id_row}")
                ])
            await query.message.reply_text("🆕 Забаненные за последние 7 дней:",
                                           reply_markup=InlineKeyboardMarkup(banned_buttons))
        return

    # Просмотр жалоб на пользователя
    if action.startswith("admin_view_ban_"):
        banned_user_id = int(action.replace("admin_view_ban_", ""))
        cursor.execute("""
            SELECT reason, timestamp
            FROM user_reports
            WHERE reported_id = $1
            ORDER BY timestamp DESC
        """, (banned_user_id, ))

        reasons = cursor.fetchall()

        if not reasons:
            await query.message.reply_text("❓ Жалобы на пользователя не найдены.")
        else:
            reasons_text = "\n\n".join(
                [f"🕒 {row[1]}: {row[0]}" for row in reasons])
            await query.message.reply_text(
                f"📋 Жалобы на пользователя {banned_user_id}:\n\n{reasons_text}"
            )
        return

    # Выдать список пользователей с кастомными странами/городами
    if action == "admin_custom_locations":
        cursor.execute("""
            SELECT user_id, name, country_other, city_other
            FROM users
            WHERE 
                (country_other IS NOT NULL AND LENGTH(TRIM(country_other)) > 0)
                OR
                (city_other IS NOT NULL AND LENGTH(TRIM(city_other)) > 0)
            ORDER BY registration_date DESC
            LIMIT 50
        """)


        if not rows:
            await query.message.reply_text("🌍 Нет кастомных стран и городов.")
            return

        text = "📋 Пользователи с кастомными странами/городами:\n\n"
        for uid, name, country, city in rows:
            text += f"• ID: {uid} | {name or '—'}\n"
            text += f"   Страна: {country or '—'} | Город: {city or '—'}\n\n"

        await query.message.reply_text(text[:4000])
        return

    # Разблокировать пользователя
    if action.startswith("admin_unban_"):
        unban_user_id = int(action.replace("admin_unban_", ""))
        async with db_pool.acquire() as conn:
            await conn.execute("DELETE FROM hidden_users WHERE hidden_user_id = $1",
                           unban_user_id)
        await query.message.reply_text(f"✅ Пользователь {unban_user_id} разблокирован.")
        return


    # Удалить профиль по ID
    if action == "admin_delete_profile_by_id":
        context.user_data["awaiting_admin_delete_id"] = True
        await query.message.reply_text("✏️ Введите ID пользователя, которого нужно удалить:")
        return

    # Если не попало ни в один блок — просим ввести ID
    await query.message.reply_text("✏️ Введи ID пользователя для выполнения действия:")



# ✏️ Обработка ввода ID пользователя и выполнение действия


async def admin_handle_text(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # 🔥 Проверяем: это вообще админ и ожидается ли действие
    if user_id not in ADMIN_IDS:
        return

    # ========== ПРОВЕРКА BROADCAST_STAGE (приоритет над admin_action) ==========
    broadcast_stage = context.user_data.get("broadcast_stage")

    # Если идёт broadcast_stage, обрабатываем независимо от admin_action
    if broadcast_stage:
        text = update.message.text.strip()

        # Если идёт процесс локальной рассылки через Geoapify
        if broadcast_stage == "awaiting_broadcast_city":
            # Запрос к Geoapify
            cities = await geoapify_search_city(text, limit=5, user_id=None)

            if not cities:
                await update.message.reply_text(
                    "❌ Города не найдены. Попробуйте другое название."
                )
                return

            # Показываем результаты с кнопками выбора
            keyboard = []
            for idx, city_data in enumerate(cities):
                city = city_data["city"]
                country = city_data["country"]
                flag = city_data.get("flag", "")

                button_text = f"{flag} {city}, {country}"
                keyboard.append([
                    InlineKeyboardButton(button_text, callback_data=f"admin_broadcast_city_{idx}")
                ])

            # Сохраняем результаты в context
            context.user_data["broadcast_city_results"] = cities

            keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="admin_broadcast_menu")])

            await update.message.reply_text(
                "📢 Выберите город для рассылки:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Если ожидается текст сообщения для рассылки
        if broadcast_stage == "awaiting_broadcast_message":
            city = context.user_data.get("broadcast_city")

            # Получаем всех пользователей из этого города
            async with db_pool.acquire() as conn:
                users = await conn.fetch("""
                    SELECT user_id FROM users
                    WHERE city = $1
                """, city)

            if not users:
                await update.message.reply_text(f"❌ В городе {city} нет пользователей.")
                context.user_data["broadcast_stage"] = None
                return

            # Рассылка сообщения
            success_count = 0
            fail_count = 0

            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user['user_id'],
                        text=f"📢 Сообщение для вашего города:\n\n{text}"
                    )
                    success_count += 1
                    await asyncio.sleep(0.05)  # Защита от rate limit
                except Exception as e:
                    fail_count += 1
                    print(f"❌ Ошибка отправки сообщения пользователю {user['user_id']}: {e}")

            await update.message.reply_text(
                f"✅ Рассылка завершена!\n\n"
                f"📊 Город: {city}\n"
                f"✅ Отправлено: {success_count}\n"
                f"❌ Ошибок: {fail_count}"
            )

            context.user_data["broadcast_stage"] = None
            context.user_data.pop("broadcast_city", None)
            context.user_data.pop("broadcast_city_results", None)
            return

    # Если нет broadcast_stage, проверяем admin_action
    if "admin_action" not in context.user_data or not context.user_data["admin_action"]:
        return  # ➔ НЕТ admin_action ➔ Передаем дальше!

    action = context.user_data.get("admin_action")
    if not action:
        return

    text = update.message.text.strip()

    # ========== ПОИСК ПОЛЬЗОВАТЕЛЯ ==========
    if action == "admin_search_user":
        async with db_pool.acquire() as conn:
            # Поиск по имени или городу
            rows = await conn.fetch("""
                SELECT user_id, name, city, country
                FROM users
                WHERE LOWER(name) LIKE $1 OR LOWER(city) LIKE $1
                LIMIT 20
            """, f"%{text.lower()}%")

        if not rows:
            await update.message.reply_text("❌ Пользователи не найдены.")
            context.user_data["admin_action"] = None
            return

        buttons = []
        for row in rows:
            user_id = row['user_id']
            name = row['name'] or "Без имени"
            city = row['city'] or "?"
            country = row['country'] or ""

            label = f"{name} ({city}, {country})"
            buttons.append([
                InlineKeyboardButton(label, callback_data=f"admin_view_user_{user_id}")
            ])

        await update.message.reply_text(
            f"🔍 Найдено пользователей: {len(rows)}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        context.user_data["admin_action"] = None
        return

    # ========== ОСТАЛЬНЫЕ ДЕЙСТВИЯ (требуют числовой ID) ==========
    if not text.isdigit():
        await update.message.reply_text("❌ Введи числовой ID.")
        return

    target_id = int(text)

    if action == "admin_unblock":
        async with db_pool.acquire() as conn:
            await conn.execute("DELETE FROM hidden_users WHERE hidden_user_id = $1",
                           target_id)
        await update.message.reply_text(
            f"✅ Пользователь {target_id} разблокирован.")


    elif action == "admin_view_profile":
        try:
            target_id = int(text.strip())
        except ValueError:
            await update.message.reply_text("❌ Введи корректный числовой ID.")
            return

        async with db_pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT name, country, country_other, city, city_other,
                       difficulty, climb_type, gender, weight, bio, photo_bytes
                FROM users WHERE user_id = $1
            """, target_id)

        if not user:
            await update.message.reply_text("❌ Пользователь не найден.")
        else:
            name = user['name']
            country = user['country']
            country_other = user['country_other']
            city = user['city']
            city_other = user['city_other']
            diff = user['difficulty']
            climb = user['climb_type']
            gender = user['gender']
            weight = user['weight']
            bio = user['bio']
            photo_bytes = user['photo_bytes']
            country_display = country_other or country or "—"
            city_display = city_other or city or "—"

            caption = (
                f"👤 *{escape_markdown(name or '—')}*\n"
                f"Страна: {escape_markdown(country_display)}\n"
                f"Город: {escape_markdown(city_display)}\n"
                f"Уровень: {DIFFICULTY_LABELS.get(diff, diff) if diff else '—'}\n"
                f"Тип: {get_climb_label(climb, 'ru') if climb else '—'}\n"
                f"Пол: {get_gender_label(gender, 'ru') if gender else '—'}\n"
                f"Вес: {get_weight_label(weight, 'ru') if weight else '—'}\n"
                f"📝 О себе: {escape_markdown(bio) if bio else '—'}"
            )

            from io import BytesIO
            try:
                if photo_bytes:
                    image_io = BytesIO(photo_bytes)
                    image_io.name = "photo.jpg"
                    image_io.seek(0)

                    await update.message.reply_photo(
                        photo=image_io,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text(
                        caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
            except Exception as e:
                print("⚠️ Ошибка при отправке фото в админке:", e)
                await update.message.reply_text(caption)

        context.user_data["admin_action"] = None
        return


    elif action == "admin_ban":
        ban_until = datetime.now() + timedelta(days=365)
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO hidden_users (user_id, hidden_user_id, hide_until, notified)
                VALUES ($1, $2, $3, 0)
                ON CONFLICT (user_id, hidden_user_id) DO UPDATE
                SET hide_until = EXCLUDED.hide_until,
                    notified = EXCLUDED.notified
                """, 0, target_id, ban_until.isoformat())

        await update.message.reply_text(
            f"🚫 Пользователь {target_id} забанен на 1 год.")

    elif action == "admin_view_chats":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT sender_id, message, timestamp
                FROM chat_messages
                WHERE sender_id = $1 OR chat_id LIKE $2
                ORDER BY timestamp DESC
                LIMIT 10
                """, target_id, f"%{target_id}%")

        if not rows:
            await update.message.reply_text("🙈 Нет сообщений.")
        else:
            text = "\n\n".join(
                [f"🗨 {row['sender_id']}: {row['message']} ({row['timestamp']})" for row in rows])
            await update.message.reply_text(f"📚 Последние сообщения:\n\n{text}"
                                            )

    elif action == "admin_reset_user":
        async with db_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM likes WHERE from_user_id = $1 OR to_user_id = $2",
                target_id, target_id)
            await conn.execute("DELETE FROM search_filters WHERE user_id = $1",
                           target_id)
        await update.message.reply_text(
            f"🧹 Данные пользователя {target_id} очищены (лайки и фильтры).")

    elif action == "admin_send_message":
        context.user_data["admin_target_id"] = target_id
        await update.message.reply_text(
            "✏️ Введи текст сообщения для отправки пользователю:")

    context.user_data["admin_action"] = None


# ✉️ Отправка сообщения пользователю
async def admin_handle_message_text(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    if "admin_target_id" not in context.user_data or not context.user_data[
            "admin_target_id"]:
        return  # ➔ НЕТ admin_target_id ➔ Передаем дальше!

    if user_id not in ADMIN_IDS:
        return

    target_id = context.user_data.get("admin_target_id")
    if not target_id:
        return

    message_text = update.message.text.strip()
    try:
        await context.bot.send_message(
            chat_id=target_id, text=f"📬 Admin *Cragsy*:\n\n{message_text}")
        await update.message.reply_text(
            f"✅ Сообщение отправлено пользователю {target_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отправки сообщения: {e}")

    context.user_data["admin_target_id"] = None


async def admin_handle_broadcast_all(update: Update,
                                     context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    message = update.message
    text = message.caption if message.caption else message.text
    photo = message.photo[-1].file_id if message.photo else None

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
    recipients = [row['user_id'] for row in rows]

    sent = 0
    for uid in recipients:
        try:
            if photo:
                await context.bot.send_photo(chat_id=uid,
                                             photo=photo,
                                             caption=text or "")
            else:
                await context.bot.send_message(chat_id=uid, text=text or "")
            sent += 1
        except:
            continue

    await update.message.reply_text(
        f"✅ Рассылка отправлена {sent} пользователям.")
    context.user_data["broadcast_stage"] = None


async def admin_broadcast_ru(message, context: ContextTypes.DEFAULT_TYPE):
    """🇷🇺 Рассылка для русскоязычных пользователей (lang=ru)"""
    broadcast_text = (
        "🎉 <b>Обновленное меню: Встречи!</b>\n\n"
        "Теперь можно найти партнёра для тренировки еще быстрее:\n\n"
        "🧗 Выбери зал и время\n"
        "👥 Присоединяйся к тренировке\n"
        "💬 Общайся с участниками в групповом чате\n\n"
        "Для <b>Москвы</b> и <b>Санкт-Петербурга</b> — добавлены популярные скалодромы!\n\n"
        "Для других городов — создавай свободные тренировки и находи компанию рядом.\n\n"
        "Попробуй прямо сейчас 👇"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤝 Открыть Встречи", callback_data="meetups_menu")
        ]
    ])
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users WHERE language = 'ru' AND is_deleted = FALSE")
    recipients = [row['user_id'] for row in rows]
    sent = 0
    failed = 0
    for uid in recipients:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=broadcast_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            sent += 1
        except Exception as e:
            failed += 1
            continue
    await message.reply_text(
        f"✅ Рассылка RU завершена!\n\n"
        f"📤 Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}"
    )
    
async def handle_admin_location_selection(update: Update,
                                          context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get(
            "broadcast_stage") == "select_country" and query.data.startswith(
                "country_"):
        country = query.data.replace("country_", "")
        context.user_data["broadcast_country"] = country
        context.user_data["broadcast_stage"] = "select_city"
        await query.message.reply_text(
            f"🏙 Вы выбрали страну: {country}. Теперь выберите город:",
            reply_markup=get_city_keyboard(context, country))
        return

    if context.user_data.get(
            "broadcast_stage") == "select_city" and query.data.startswith(
                "city_"):
        city = query.data.replace("city_", "")
        context.user_data["broadcast_city"] = city
        context.user_data["broadcast_stage"] = "awaiting_media"
        await query.message.reply_text(
            "📨 Пришли текст объявления (можно с фото).")
        return


async def handle_admin_broadcast_message(update: Update,
                                         context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    message = update.message
    text = message.caption if message.caption else message.text
    photo = message.photo[-1].file_id if message.photo else None

    country = context.user_data.get("broadcast_country")
    city = context.user_data.get("broadcast_city")

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id FROM users WHERE country = $1 AND city = $2 AND is_deleted = FALSE",
            country, city)
    recipients = [row['user_id'] for row in rows]

    sent = 0
    for uid in recipients:
        try:
            if photo:
                await context.bot.send_photo(chat_id=uid,
                                             photo=photo,
                                             caption=text or "")
            else:
                await context.bot.send_message(chat_id=uid, text=text or "")
            sent += 1
        except Forbidden:
            print(f"❌ Сообщение НЕ доставлено — пользователь {uid} заблокировал бота.")
        except Exception as e:
            print(f"⚠️ Ошибка при отправке пользователю {uid}: {e}")
            continue

    await message.reply_text(f"✅ Рассылка отправлена {sent} пользователям.")
    context.user_data["broadcast_stage"] = None


async def handle_stats_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ========== DAU/WAU/MAU ==========
    if data == "stats_dau":
        async with db_pool.acquire() as conn:
            dau = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id) FROM user_logins 
                WHERE login_date = CURRENT_DATE
            """) or 0

            wau = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id) FROM user_logins 
                WHERE login_date >= CURRENT_DATE - INTERVAL '7 days'
            """) or 0

            mau = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id) FROM user_logins 
                WHERE login_date >= CURRENT_DATE - INTERVAL '30 days'
            """) or 0

            total = await conn.fetchval("""
                SELECT COUNT(*) FROM registration_times WHERE finish_time IS NOT NULL
            """) or 0

        stickiness = round(dau / wau * 100, 1) if wau else 0

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")]]
        await query.message.reply_text(
            f"🔥 Активность:\n\n"
            f"📅 DAU (сегодня): {dau}\n"
            f"📆 WAU (7 дней): {wau}\n"
            f"🗓 MAU (30 дней): {mau}\n"
            f"👥 Всего пользователей: {total}\n\n"
            f"📊 Stickiness (DAU/WAU): {stickiness}%",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ========== RETENTION (новый) ==========
    elif data == "stats_retention_new":
        keyboard = [
            [InlineKeyboardButton("D1 (вчера)", callback_data="stats_ret_1")],
            [InlineKeyboardButton("D7 (неделя)", callback_data="stats_ret_7")],
            [InlineKeyboardButton("D30 (месяц)", callback_data="stats_ret_30")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")],
        ]
        await query.message.reply_text(
            "📈 Retention — % пользователей, вернувшихся после регистрации:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("stats_ret_"):
        days = int(data.split("_")[-1])

        async with db_pool.acquire() as conn:
            cohort = await conn.fetch("""
                SELECT user_id FROM registration_times 
                WHERE finish_time::date = CURRENT_DATE - $1 * INTERVAL '1 day'
            """, days)
            cohort_ids = set(row['user_id'] for row in cohort)

            if cohort_ids:
                returned = await conn.fetch("""
                    SELECT DISTINCT user_id FROM user_logins 
                    WHERE user_id = ANY($1::bigint[])
                      AND login_date > CURRENT_DATE - $2 * INTERVAL '1 day'
                """, list(cohort_ids), days)
                returned_ids = set(row['user_id'] for row in returned)
            else:
                returned_ids = set()

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="stats_retention_new")]]
        if cohort_ids:
            percent = round(len(returned_ids) / len(cohort_ids) * 100, 1)
            await query.message.reply_text(
                f"📈 Retention D{days}:\n\n"
                f"👥 Зарегистрировались {days} дн. назад: {len(cohort_ids)}\n"
                f"🔄 Вернулись: {len(returned_ids)}\n"
                f"📊 Retention: {percent}%",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text(
                f"⚠️ Нет регистраций за D{days}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # ========== СТАТИСТИКА ПО МЕСЯЦАМ ==========
    elif data == "stats_monthly":
        keyboard = [
            [InlineKeyboardButton("❤️ Лайки", callback_data="stats_monthly_likes")],
            [InlineKeyboardButton("📝 Регистрации", callback_data="stats_monthly_regs")],
            [InlineKeyboardButton("💬 Сообщения", callback_data="stats_monthly_msgs")],
            [InlineKeyboardButton("🤝 Тренировки", callback_data="stats_monthly_meetups")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")],
        ]
        await query.message.reply_text(
            "📅 Статистика по месяцам (последние 6 мес.):", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "stats_monthly_likes":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT TO_CHAR(timestamp, 'YYYY-MM') as month, COUNT(*) as cnt
                FROM likes
                WHERE timestamp >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(timestamp, 'YYYY-MM')
                ORDER BY month DESC
            """)

        text = "❤️ Лайки по месяцам:\n\n"
        for row in rows:
            text += f"📅 {row['month']}: {row['cnt']}\n"
        if not rows:
            text += "Нет данных"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="stats_monthly")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "stats_monthly_regs":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT TO_CHAR(finish_time, 'YYYY-MM') as month, COUNT(*) as cnt
                FROM registration_times
                WHERE finish_time IS NOT NULL
                  AND finish_time >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(finish_time, 'YYYY-MM')
                ORDER BY month DESC
            """)

        text = "📝 Регистрации по месяцам:\n\n"
        for row in rows:
            text += f"📅 {row['month']}: {row['cnt']}\n"
        if not rows:
            text += "Нет данных"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="stats_monthly")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "stats_monthly_msgs":
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT TO_CHAR(timestamp, 'YYYY-MM') as month, COUNT(*) as cnt
                FROM chat_messages
                WHERE timestamp >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(timestamp, 'YYYY-MM')
                ORDER BY month DESC
            """)

        text = "💬 Сообщения по месяцам:\n\n"
        for row in rows:
            text += f"📅 {row['month']}: {row['cnt']}\n"
        if not rows:
            text += "Нет данных"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="stats_monthly")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "stats_monthly_meetups":
        async with db_pool.acquire() as conn:
            # Участия в тренировках
            participants = await conn.fetch("""
                SELECT TO_CHAR(joined_at, 'YYYY-MM') as month, COUNT(*) as cnt
                FROM gym_session_participants
                WHERE joined_at >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(joined_at, 'YYYY-MM')
                ORDER BY month DESC
            """)
    
            # Сообщения в групповых чатах
            messages = await conn.fetch("""
                SELECT TO_CHAR(sent_at, 'YYYY-MM') as month, COUNT(*) as cnt
                FROM group_chat_messages
                WHERE sent_at >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(sent_at, 'YYYY-MM')
                ORDER BY month DESC
            """)
    
        text = "🤝 *Meetups по месяцам:*\n\n"
        text += "📅 Участия в тренировках:\n"
        for row in participants:
            text += f"  {row['month']}: {row['cnt']}\n"
        if not participants:
            text += "  Нет данных\n"
    
        text += "\n💬 Сообщения в чатах:\n"
        for row in messages:
            text += f"  {row['month']}: {row['cnt']}\n"
        if not messages:
            text += "  Нет данных\n"
    
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="stats_monthly")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    # ========== СТАТИСТИКА ЧАТОВ ==========
    elif data == "stats_chats":
        async with db_pool.acquire() as conn:
            # === 1x1 ЧАТЫ ===
            # Уникальные пары чатов
            total_chats = await conn.fetchval("""
                SELECT COUNT(DISTINCT LEAST(user_id, partner_id)::text || '_' || GREATEST(user_id, partner_id)::text)
                FROM user_chats
            """) or 0

            # Чаты с сообщениями
            active_chats = await conn.fetchval("SELECT COUNT(DISTINCT chat_id) FROM chat_messages") or 0

            # Сообщений всего
            total_messages = await conn.fetchval("SELECT COUNT(*) FROM chat_messages") or 0

            # Сообщений за сегодня
            messages_today = await conn.fetchval("""
                SELECT COUNT(*) FROM chat_messages WHERE timestamp::date = CURRENT_DATE
            """) or 0

            # Сообщений за 7 дней
            messages_week = await conn.fetchval("""
                SELECT COUNT(*) FROM chat_messages 
                WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
            """) or 0

            # === ГРУППОВЫЕ ЧАТЫ (Meetups) ===
            # Активные чаты (не удалённые)
            group_chats_active = await conn.fetchval("SELECT COUNT(*) FROM group_chats") or 0

            # Всего чатов за всё время (по уникальным chat_id в сообщениях)
            group_chats_total = await conn.fetchval("""
                SELECT COUNT(DISTINCT chat_id) FROM group_chat_messages
            """) or 0

            # Сообщений в групповых чатах
            group_messages = await conn.fetchval("SELECT COUNT(*) FROM group_chat_messages") or 0

            # Сообщений за сегодня
            group_messages_today = await conn.fetchval("""
                SELECT COUNT(*) FROM group_chat_messages WHERE sent_at::date = CURRENT_DATE
            """) or 0

            # Сообщений за 7 дней
            group_messages_week = await conn.fetchval("""
                SELECT COUNT(*) FROM group_chat_messages 
                WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days'
            """) or 0

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")]]
        await query.message.reply_text(
            f"💬 Статистика чатов:\n\n"
            f"👥 *1x1 чаты:*\n"
            f"├ Всего пар: {total_chats}\n"
            f"├ С сообщениями: {active_chats}\n"
            f"├ Сообщений всего: {total_messages}\n"
            f"├ За сегодня: {messages_today}\n"
            f"└ За 7 дней: {messages_week}\n\n"
            f"🤝 *Групповые чаты (Meetups):*\n"
            f"├ Активных сейчас: {group_chats_active}\n"
            f"├ Всего за всё время: {group_chats_total}\n"
            f"├ Сообщений всего: {group_messages}\n"
            f"├ За сегодня: {group_messages_today}\n"
            f"└ За 7 дней: {group_messages_week}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    # ========== СТАТИСТИКА ЛАЙКОВ (детальная) ==========
    elif data == "stats_likes_detailed":
        async with db_pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM likes") or 0
            today = await conn.fetchval("""
                SELECT COUNT(*) FROM likes WHERE timestamp::date = CURRENT_DATE
            """) or 0
            week = await conn.fetchval("""
                SELECT COUNT(*) FROM likes 
                WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
            """) or 0

            # Мэтчи (взаимные лайки)
            matches = await conn.fetchval("""
                SELECT COUNT(*) FROM likes l1
                JOIN likes l2 ON l1.from_user_id = l2.to_user_id 
                             AND l1.to_user_id = l2.from_user_id
                WHERE l1.from_user_id < l1.to_user_id
            """) or 0

        conversion = round(matches * 2 / total * 100, 1) if total else 0

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")]]
        await query.message.reply_text(
            f"❤️ Статистика лайков:\n\n"
            f"📊 Всего: {total}\n"
            f"📅 Сегодня: {today}\n"
            f"📆 За 7 дней: {week}\n\n"
            f"💕 Мэтчей (взаимных): {matches}\n"
            f"📈 Конверсия в мэтч: {conversion}%",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ========== СТАРЫЕ ОБРАБОТЧИКИ (регистрации) ==========
    elif data == "stats_retention":
        # Старый retention — перенаправляем на новый
        keyboard = [
            [InlineKeyboardButton("D1 (вчера)", callback_data="stats_ret_1")],
            [InlineKeyboardButton("D7 (неделя)", callback_data="stats_ret_7")],
            [InlineKeyboardButton("D30 (месяц)", callback_data="stats_ret_30")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_stats_menu")],
        ]
        await query.message.reply_text(
            "📈 Retention — % пользователей, вернувшихся после регистрации:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "stats_likes":
        async with db_pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM likes")
        await query.message.reply_text(f"❤️ Общее количество лайков: {count}")

    elif data == "stats_proxies":
        # Исправлено — теперь считаем user_chats
        async with db_pool.acquire() as conn:
            count = await conn.fetchval("""
                SELECT COUNT(DISTINCT LEAST(user_id, partner_id)::text || '_' || GREATEST(user_id, partner_id)::text)
                FROM user_chats
            """) or 0
        await query.message.reply_text(f"🔗 Всего чатов (уникальных пар): {count}")

    elif data == "stats_start":
        async with db_pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM registration_times")
        await query.message.reply_text(f"👤 Пользователи, нажавшие /start: {count}")

    elif data == "stats_registered":
        async with db_pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM registration_times WHERE finish_time IS NOT NULL"
            )
        await query.message.reply_text(f"✅ Пользователи, завершившие регистрацию: {count}")

    elif data == "stats_avg_time":
        async with db_pool.acquire() as conn:
            avg_seconds = await conn.fetchval("""
                SELECT AVG(EXTRACT(EPOCH FROM finish_time) - EXTRACT(EPOCH FROM start_time))
                FROM registration_times
                WHERE finish_time IS NOT NULL
                  AND (EXTRACT(EPOCH FROM finish_time) - EXTRACT(EPOCH FROM start_time)) < 420
            """)
        if avg_seconds:
            minutes = round(avg_seconds / 60, 2)
            await query.message.reply_text(f"⏱ Среднее время регистрации (до 7 мин): {minutes} мин.")
        else:
            await query.message.reply_text("⚠️ Недостаточно данных.")

    elif data.startswith("stats_retention_"):
        # Старый формат — перенаправляем на новый
        days = int(data.split("_")[-1])
        # Эмулируем новый формат
        query.data = f"stats_ret_{days}"
        await handle_stats_selection(update, context)

def get_muted_chats_keyboard(user_id: int, page: int = 0, lang: str = "ru", all_muted: list = None, max_page: int = 0):
    """Генерирует клавиатуру для пагинации 'Мьютированные пользователи' (5 на странице)"""
    if not all_muted:
        return InlineKeyboardMarkup([])

    buttons = []
    for muted in all_muted:
        muted_user_id = muted['muted_user_id']
        name_display = muted.get('name_display', 'User')

        buttons.append([
            InlineKeyboardButton(name_display, callback_data=f"profile_{muted_user_id}"),
            InlineKeyboardButton("🔊", callback_data=f"unmute_{muted_user_id}")
        ])

    # Навигация (◀️ ▶️)
    nav_buttons = []
    if page < max_page:  # Есть ещё страницы вперёд
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"muted_chats_page_nav_{page+1}"))
    if page > 0:  # Есть предыдущие страницы
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"muted_chats_page_nav_{page-1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)


async def show_muted_chats_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_first: bool = False):
    """Показывает страницу 'Мьютированные пользователи' с пагинацией"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    async with db_pool.acquire() as conn:
        # Получаем всех мьютированных пользователей
        all_muted = await conn.fetch("""
            SELECT muted_user_id FROM muted_users WHERE user_id = $1
            ORDER BY muted_user_id DESC
        """, user_id)

        if not all_muted:
            if is_first:
                await update.message.reply_text(TEXT2[lang]["mute_list_empty"])
            else:
                # Если список опустел - показываем пустое меню
                await update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
            return

        # Подготовляем данные с именами
        all_muted_with_data = []
        for muted_row in all_muted:
            muted_user_id = muted_row['muted_user_id']
            user_row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", muted_user_id)
            name = user_row['name'] if user_row and user_row['name'] else TEXT2[lang]["default_user"]

            all_muted_with_data.append(dict(
                muted_row,
                name_display=name
            ))

    # Вычисляем максимальный номер страницы
    max_page = (len(all_muted_with_data) - 1) // LIKES_PROFILES_PER_PAGE
    page = max(0, min(page, max_page))

    # Сохраняем текущую страницу в контексте
    context.user_data["muted_chats_page"] = page

    keyboard = get_muted_chats_keyboard(user_id, page, lang, all_muted_with_data, max_page)

    # Проверяем, нужно ли обновить текст (возвращение из меню размьючивания)
    update_text = context.user_data.get("_restore_muted_chats", False)

    if is_first:
        # Первый показ - отправляем новое сообщение
        await update.message.reply_text(
            TEXT2[lang]["mute_list_title"],
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # Пагинация - обновляем существующее меню
        if update_text:
            # Возвращение из меню размьючивания - обновляем и текст и клавиатуру
            try:
                await update.callback_query.message.edit_text(
                    TEXT2[lang]["mute_list_title"],
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except BadRequest:
                pass  # Query expired - ignore
            # Очищаем флаг
            context.user_data["_restore_muted_chats"] = False
        else:
            # Простая пагинация - обновляем только клавиатуру
            try:
                await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)
            except BadRequest:
                pass  # Query expired - ignore


async def handle_mute_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список мьютированных пользователей с пагинацией"""
    await show_muted_chats_page(update, context, page=0, is_first=True)


async def handle_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    muted_user_id = int(query.data.replace("unmute_", ""))

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM muted_users WHERE user_id = $1 AND muted_user_id = $2
            """, user_id, muted_user_id)

    # Отправляем отбивку с сообщением об успехе
    await query.answer(TEXT2[lang]["mute_unmuted"])

    # Обновляем меню - пересчитываем список мьютированных пользователей с пагинацией
    page = context.user_data.get("muted_chats_page", 0)
    # Устанавливаем флаг для обновления текста меню
    context.user_data["_restore_muted_chats"] = True
    await show_muted_chats_page(update, context, page=page, is_first=False)


async def handle_mute_from_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    muted_user_id = int(query.data.replace("mute_from_request_", ""))

    async with db_pool.acquire() as conn:
        # Сохраняем mute в базу
        await conn.execute("""
            INSERT INTO muted_users (user_id, muted_user_id) VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """, user_id, muted_user_id)

        # Чистим активные запросы и чаты
        await conn.execute("""
            DELETE FROM chat_requests_log
            WHERE from_user_id = $1 AND to_user_id = $2 AND status = 'pending'
        """, muted_user_id, user_id)
        await conn.execute("""
            DELETE FROM proxy_chats
            WHERE (user1_id = $1 AND user2_id = $2) OR (user1_id = $2 AND user2_id = $1)
        """, user_id, muted_user_id)

    # Отправляем отбивку с сообщением об успехе
    await query.answer(TEXT2[lang]["mute_user_muted"])

    # Обновляем меню - пересчитываем список чатов с пагинацией
    # Сохраняем текущую страницу из context если была
    page = context.user_data.get("active_chats_page", 0)
    await show_active_chats_page(update, context, page=page, is_first=False)


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Главное меню
    if text == TEXTS[lang]["menu_form"]:
        await handle_menu(update, context)
        return
    if text == TEXTS[lang]["menu_search"]:
        await handle_menu(update, context)
        return
    if text == TEXTS[lang]["menu_likes"]:
        await handle_menu(update, context)
        return
    if text == TEXTS[lang]["menu_chats"]:
        await handle_menu(update, context)
        return
    if text == TEXTS[lang]["menu_chalk"]:
        await handle_menu(update, context)
        return
    if text == TEXTS[lang]["menu_about"]:
        await handle_menu(update, context)
        return

    # Остальные действия
    # Открыть выбор статуса
    if text == TEXT2[lang]["profile_status_btn"]:
        opts = TEXT2[lang]["status_options"]
        buttons = [[InlineKeyboardButton(label, callback_data=f"set_status:{slug}")]
                   for slug, label in opts]
        await update.message.reply_text(
            TEXT2[lang]["choose_status"],
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return


    if text == TEXTS[lang]["search_next_person"]:
        # 🌍 Проверяем режим глобального поиска
        if context.user_data.get("global_search_mode"):
            await show_global_search_result(update, context)
        else:
            await show_next_search_result(update, context)
        return

    if text == TEXTS[lang]["chats_back"]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["menu_home"]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["likes_back"]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["form_back"]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["chalk_back"]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["about_back"]:
        await handle_menu(update, context)
        return

    if text == TEXTS[lang]["offline_back"]:
        menu = [
            [KeyboardButton(TEXTS[lang]["chats_active"])],
            [KeyboardButton(TEXTS[lang]["offline_muted"])],
            [KeyboardButton(TEXTS[lang]["chats_back"])]
        ]
        markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)
        await update.message.reply_text(TEXT2[lang]["menu_chats_title"], reply_markup=markup)
        return


    if text in [TEXTS[lang]["search_back"], TEXTS[lang]["menu_home"]]:
        await handle_back_to_main(update, context)
        return

    if text == TEXTS[lang]["offline_archive"]:
        await handle_chat_archive(update, context)
        return

    if text == TEXTS[lang]["search_find"]:
        await handle_search_command(update, context)
        return

    if text == TEXTS[lang]["search_filters"]:
        await handle_filters(update, context)
        return

    if text == TEXTS[lang]["search_hidden"]:
        await handle_hidden_users(update, context)
        return

    if text.startswith(TEXTS[lang]["likes_sent"]):
        await handle_my_likes(update, context)
        return

    if text == TEXTS[lang]["chalk_get"]:
        await handle_get_magnesia(update, context)
        return

    # Подменю "Получить магнезию"
    if text == TEXTS[lang]["chalk_get_referral"]:
        await handle_chalk_get_referral(update, context)
        return

    if text == TEXTS[lang]["chalk_get_board"]:
        await handle_chalk_get_board(update, context)
        return

    if text == TEXTS[lang]["chalk_get_stars"]:
        await handle_chalk_get_stars(update, context)
        return

    if text == TEXTS[lang]["chalk_get_founder"]:
        await handle_chalk_get_founder(update, context)
        return

    if text == TEXTS[lang]["chalk_get_back"]:
        # Возврат в меню "Магнезия"
        keyboard = [[
            KeyboardButton(TEXTS[lang]["chalk_get"]),
            KeyboardButton(TEXTS[lang]["chalk_use"])
        ], [KeyboardButton(TEXTS[lang]["chalk_amount"]), KeyboardButton(TEXTS[lang]["chalk_status"])],
                    [KeyboardButton(TEXTS[lang]["chalk_back"])]]
        await update.message.reply_text(TEXT2[lang]["menu_chalk_title_hi"],
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard, resize_keyboard=True))
        return

    if text == TEXTS[lang]["offline_muted"]:
        await handle_mute_menu(update, context)
        return

    if text.startswith(TEXTS[lang]["likes_mutual"]):
        await handle_mutual_likes(update, context)
        return

    if text.startswith(TEXTS[lang]["likes_received"]):
        await handle_liked_me(update, context)
        return


    if text == TEXTS[lang]["chats_active"]:
        await handle_active_chats(update, context)
        return

    # Магнезия - Использовать (новые тарифы)
    if text == TEXTS[lang]["chalk_use"]:
        buttons = [
            [InlineKeyboardButton(TEXTS[lang]["boost_buy_14_btn"], callback_data="boost_buy_14")],
            [InlineKeyboardButton(TEXTS[lang]["boost_buy_182_btn"], callback_data="boost_buy_182")],
            [InlineKeyboardButton(TEXTS[lang]["boost_buy_365_btn"], callback_data="boost_buy_365")]
        ]
        await update.message.reply_text(
            TEXT2[lang]["menu_chalk_title"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Статус Boost (перенесён в основное меню)
    if text == TEXTS[lang]["chalk_status"]:
        await handle_boost_status_button(update, context)
        return

    if text == TEXTS[lang]["chalk_amount"]:
        balance = await get_magnesium(user_id)
        await update.message.reply_text(
            TEXT2[lang]["chalk_balance"].format(balance=balance))
        return

    # 🤝 Встречи (новое меню)
    if text == TEXTS[lang]["menu_board"]:
        await handle_meetups_menu(update, context)
        return

    if text == TEXTS[lang]["board_my"]:
        await handle_board_my(update, context)
        return

    if text == TEXTS[lang]["board_create"]:
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        buttons = [[
            InlineKeyboardButton(TEXT2[lang]["board_date_today"].format(
                date=today.strftime("%d.%m (%a)")), callback_data="board_date_today")
        ], [
            InlineKeyboardButton(TEXT2[lang]["board_date_tomorrow"].format(
                date=tomorrow.strftime("%d.%m (%a)")), callback_data="board_date_tomorrow")
        ], [
            InlineKeyboardButton(TEXT2[lang]["board_date_custom"],
                                 callback_data="board_date_custom")
        ]]

        context.user_data["board"] = {}
        context.user_data["awaiting_board_date"] = True

        await update.message.reply_text(TEXT2[lang]["board_create_intro"],
                                        reply_markup=InlineKeyboardMarkup(buttons))
        return

    if text == TEXTS[lang]["board_city"]:
        await handle_meetups_menu(update, context)
        return

    # Cragsy / About
    if text == TEXTS[lang]["about_home"]:
        await start(update, context)
        return

    if text == TEXTS[lang]["about_rules"]:
        await show_user_agreement(update, context, show_inline_button=False)
        return

    if text == TEXTS[lang]["about_feedback"]:
        context.user_data["awaiting_feedback"] = True
        await update.message.reply_text(TEXT2[lang]["feedback_intro"])
        return

    if text in [TEXTS[lang]["form_edit"], TEXTS[lang]["form_delete"]]:
        await handle_text_message(update, context)
        return


    if DEBUG_MODE:
        print(f"[DEBUG] Неизвестная кнопка: {text}")


async def dump_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    try:
        cursor.execute("SELECT user_id FROM users")


        if not rows:
            await update.message.reply_text("🗃️ В базе пока нет пользователей.")
            return

        user_list = "\n".join([str(row[0]) for row in rows])
        await update.message.reply_text(f"👥 Пользователи:\n{user_list}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при доступе к базе: {e}")



###################### Изменение Анкеты ######################

async def show_profile_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    message = update.message if update.message else update.callback_query.message

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if not row:
            await message.reply_text(TEXT2[lang]["profile_not_found"])
            return

        data = dict(row)

        # --- те же расчёты, что и в edit_profile_menu ---

        difficulty_raw = DIFFICULTY_LABELS.get(
            data.get("difficulty"),
            data.get("difficulty") or TEXT2[lang]["not_specified"]
        )
        difficulty_display = escape_markdown(difficulty_raw)

        climb_type_raw = get_climb_label(data.get("climb_type", ""), lang) if data.get("climb_type") else TEXT2[lang]["not_specified"]
        climb_type_display = escape_markdown(climb_type_raw)

        gender_raw = get_gender_label(data.get("gender", ""), lang) if data.get("gender") else TEXT2[lang]["not_specified"]
        gender_display = escape_markdown(gender_raw)

        weight_raw = get_weight_label(data.get("weight", ""), lang) if data.get("weight") else TEXT2[lang]["not_specified"]
        weight_display = escape_markdown(weight_raw)

        country_display = escape_markdown(data.get("country") or "—")
        city_value = data.get("city_other") if data.get("city") == "Другой" else data.get("city", "—")
        city_display = escape_markdown(city_value) if city_value else TEXT2[lang]["not_specified"]

        likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", user_id)
        likes_count = likes_count or 0  # Fallback на 0 если NULL
        likes_display_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
        likes_display = escape_markdown(likes_display_raw)

    status_slug = data.get("status_slug")

    def render_status_line_local(lang: str, slug: str | None) -> str:
        if not slug:
            return ""
        opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
        raw = opts_map.get(slug, "")
        return f"*{escape_markdown(raw)}*" if raw else ""

    name_raw = data.get('name', '—')
    name_with_boost = await add_boost_emoji_to_name(name_raw, user_id)

    caption_lines = [
        f"{TEXT2[lang]['profile_user']}: *{escape_markdown(name_with_boost)}*",
        f"{TEXT2[lang]['field_type']}: {climb_type_display} I {difficulty_display}",
        f"{TEXT2[lang]['field_country']}: {country_display}",
        f"{TEXT2[lang]['field_city']}: {city_display or TEXT2[lang]['not_specified']}",
        f"{TEXT2[lang]['field_gender']}: {gender_display}",
        f"{TEXT2[lang]['field_weight']}: {weight_display}\n",
        render_status_line_local(lang, status_slug),
        f"❤️ {likes_display}"
    ]
    caption_lines = [line for line in caption_lines if line]
    if data.get("bio"):
        caption_lines.append(f"📝 {escape_markdown(data['bio'])}")

    caption = "\n".join(caption_lines)

    # 🔽 Меню анкеты как ReplyKeyboard
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(TEXTS[lang]["form_edit"])],
        [KeyboardButton(TEXTS[lang]["form_delete"])],
        [KeyboardButton(TEXTS[lang]["form_back"])]
    ], resize_keyboard=True)

    try:
        if data.get("photo_bytes"):
            image_io = BytesIO(data["photo_bytes"])
            image_io.name = "photo.jpg"
            image_io.seek(0)

            await message.reply_photo(
                photo=image_io,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                protect_content=True,
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=keyboard
            )
    except Exception as e:
        print("⚠️ Ошибка при отправке анкеты (preview):", e)
        await message.reply_text(
            caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard
        )


async def safe_edit_or_reply(message, text, reply_markup=None, lang="ru"):
    """
    ✅ Редактирует сообщение, сохраняя фото если оно есть
    Если фото - редактирует подпись, если текст - редактирует текст
    """
    try:
        if message.photo:
            # Если фото - редактируем подпись (caption) БЕЗ parse_mode (фото требует другого подхода)
            await message.edit_caption(
                caption=text,
                reply_markup=reply_markup
            )
        else:
            # Если текст - редактируем текст
            await message.edit_text(text, reply_markup=reply_markup)
    except Exception as e:
        # На случай ошибок - просто отправляем новое
        try:
            await message.reply_text(text, reply_markup=reply_markup)
        except Exception as e2:
            print(f"⚠️ Ошибка при safe_edit_or_reply: {e} / {e2}")

async def send_profile_menu(message, user_id, context):
    """✅ Отправляет профиль-меню с фото и 9 кнопками"""
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if not row:
            return

        data = dict(row)

        # Экранируем для MARKDOWN_V2
        difficulty_raw = DIFFICULTY_LABELS.get(
            data.get("difficulty"),
            data.get("difficulty") or TEXT2[lang]["not_specified"]
        )
        difficulty_display = escape_markdown(difficulty_raw)

        climb_type_raw = get_climb_label(data.get("climb_type", ""), lang) if data.get("climb_type") else TEXT2[lang]["not_specified"]
        climb_type_display = escape_markdown(climb_type_raw)

        gender_raw = get_gender_label(data.get("gender", ""), lang) if data.get("gender") else TEXT2[lang]["not_specified"]
        gender_display = escape_markdown(gender_raw)

        weight_raw = get_weight_label(data.get("weight", ""), lang) if data.get("weight") else TEXT2[lang]["not_specified"]
        weight_display = escape_markdown(weight_raw)

        country_display = escape_markdown(data.get("country") or "—")
        city_value = data.get("city_other") if data.get("city") == "Другой" else data.get("city", "—")
        city_display = escape_markdown(city_value) if city_value else TEXT2[lang]["not_specified"]

        likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", user_id)
        likes_count = likes_count or 0
        likes_display_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
        likes_display = escape_markdown(likes_display_raw)

    status_slug = data.get("status_slug")

    def render_status_line_local(lang: str, slug: str | None) -> str:
        if not slug:
            return ""
        opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
        raw = opts_map.get(slug, "")
        return f"*{escape_markdown(raw)}*" if raw else ""

    name_raw = data.get('name', '—')
    name_with_boost = await add_boost_emoji_to_name(name_raw, user_id)

    caption_lines = [
        f"{TEXT2[lang]['profile_user']}: *{escape_markdown(name_with_boost)}*",
        f"{TEXT2[lang]['field_type']}: {climb_type_display} I {difficulty_display}",
        f"{TEXT2[lang]['field_country']}: {country_display}",
        f"{TEXT2[lang]['field_city']}: {city_display or TEXT2[lang]['not_specified']}",
        f"{TEXT2[lang]['field_gender']}: {gender_display}",
        f"{TEXT2[lang]['field_weight']}: {weight_display}\n",
        render_status_line_local(lang, status_slug),
        f"❤️ {likes_display}"
    ]

    caption_lines = [line for line in caption_lines if line]
    if data.get("bio"):
        caption_lines.append(f"📝 {escape_markdown(data['bio'])}")

    caption = "\n".join(caption_lines)

    buttons = [
        [
            InlineKeyboardButton(f"👤 {TEXT2[lang]['profile_myname']}", callback_data="edit_name"),
            InlineKeyboardButton(f"🌍 {TEXT2[lang]['field_location']}", callback_data="edit_location"),
            InlineKeyboardButton(f"🏷️ {TEXT2[lang]['profile_status_btn']}", callback_data="edit_status")
        ],
        [
            InlineKeyboardButton(f"🧗 {TEXT2[lang]['field_level']}", callback_data="edit_level"),
            InlineKeyboardButton(f"🏔️ {TEXT2[lang]['filter_type']}", callback_data="edit_climb_type"),
            InlineKeyboardButton(f"🚻 {TEXT2[lang]['field_gender']}", callback_data="edit_gender")
        ],
        [
            InlineKeyboardButton(f"⚖️ {TEXT2[lang]['field_weight']}", callback_data="edit_weight"),
            InlineKeyboardButton(f"🖼 {TEXT2[lang]['field_photo']}", callback_data="edit_photo"),
            InlineKeyboardButton(f"📝 {TEXT2[lang]['field_about']}", callback_data="edit_about")
        ]
    ]

    try:
        if data.get("photo_bytes"):
            image_io = BytesIO(data["photo_bytes"])
            image_io.name = "photo.jpg"
            image_io.seek(0)
            await message.reply_photo(
                photo=image_io,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(buttons),
                protect_content=True
            )
        else:
            await message.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        print(f"⚠️ Ошибка при отправке профиля: {e}")

async def edit_profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, force_new: bool = False):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    message = update.message if update.message else update.callback_query.message

    # ✅ Для плавных переходов через edit_text()
    if update.callback_query:
        message = update.callback_query.message

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if not row:
            await message.reply_text(TEXT2[lang]["profile_not_found"])
            return

        data = dict(row)

        # --- ЭКРАНИРУЕМ ВСЁ, что уходит в MARKDOWN_V2 ---
        # Уровень: поддерживаем старые коды ('beginner'/'advanced'/'pro') и новые грейды ('6B+'), затем экранируем
        difficulty_raw = DIFFICULTY_LABELS.get(
            data.get("difficulty"),
            data.get("difficulty") or TEXT2[lang]["not_specified"]
        )
        difficulty_display = escape_markdown(difficulty_raw)

        # Тип / Пол / Вес: берём лейблы и экранируем
        climb_type_raw = get_climb_label(data.get("climb_type", ""), lang) if data.get("climb_type") else TEXT2[lang]["not_specified"]
        climb_type_display = escape_markdown(climb_type_raw)

        gender_raw = get_gender_label(data.get("gender", ""), lang) if data.get("gender") else TEXT2[lang]["not_specified"]
        gender_display = escape_markdown(gender_raw)

        weight_raw = get_weight_label(data.get("weight", ""), lang) if data.get("weight") else TEXT2[lang]["not_specified"]
        weight_display = escape_markdown(weight_raw)

        # Страна / Город
        country_display = escape_markdown(data.get("country") or "—")
        city_value = data.get("city_other") if data.get("city") == "Другой" else data.get("city", "—")
        city_display = escape_markdown(city_value) if city_value else TEXT2[lang]["not_specified"]

        # Лайки: формируем строку и экранируем (важно для "K+" / "M+")
        likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", user_id)
        likes_count = likes_count or 0  # Fallback на 0 если NULL
        likes_display_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
        likes_display = escape_markdown(likes_display_raw)

    # достаём статус из БД
    status_slug = data.get("status_slug")

    # готовим строку статуса (если нет — пустая строка)
    def render_status_line_local(lang: str, slug: str | None) -> str:
        if not slug:
            return ""
        opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
        raw = opts_map.get(slug, "")
        return f"*{escape_markdown(raw)}*" if raw else ""   # жирный + перенос строки

    name_raw = data.get('name', '—')
    name_with_boost = await add_boost_emoji_to_name(name_raw, user_id)

    caption_lines = [
        f"{TEXT2[lang]['profile_user']}: *{escape_markdown(name_with_boost)}*",
        f"{TEXT2[lang]['field_type']}: {climb_type_display} I {difficulty_display}",
        f"{TEXT2[lang]['field_country']}: {country_display}",
        f"{TEXT2[lang]['field_city']}: {city_display or TEXT2[lang]['not_specified']}",
        f"{TEXT2[lang]['field_gender']}: {gender_display}",
        f"{TEXT2[lang]['field_weight']}: {weight_display}\n",
        render_status_line_local(lang, status_slug), # ← ✅ новая строка под именем
        f"❤️ {likes_display}"
    ]

    caption_lines = [line for line in caption_lines if line]  # убираем пустые
    if data.get("bio"):
        caption_lines.append(f"📝 {escape_markdown(data['bio'])}")


    caption = "\n".join(caption_lines)

    buttons = [
        [
            InlineKeyboardButton(f"👤 {TEXT2[lang]['profile_myname']}", callback_data="edit_name"),
            InlineKeyboardButton(f"🌍 {TEXT2[lang]['field_location']}", callback_data="edit_location"),
            InlineKeyboardButton(f"🏷️ {TEXT2[lang]['profile_status_btn']}", callback_data="edit_status")
        ],
        [
            InlineKeyboardButton(f"🧗 {TEXT2[lang]['field_level']}", callback_data="edit_level"),
            InlineKeyboardButton(f"🏔️ {TEXT2[lang]['filter_type']}", callback_data="edit_climb_type"),
            InlineKeyboardButton(f"🚻 {TEXT2[lang]['field_gender']}", callback_data="edit_gender")
        ],
        [
            InlineKeyboardButton(f"⚖️ {TEXT2[lang]['field_weight']}", callback_data="edit_weight"),
            InlineKeyboardButton(f"🖼 {TEXT2[lang]['field_photo']}", callback_data="edit_photo"),
            InlineKeyboardButton(f"📝 {TEXT2[lang]['field_about']}", callback_data="edit_about")
        ]
    ]


    try:
        # ✅ Используем edit_text для плавных переходов или reply для первого открытия
        if force_new or not hasattr(message, 'edit_text'):
            # Первое открытие - отправляем новое сообщение
            if data.get("photo_bytes"):
                image_io = BytesIO(data["photo_bytes"])
                image_io.name = "photo.jpg"
                image_io.seek(0)

                await message.reply_photo(
                    photo=image_io,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    protect_content=True
                )
            else:
                await message.reply_text(
                    caption,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        else:
            # Плавный переход - редактируем существующее (только текстовые сообщения)
            try:
                await message.edit_text(
                    caption,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except Exception as edit_err:
                # Если не можем отредактировать, отправляем новое
                if data.get("photo_bytes"):
                    image_io = BytesIO(data["photo_bytes"])
                    image_io.name = "photo.jpg"
                    image_io.seek(0)
                    await message.reply_photo(
                        photo=image_io,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        protect_content=True
                    )
                else:
                    await message.reply_text(
                        caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
    except Exception as e:
        print("⚠️ Ошибка при отправке меню профиля:", e)
        await message.reply_text(
            caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def handle_edit_name_text(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data["lang"]
    text = update.message.text.strip()

    error = validate_text(text, lang=lang, max_length=30)
    if error:
        await update.message.reply_text(error)
        return

    if contains_emoji(text):
        await update.message.reply_text(TEXT2[lang]["err_emoji_in_name"])
        return

    # ✅ Сохраняем имя в БД
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET name = $1 WHERE user_id = $2", text, user_id)

    # ✅ Отправляем отбивку И форсируем меню профиля
    await update.message.reply_text(TEXT2[lang].get("saved"))

    from types import SimpleNamespace
    fake_update = SimpleNamespace(effective_user=update.effective_user, message=update.message, callback_query=None)
    await edit_profile_menu(fake_update, context, force_new=True)


async def handle_edit_name_button(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    set_state(context, "awaiting_name2")
    await safe_edit_or_reply(query.message, TEXT2[lang]["ask_name_again"], lang=lang)


async def edit_level_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    await safe_edit_or_reply(
        query.message,
        TEXT2[lang]["ask_difficulty_again"],
        reply_markup=get_difficulty_keyboard(page=1, lang=lang, prefix="editdiffval_"),
        lang=lang
    )

async def edit_level_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    raw = query.data.replace("editdiffval_", "")

    # Перелистывание - отбивка без текста
    if raw.startswith("page_"):
        await query.answer()
        page = int(raw.split("_")[1])
        await query.message.edit_reply_markup(
            reply_markup=get_difficulty_keyboard(page=page, lang=lang, prefix="editdiffval_")
        )
        return

    # Пропуск или выбор - отбивка с текстом
    await query.answer(TEXT2[lang].get("saved"))
    new_value = None if raw == "skip" else raw

    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET difficulty = $1 WHERE user_id = $2", new_value, user_id)

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def edit_gender_prompt(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    question = TEXT2[lang]["ask_gender_again"]

    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_male"],
                             callback_data="editgender_male"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_female"],
                             callback_data="editgender_female")
    ], [
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_skip"],
                             callback_data="editgender_other")
    ]]

    await safe_edit_or_reply(query.message, question,
                             reply_markup=InlineKeyboardMarkup(keyboard), lang=lang)


async def edit_gender_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(TEXT2[context.user_data.get("lang", "ru")].get("saved", "✓ Сохранено"))
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    gender = query.data.replace("editgender_", "")  # male / female / other

    # Обновляем БД
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET gender = $1 WHERE user_id = $2", gender, user_id)

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def edit_climb_type_prompt(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    question = TEXT2[lang]["ask_climb_type_again"]

    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"],
                             callback_data="edittype_difficulty"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"],
                             callback_data="edittype_bouldering")
    ],
                [
                    InlineKeyboardButton(
                        INLINE_TEXTS[lang]["btn_search_type_any"],
                        callback_data="edittype_both")
                ]]

    await safe_edit_or_reply(query.message, question,
                             reply_markup=InlineKeyboardMarkup(keyboard), lang=lang)


async def edit_climb_type_save(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(TEXT2[context.user_data.get("lang", "ru")].get("saved", "✓ Сохранено"))
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    climb_type = query.data.replace("edittype_",
                                    "")  # difficulty / bouldering / both

    # Обновляем БД
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET climb_type = $1 WHERE user_id = $2", climb_type, user_id)

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def edit_weight_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    question = TEXT2[lang]["ask_weight_again"]

    await safe_edit_or_reply(
        query.message,
        question,
        reply_markup=get_weight_keyboard(page=2, lang=lang, prefix="editweight_"),
        lang=lang
    )

async def edit_weight_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    weight_raw = query.data.replace("editweight_", "")

    # 👉 Обработка переключения страниц - отбивка без текста
    if weight_raw.startswith("page_"):
        await query.answer()
        page = int(weight_raw.split("_")[1])
        await query.message.edit_reply_markup(
            reply_markup=get_weight_keyboard(page=page, lang=lang, prefix="editweight_")
        )
        return

    # 👉 Пропуск или выбор - отбивка с текстом
    await query.answer(TEXT2[lang].get("saved"))
    weight = None if weight_raw == "skip" else weight_raw

    # Обновляем БД
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET weight = $1 WHERE user_id = $2",
                           weight, user_id)

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def edit_photo_prompt(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    context.user_data["awaiting_edit_photo"] = True

    question = TEXT2[lang]["ask_photo_again"]

    keyboard = [[
        InlineKeyboardButton("🗑 " + TEXT2[lang]["btn_photo_delete"],
                             callback_data="editphoto_delete"),
        InlineKeyboardButton("⏭ " + TEXT2[lang]["btn_skip"],
                             callback_data="editphoto_skip")
    ]]

    await safe_edit_or_reply(query.message, question,
                             reply_markup=InlineKeyboardMarkup(keyboard), lang=lang)


async def edit_photo_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(TEXT2[context.user_data.get("lang", "ru")].get("saved", "✓ Сохранено"))
    user_id = query.from_user.id
    lang = context.user_data.get("lang", "ru")

    # 🧠 Определяем пол из БД
    async with db_pool.acquire() as conn:
        result = await conn.fetchrow("SELECT gender FROM users WHERE user_id = $1", user_id)
    gender = result[0] if result else "other"

    # 🎯 Подставляем заглушку
    from random import choice
    selected_url = choice(PLACEHOLDER_URLS.get(gender, PLACEHOLDER_URLS["other"]))
    try:
        import requests
        response = requests.get(selected_url, timeout=3)
        if response.status_code == 200:
            async with db_pool.acquire() as conn:
                await conn.execute("UPDATE users SET photo_bytes = $1, has_real_photo = FALSE WHERE user_id = $2", response.content, user_id)
        else:
            print("⚠️ Не удалось загрузить заглушку. Статус:", response.status_code)
    except Exception as e:
        print("❌ Ошибка при загрузке заглушки:", e)

    context.user_data["awaiting_edit_photo"] = False

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def edit_photo_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(TEXT2[context.user_data.get("lang", "ru")].get("saved", "✓ Сохранено"))

    context.user_data["awaiting_edit_photo"] = False

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def unified_photo_handler(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    photo = update.message.photo[-1]

    try:
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()

        is_clean = check_image_for_harm_base64(image_bytes)
        if not is_clean:
            await update.message.reply_text(TEXT2[lang]["photo_blocked"])
            return

        # 🔁 Режим редактирования анкеты
        if context.user_data.get("awaiting_edit_photo", False):
            context.user_data["awaiting_edit_photo"] = False

            async with db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET photo_bytes = $1, has_real_photo = TRUE WHERE user_id = $2",
                    image_bytes, user_id)

            # ✅ Форсируем кнопки меню Профиль
            keyboard = [
                [KeyboardButton(TEXTS[lang]["form_edit"])],
                [KeyboardButton(TEXTS[lang]["form_delete"])],
                [KeyboardButton(TEXTS[lang]["form_back"])]
            ]

            # ✅ Отправляем отбивку И форсируем меню профиля
            await update.message.reply_text(TEXT2[lang].get("saved"), reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

            await edit_profile_menu(update, context)
            return

        # 🧾 Режим регистрации
        if context.user_data.get("awaiting_photo", False):
            user_sessions[user_id] = user_sessions.get(user_id, {})
            user_sessions[user_id]["photo_bytes"] = image_bytes
            await save_partial_profile(user_id)

            context.user_data["awaiting_photo"] = False
            await update.message.reply_text(TEXT2[lang]["photo_accepted"],
                                            reply_markup=get_progress_keyboard(7, lang))

            # ⏭ Переход к следующему шагу — выбор веса
            await update.message.reply_text(TEXT2[lang]["ask_weight"],
                reply_markup=get_weight_keyboard(page=2, lang=lang, prefix="weightval_"))

            return

        # ✅ РЕДАКТИРОВАНИЕ ПРОФИЛЯ - сохраняем фото
        if context.user_data.get("awaiting_edit_photo", False):
            reset_user_context(context)  # ⬅️ сбрасываем все registration-флаги
            return


    except Exception as e:
        print(f"❌ Ошибка при обработке фото: {e}")
        await update.message.reply_text(
            "⚠️ Не удалось обработать фото. Попробуй ещё раз.")


async def edit_bio_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Устанавливаем флаг ожидания текста
    context.user_data["awaiting_bio_again"] = True

    keyboard = [[
        InlineKeyboardButton("🗑 " + TEXT2[lang]["btn_photo_delete"],
                             callback_data="editbio_delete"),
        InlineKeyboardButton("⏭ " + TEXT2[lang]["btn_skip"],
                             callback_data="editbio_skip")
    ]]

    await safe_edit_or_reply(query.message, TEXT2[lang]["ask_bio_again"],
                             reply_markup=InlineKeyboardMarkup(keyboard), lang=lang)


async def edit_bio_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(TEXT2[context.user_data.get("lang", "ru")].get("saved", "✓ Сохранено"))
    user_id = query.from_user.id
    lang = context.user_data.get("lang", "ru")

    # Удаляем био из БД
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET bio = NULL WHERE user_id = $1", user_id)

    context.user_data["awaiting_bio_again"] = False

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)


async def edit_bio_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(TEXT2[context.user_data.get("lang", "ru")].get("saved", "✓ Сохранено"))

    context.user_data["awaiting_bio_again"] = False

    # ✅ Возвращаемся в меню профиля
    await edit_profile_menu(update, context)

async def handle_edit_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Редактирование локации профиля через Geoapify city search
    """
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Устанавливаем флаг редактирования локации
    set_state(context, "awaiting_edit_location_search")

    # ✅ Используем safe_edit_or_reply для плавного перехода
    await safe_edit_or_reply(query.message, TEXT2[lang]["ask_city_search"],
                             lang=lang)

############################ Подменю Объявления ###########################
async def handle_board_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = context.user_data.get("lang", "ru")

    if not context.user_data.get("awaiting_board_date"):
        return

    now = datetime.now()

    if query.data == "board_date_today":
        date_str = now.strftime("%Y-%m-%d")
    elif query.data == "board_date_tomorrow":
        date_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif query.data == "board_date_custom":
        context.user_data["awaiting_board_date"] = False
        context.user_data["awaiting_custom_board_date"] = True
        await query.message.reply_text(TEXTS[lang]["board_custom_date_prompt"])
        return
    else:
        await query.message.reply_text("⚠️ Неизвестный формат даты.")
        return

    # Проверяем, не участвует ли уже пользователь в тренировке на эту дату
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        async with db_pool.acquire() as conn:
            # Проверяем и кастомные (board_sessions), и дефолтные (gym_sessions) тренировки
            existing_board = await conn.fetchrow("""
                SELECT bs.id FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date = $2
            """, user_id, selected_date)

            existing_gym = await conn.fetchrow("""
                SELECT gs.id FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, selected_date)

            if existing_board or existing_gym:
                await query.message.reply_text(TEXT2[lang]["meetups_already_joined"])
                # НЕ сбрасываем awaiting_board_date, чтобы пользователь мог выбрать другую дату
                return
    except Exception as e:
        print(f"❌ Ошибка проверки дублирования даты: {e}")

    # Сохраняем дату и переключаемся на выбор времени
    context.user_data["board"]["date"] = date_str
    context.user_data["awaiting_board_date"] = False
    context.user_data["awaiting_board_time"] = True
    context.user_data["time_page"] = 0

    # 🕓 2. Следом — новое сообщение с выбором времени
    await show_time_page(update, context)

async def handle_board_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")

    if not context.user_data.get("awaiting_board_time"):
        return

    time_str = query.data.replace("board_time_", "")
    context.user_data["board"]["time"] = time_str
    context.user_data["awaiting_board_time"] = False

    # Переход к следующему шагу
    await ask_board_climb_type(update, context)

async def show_time_page(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    user_id = update_or_query.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")
    # Генерируем все варианты времени с 7:00 до 22:00
    time_slots = []
    for hour in range(7, 23):  # с 7:00 до 22:00 включительно
        time_slots.append(f"{hour:02d}:00")

    # Формируем кнопки в 4 столбца

    buttons = []
    row = []
    for i, time_str in enumerate(time_slots):
        row.append(InlineKeyboardButton(time_str, callback_data=f"board_time_{time_str}"))
        # Каждые 4 кнопки создаём новую строку
        if (i + 1) % 4 == 0:
            buttons.append(row)
            row = []

    # Добавляем последнюю строку, если есть оставшиеся кнопки
    if row:
        buttons.append(row)

    markup = InlineKeyboardMarkup(buttons)
    text = TEXT2[lang]["board_time_intro"]

    try:
        # Пагинация: редактируем сообщение
        callback = getattr(update_or_query, "callback_query", None)
        if callback and callback.data and callback.data.startswith("time_page_"):

            await update_or_query.callback_query.edit_message_text(
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            # Вывод нового сообщения
            await update_or_query.effective_message.reply_text(
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        print(f"⚠️ Ошибка show_time_page: {e}")



async def ask_board_climb_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    context.user_data["awaiting_board_climb_type"] = True

    keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"],
                             callback_data="board_climb_difficulty"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"],
                             callback_data="board_climb_bouldering")
    ]]

    await update.callback_query.message.reply_text(
        TEXTS[lang]["board_climb_type_intro"],
        reply_markup=InlineKeyboardMarkup(keyboard))

async def ask_board_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Шаг после выбора типа лазания: уровень для конкретного объявления."""
    lang = context.user_data.get("lang", "ru")
    context.user_data["awaiting_board_difficulty"] = True

    await update.callback_query.message.reply_text(
        TEXT2[lang]["board_difficulty_intro"],
        reply_markup=get_board_difficulty_keyboard(page=0, lang=lang, prefix="boarddiff_")
    )


async def handle_board_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора уровня в объявлении (с пагинацией)."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")

    if not context.user_data.get("awaiting_board_difficulty"):
        return

    raw = query.data.replace("boarddiff_", "")

    # Пагинация
    if raw.startswith("page_"):
        page = int(raw.split("_")[1])
        await query.message.edit_reply_markup(
            reply_markup=get_board_difficulty_keyboard(page=page, lang=lang, prefix="boarddiff_")
        )
        return

    # Выбор значения (теперь только конкретный грейд)
    context.user_data.setdefault("board", {})["difficulty"] = raw
    context.user_data["awaiting_board_difficulty"] = False

    # следующий шаг – выбор зала (пропускаем выбор пола партнёра)
    await ask_board_gym_selection(update, context)


async def handle_board_climb_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("awaiting_board_climb_type"):
        return

    climb_type = query.data.replace("board_climb_", "")
    context.user_data.setdefault("board", {})["climb_type"] = climb_type
    context.user_data["awaiting_board_climb_type"] = False

    # следующий шаг – выбор зала (убрали выбор уровня)
    await ask_board_gym_selection(update, context)


async def ask_board_gym_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Шаг выбора зала после выбора уровня сложности"""
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ru")
    context.user_data["awaiting_board_gym_selection"] = True

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city, city_other FROM users WHERE user_id = $1", user_id)
            if not row:
                await update.callback_query.message.reply_text(TEXT2[lang].get("profile_not_found", "⚠️ Профиль не найден"))
                return

            city = row['city_other'] if row['city'] == "Другой" else row['city']

            buttons = []

            # Определяем список залов в зависимости от города
            if city and ("Санкт-Петербург" in city or "Saint Petersburg" in city):
                # Питер - показываем залы парами
                for i in range(0, len(GYMS_SPB), 2):
                    row_btns = []
                    for gym in GYMS_SPB[i:i+2]:
                        gym_name = format_gym_name(gym)
                        row_btns.append(InlineKeyboardButton(gym_name, callback_data=f"board_gym_sel_{gym_name}"))
                    buttons.append(row_btns)
            elif city and ("Москва" in city or "Moscow" in city):
                # Москва - показываем залы парами
                for i in range(0, len(GYMS_MSK), 2):
                    row_btns = []
                    for gym in GYMS_MSK[i:i+2]:
                        gym_name = format_gym_name(gym)
                        # Пропускаем "Другая локация" из обычного списка
                        if gym_name != "Другая локация":
                            row_btns.append(InlineKeyboardButton(gym_name, callback_data=f"board_gym_sel_{gym_name}"))
                    if row_btns:
                        buttons.append(row_btns)

            # Добавляем кнопку "Другая локация" для всех городов
            buttons.append([InlineKeyboardButton(
                TEXT2[lang].get("board_gym_other", "📍 Другая локация"),
                callback_data="board_gym_sel_custom"
            )])

            await update.callback_query.message.reply_text(
                TEXT2[lang].get("board_gym_select", "🏢 Выбери зал для тренировки:"),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        print(f"⚠️ Ошибка ask_board_gym_selection: {e}")


async def handle_board_gym_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора зала"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")

    if not context.user_data.get("awaiting_board_gym_selection"):
        return

    if query.data == "board_gym_sel_custom":
        # Пользователь хочет ввести кастомную локацию
        context.user_data["awaiting_board_gym_selection"] = False
        context.user_data["awaiting_board_gym_custom"] = True
        await query.message.reply_text(TEXT2[lang].get("board_gym_custom_prompt", "📍 Введите название зала или локации:"))
        return

    # Извлекаем название зала
    gym_name = query.data.replace("board_gym_sel_", "")
    context.user_data["board"]["gym"] = gym_name
    context.user_data["awaiting_board_gym_selection"] = False

    # Показываем превью карточки
    await show_board_preview(update, context)


async def ask_board_partner_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DEPRECATED: Этот шаг больше не используется"""
    lang = context.user_data.get("lang", "ru")
    context.user_data["awaiting_board_partner_gender"] = True

    keyboard = [
        [
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_male"], callback_data="board_gender_male"),
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_female"], callback_data="board_gender_female")
        ],
        [
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_any"], callback_data="board_gender_any")
        ]
    ]

    await update.callback_query.message.reply_text(
        TEXT2[lang]["search_choose_gender"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_board_partner_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DEPRECATED: Этот шаг больше не используется"""
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("awaiting_board_partner_gender"):
        return

    gender_code = query.data.replace("board_gender_", "")
    context.user_data["board"]["partner_gender"] = gender_code
    context.user_data["awaiting_board_partner_gender"] = False

    # Переход к следующему шагу
    await ask_board_gym(update, context)


async def ask_board_gym(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    context.user_data["awaiting_board_gym"] = True

    await update.callback_query.message.reply_text(TEXTS[lang]["board_gym_intro"])


async def show_board_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает превью создаваемой board-тренировки в формате meetup-карточки"""
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id
    board = context.user_data.get("board", {})

    try:
        # Извлекаем данные
        date = board.get("date", "—")
        time = board.get("time", "—")
        gym = board.get("gym", "—")
        climb_type = board.get("climb_type", "both")

        # Форматируем дату
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            weekday_key = f"weekday_{date_obj.strftime('%a').lower()[:3]}"
            weekday = TEXT2[lang].get(weekday_key, "")
            date_formatted = date_obj.strftime("%d.%m")
        except ValueError:
            weekday = ""
            date_formatted = date
            print(f"⚠️ Неверный формат даты в show_board_preview: {date}")

        # Определяем тип тренировки
        if climb_type == "bouldering":
            type_label = TEXT2[lang]["meetups_card_bouldering"]
        elif climb_type == "difficulty":
            type_label = TEXT2[lang]["meetups_card_lead"]
        else:
            type_label = INLINE_TEXTS[lang]["btn_search_type_any"]

        # Формируем текст карточки в стиле meetup
        cards_text = f"🧗 {gym}\n\n"
        cards_text += f"{type_label} · {date_formatted} {weekday} · 🕖 {time}\n"
        cards_text += f"{TEXT2[lang].get('meetups_card_participants_preview', 'Уже идут')}: 1\n"

        # Кнопки
        buttons = [
            [
                InlineKeyboardButton(TEXTS[lang]["board_buttons_publish"], callback_data="board_publish"),
            ],
            [
                InlineKeyboardButton(TEXTS[lang]["board_buttons_edit"], callback_data="board_edit")
            ]
        ]

        # Используем дефолтное фото для bouldering
        photo_url = "https://i.postimg.cc/qN0BBrzV/bouldering.jpg"

        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo_url,
                caption=cards_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            print(f"❌ Ошибка отправки фото в show_board_preview: {e}")
            # Fallback на текстовое сообщение
            await update.effective_message.reply_text(
                cards_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        print(f"⚠️ Ошибка show_board_preview: {e}")
        import traceback
        traceback.print_exc()
        await update.effective_message.reply_text(TEXT2[lang].get("error_generic", "⚠️ Произошла ошибка. Попробуйте позже."))


async def handle_board_publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    try:
        async with db_pool.acquire() as conn:
            # Загружаем из контекста или из БД
            board = context.user_data.get("board", {})

            # Если context.user_data["board"] пуст — грузим из базы
            if not board or not all(k in board for k in ["date", "time", "climb_type", "gym"]):
                row = await conn.fetchrow("""
                    SELECT date, time, climb_type, difficulty, gym FROM board_posts
                    WHERE user_id = $1
                """, user_id)
                if not row:
                    await query.message.reply_text(TEXT2[lang].get("board_empty", "📭 У тебя пока нет активных объявлений."))
                    return

                board = {
                    "date": row['date'],
                    "time": row['time'],
                    "climb_type": row['climb_type'],
                    "difficulty": row['difficulty'],
                    "gym": row['gym']
                }

            # Определяем city_key по городу пользователя
            row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            city_key = None
            if row:
                city = row['city']
                if city and ("Петербург" in city or "Petersburg" in city):
                    city_key = "spb"
                elif city and ("Москва" in city or "Moscow" in city):
                    city_key = "msk"
                elif city:
                    # Для других городов используем сам город как city_key
                    city_key = city

            # Конвертируем строки в date/time объекты
            if isinstance(board["date"], str):
                session_date = datetime.strptime(board["date"], "%Y-%m-%d").date()
            else:
                session_date = board["date"]

            if isinstance(board["time"], str):
                session_time = datetime.strptime(board["time"], "%H:%M").time()
            else:
                session_time = board["time"]

            # Проверяем, не участвует ли пользователь уже в тренировке на этот день
            # Проверяем и кастомные (board_sessions), и дефолтные (gym_sessions) тренировки
            existing_board = await conn.fetchrow("""
                SELECT bs.id FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date = $2
            """, user_id, session_date)

            existing_gym = await conn.fetchrow("""
                SELECT gs.id FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, session_date)

            if existing_board or existing_gym:
                await query.message.reply_text(TEXT2[lang]["meetups_already_joined"])
                return

            # Создаём board_session
            session_id = await conn.fetchval("""
                INSERT INTO board_sessions
                (creator_id, gym_name, city_key, climb_type, session_date, session_time, is_custom, status)
                VALUES ($1, $2, $3, $4, $5, $6, TRUE, 'active')
                RETURNING id
            """, user_id, board["gym"], city_key, board["climb_type"], session_date, session_time)

            # Добавляем создателя как участника
            await conn.execute("""
                INSERT INTO board_session_participants (session_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            """, session_id, user_id)


            # 🎁 Магнезия за объявление — максимум 1 раз в неделю
            week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
            row = await conn.fetchrow("""
                SELECT 1 FROM board_magnesium_log
                WHERE user_id = $1 AND week_start = $2
            """, user_id, week_start)
            already_received = row is not None

            if not already_received:
                # Добавляем магнезию
                await conn.execute(
                    "INSERT INTO magnesium_balance (user_id, balance) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
                    user_id)
                await conn.execute(
                    "UPDATE magnesium_balance SET balance = balance + $1 WHERE user_id = $2",
                    2.5, user_id)
                await conn.execute(
                    "INSERT INTO magnesium_log (user_id, change, reason) VALUES ($1, $2, $3)",
                    user_id, 2.5, "Публикация объявления")

                # Логируем выдачу магнезии
                await conn.execute("""
                    INSERT INTO board_magnesium_log (user_id, week_start)
                    VALUES ($1, $2)
                """, user_id, week_start)

                # Получаем текущий баланс для уведомления
                balance_row = await conn.fetchrow("SELECT balance FROM magnesium_balance WHERE user_id = $1", user_id)
                current_balance = balance_row['balance'] if balance_row else 0

                await query.message.reply_text(
                    TEXT2[lang]["magnesium_board_gift"].format(balance=current_balance)
                )

            # 🚨 Пуш в город о новом объявлении (исключая автора)
            row = await conn.fetchrow("SELECT city, city_other FROM users WHERE user_id = $1", user_id)
            if row:
                city, city_other = row['city'], row['city_other']
                current_city = city_other if city == "Другой" else city
                await send_board_push_if_needed(context, current_city, exclude_user_id=user_id)

        # Отправляем уведомление об успешной публикации
        await query.message.reply_text(TEXTS[lang]["board_published"])

        # Перенаправляем пользователя к карточке созданной сессии
        gym_name = board["gym"]

        # Определяем, является ли gym_name известным залом
        known_gyms = set(g[0] for g in GYMS_SPB + GYMS_MSK)

        if gym_name in known_gyms:
            # Известный зал - показываем через стандартную механику
            context.user_data["meetup_selected_gym"] = gym_name
        else:
            # Кастомная локация - показываем через "other"
            context.user_data["meetup_selected_gym"] = "other"

        # Загружаем созданную сессию и показываем её карточку
        async with db_pool.acquire() as conn:
            # Находим только что созданную сессию
            created_session = await conn.fetchrow("""
                SELECT bs.id, bs.gym_name, bs.climb_type, bs.session_time, bs.session_date,
                       FALSE as is_default,
                       COUNT(bsp.user_id) AS participants_count,
                       'board' as session_type
                FROM board_sessions bs
                LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.id = $1
                GROUP BY bs.id
            """, session_id)

            if created_session:
                # Формируем страницу с одной сессией
                session_dict = dict(created_session)
                context.user_data["meetups_session_pages"] = [[session_dict]]
                context.user_data["meetups_session_index"] = 0
                context.user_data["meetup_gym_info"] = {}

                # Показываем карточку созданной сессии
                await show_session_card(update, context, 0, edit=False)
            else:
                # Fallback - показываем список залов
                await show_gym_list(update, context, edit=False)
                
    except Exception as e:
        print(f"⚠️ Ошибка handle_board_publish: {e}")
        await query.message.reply_text(TEXT2[lang].get("error_generic", "⚠️ Произошла ошибка. Попробуйте позже."))


async def handle_board_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = context.user_data.get("lang", "ru")

    try:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE board_posts SET status = 'removed', updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $1
            """, user_id)
        await query.message.reply_text(TEXTS[lang]["board_removed"])
    except Exception as e:
        print(f"⚠️ Ошибка handle_board_remove: {e}")
        await query.message.reply_text(TEXT2[lang].get("error_generic", "⚠️ Произошла ошибка. Попробуйте позже."))

async def handle_board_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Возвращаемся к шагу 1 — выбор даты
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    buttons = [[
        InlineKeyboardButton(TEXT2[lang]["board_date_today"].format(
            date=today.strftime("%d.%m (%a)")), callback_data="board_date_today")
    ], [
        InlineKeyboardButton(TEXT2[lang]["board_date_tomorrow"].format(
            date=tomorrow.strftime("%d.%m (%a)")), callback_data="board_date_tomorrow")
    ], [
        InlineKeyboardButton(TEXT2[lang]["board_date_custom"],
                             callback_data="board_date_custom")
    ]]

    context.user_data["board"] = {}
    context.user_data["awaiting_board_date"] = True

    await query.message.reply_text(f"{TEXT2[lang]['board_create_intro']}",
                                   reply_markup=InlineKeyboardMarkup(buttons))


async def handle_board_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safe message handling: support both message and callback_query
    message = None
    if update.message:
        message = update.message
    elif update.callback_query:
        message = update.callback_query.message

    if not message:
        return

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    try:
        async with db_pool.acquire() as conn:
            # Город пользователя
            row = await conn.fetchrow("SELECT city, city_other FROM users WHERE user_id = $1", user_id)
            if not row:
                await message.reply_text(TEXTS[lang]["board_city_empty"])
                return

            city, city_other = row['city'], row['city_other']
            current_city = city_other if city == "Другой" else city

            # Загружаем ВСЕ объявления по городу, отсортированные по времени
            posts = await conn.fetch("""
                SELECT bp.user_id, bp.date, bp.time, bp.climb_type, bp.difficulty, bp.gym, bp.status, bp.partner_gender
                FROM board_posts bp
                JOIN users u ON bp.user_id = u.user_id
                WHERE (u.city = $1 OR u.city_other = $2)
                  AND bp.user_id != $3
                  AND u.is_deleted = FALSE
                  AND (
                    (
                      bp.status = 'active'
                      AND (bp.date || ' ' || bp.time)::timestamp > NOW()
                    )
                    OR (
                      bp.status = 'removed'
                      AND bp.updated_at + INTERVAL '10 minutes' > NOW()
                    )
                  )
                ORDER BY (bp.date || ' ' || bp.time)::timestamp ASC
            """, current_city, current_city, user_id)

            if not posts:
                await message.reply_text(TEXTS[lang]["board_city_empty"])
                return

            # Сохраняем результаты в сессию
            context.user_data["board_city_results"] = posts
            context.user_data["board_city_page"] = 0

        await show_board_city_page(update, context)
    except Exception as e:
        print(f"⚠️ Ошибка handle_board_city: {e}")
        await message.reply_text(TEXT2[lang].get("error_generic", "⚠️ Произошла ошибка. Попробуйте позже."))

async def show_board_city_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(context, update.effective_user.id)
    lang = context.user_data["lang"]
    posts = context.user_data.get("board_city_results", [])
    page = context.user_data.get("board_city_page", 0)

    if not posts or page >= len(posts):
        await update.effective_message.reply_text(TEXT2[lang]["board_city_no_more"])
        return

    post = posts[page]
    uid, date, time, climb_type, difficulty_wish, gym, post_status, partner_gender = post['user_id'], post['date'], post['time'], post['climb_type'], post['difficulty'], post['gym'], post['status'], post['partner_gender']

    try:
        async with db_pool.acquire() as conn:
            # Данные пользователя (пропускаем удалённые профили)
            row = await conn.fetchrow("SELECT name, gender, weight, difficulty, photo_bytes, bio FROM users WHERE user_id = $1 AND is_deleted = FALSE", uid)
            if not row:
                context.user_data["board_city_page"] = page + 1
                await show_board_city_page(update, context)
                return

            name, gender, weight, profile_difficulty, photo_bytes, bio = row['name'], row['gender'], row['weight'], row['difficulty'], row['photo_bytes'], row['bio']

            if difficulty_wish:
                diff_display_md = display_difficulty_md(difficulty_wish, lang)
            else:
                diff_display_md = escape_markdown(TEXT2[lang]["board_difficulty_any"])

            weight_display_md = display_weight_md(weight, lang)
            likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", uid)
            likes_count = likes_count or 0  # Fallback на 0 если NULL
            likes_display = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
    except Exception as e:
        print(f"⚠️ Ошибка show_board_city_page DB: {e}")
        return

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        weekday_key = f"weekday_{date_obj.strftime('%a').lower()[:3]}"
        weekday = TEXT2[lang].get(weekday_key, "")
    except ValueError:
        weekday = ""
        print(f"⚠️ Неверный формат даты в show_board_city_page: {date}")
    bio_line = f"\n📝 {escape_markdown(bio)}" if bio else ""

    name_with_boost = await add_boost_emoji_to_name(name, uid)

    caption = (
        f"🤝 *{escape_markdown(TEXT2[lang]['board_intro_label'])}*\n"
        f"📌 {escape_markdown(date)} \\| {escape_markdown(weekday)} \\| {escape_markdown(time)}\n"
        f"{TEXT2[lang]['field_gym']}: *{escape_markdown(gym)}*\n\n"
        f"{TEXT2[lang]['field_type']}: *{escape_markdown(get_climb_label(climb_type, lang))}*\n"
        f"{TEXT2[lang]['board_field_level']}: *{diff_display_md}*\n\n"
        f"{TEXT2[lang]['profile_user']}: *{escape_markdown(name_with_boost)}*\n"
        f"{TEXT2[lang]['field_gender']}: {escape_markdown(get_gender_label(gender, lang))}\n"
        f"{TEXT2[lang]['field_weight']}: {weight_display_md}\n"
        f"❤️ {escape_markdown(likes_display)}{bio_line}"
    )

    # Кнопки
    status_icon = TEXTS[lang]["board_btn_status_active"] if post_status == "active" else TEXTS[lang]["board_btn_status_removed"]
    status_callback = "board_status_active" if post_status == "active" else "board_status_removed"

    buttons = [[
        InlineKeyboardButton(TEXTS[lang]["board_btn_write"], callback_data=f"open_chat_{uid}"),
        InlineKeyboardButton("🚫", callback_data=f"report_{uid}"),
        InlineKeyboardButton(status_icon, callback_data=status_callback)
    ]]
    markup = InlineKeyboardMarkup(buttons)

    target = update.callback_query.message if update.callback_query else update.message

    try:
        if photo_bytes:
            image = BytesIO(photo_bytes)
            image.name = "photo.jpg"
            image.seek(0)
            sent = await target.reply_photo(
                photo=image,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup,
                protect_content=True
            )
        else:
            sent = await target.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup
            )

        context.user_data["last_board_card_message_id"] = sent.message_id
        context.user_data["board_city_page"] = page + 1

    except Exception as e:
        print(f"❌ Ошибка отправки объявления с фото: {e}")

async def handle_board_city_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    await show_board_city_page(update, context)


async def handle_toggle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_id = int(query.data.replace("toggle_profile_", ""))
    lang = context.user_data.get("lang", "ru")

    key = f"profile_msg_id_{target_id}"
    msg_id = context.user_data.get(key)

    # Если уже показывали — удалить
    if msg_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
        except Exception as e:
            print(f"❌ Ошибка удаления сообщения профиля: {e}")
        context.user_data.pop(key, None)
        return

    try:
        async with db_pool.acquire() as conn:
            # Получаем профиль
            row = await conn.fetchrow("""
                SELECT name, photo_bytes, difficulty, climb_type, country, country_other, city, city_other, gender, weight, bio
                FROM users WHERE user_id = $1
            """, target_id)
            if not row:
                await query.message.reply_text(TEXTS[lang]["board_profile_not_found"])
                return

            name, photo_bytes, diff, climb, country, country_other, city, city_other, gender, weight, bio = row['name'], row['photo_bytes'], row['difficulty'], row['climb_type'], row['country'], row['country_other'], row['city'], row['city_other'], row['gender'], row['weight'], row['bio']

            # Отображения (MarkdownV2-safe)
            country_display = country_other if country == "🌍 Other" else country
            city_display = city_other if city == "Другой" else city

            name_md = escape_markdown(name or "—")
            climb_md = escape_markdown(get_climb_label(climb, lang) if climb else TEXT2[lang]["not_specified"])
            diff_md = display_difficulty_md(diff, lang)          # <- новый хелпер
            gender_md = escape_markdown(get_gender_label(gender, lang) if gender else TEXT2[lang]["not_specified"])
            weight_md = display_weight_md(weight, lang)          # <- новый хелпер
            country_md = escape_markdown(country_display) if country_display else TEXT2[lang]["not_specified"]
            city_md = escape_markdown(city_display) if city_display else TEXT2[lang]["not_specified"]

            # Лайки (используем денормализованное поле)
            likes_count = await conn.fetchval("SELECT likes_count FROM users WHERE user_id = $1", target_id)
            likes_count = likes_count or 0  # Fallback на 0 если NULL
            likes_raw = "1M+" if likes_count >= 1_000_000 else f"{likes_count // 1000}K+" if likes_count >= 1000 else str(likes_count)
            likes_md = escape_markdown(likes_raw)

            name_with_boost = await add_boost_emoji_to_name(name or "—", target_id)
    except Exception as e:
        print(f"⚠️ Ошибка handle_toggle_profile: {e}")
        await query.message.reply_text(TEXT2[lang].get("error_generic", "⚠️ Произошла ошибка. Попробуйте позже."))
        return
    name_boost_md = escape_markdown(name_with_boost)

    caption_lines = [
        f"{TEXT2[lang]['profile_user']}: *{name_boost_md}*",
        f"{TEXT2[lang]['field_level']}: {diff_md}",
        f"{TEXT2[lang]['field_type']}: {climb_md}",
        f"{TEXT2[lang]['field_country']}: {country_md}",
        f"{TEXT2[lang]['field_city']}: {city_md}",
        f"{TEXT2[lang]['field_gender']}: {gender_md}",
        f"{TEXT2[lang]['field_weight']}: {weight_md}",
        f"❤️ {likes_md}"
    ]
    if bio:
        caption_lines.append(f"📝 {escape_markdown(bio)}")

    caption = "\n".join(caption_lines)

    try:
        if photo_bytes:
            from io import BytesIO
            image = BytesIO(photo_bytes)
            image.name = "photo.jpg"
            image.seek(0)

            msg = await context.bot.send_photo(
                chat_id=user_id,
                photo=image,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            msg = await context.bot.send_message(
                chat_id=user_id,
                text=caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )

        context.user_data[key] = msg.message_id

    except Exception as e:
        print(f"❌ Ошибка отправки профиля: {e}")

async def handle_board_status_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")

    await query.message.reply_text(TEXTS[lang]["board_status_active_text"])

async def handle_board_status_removed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")

    await query.message.reply_text(TEXTS[lang]["board_status_removed_text"])


async def handle_time_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "time_page_prev":
        context.user_data["time_page"] = max(context.user_data.get("time_page", 0) - 1, 0)
    elif query.data == "time_page_next":
        context.user_data["time_page"] = context.user_data.get("time_page", 0) + 1

    await show_time_page(update, context)

async def handle_board_my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает тренировки, в которые пользователь записан как участник"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    try:
        today = datetime.now().date()

        async with db_pool.acquire() as conn:
            # Получаем все тренировки (gym_sessions + board_sessions), где пользователь участник
            # Сортируем по дате и времени
            all_sessions = await conn.fetch("""
                SELECT
                    gs.id, gs.gym_name, gs.climb_type, gs.session_date, gs.session_time,
                    'gym' AS session_type,
                    COUNT(gsp2.user_id) AS participants_count
                FROM gym_sessions gs
                JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                LEFT JOIN gym_session_participants gsp2 ON gs.id = gsp2.session_id
                WHERE gsp.user_id = $1 AND gs.session_date >= $2
                GROUP BY gs.id

                UNION ALL

                SELECT
                    bs.id, bs.gym_name, bs.climb_type, bs.session_date, bs.session_time,
                    'board' AS session_type,
                    COUNT(bsp2.user_id) AS participants_count
                FROM board_sessions bs
                JOIN board_session_participants bsp ON bs.id = bsp.session_id
                LEFT JOIN board_session_participants bsp2 ON bs.id = bsp2.session_id
                WHERE bsp.user_id = $1 AND bs.session_date >= $2
                GROUP BY bs.id

                ORDER BY session_date, session_time
            """, user_id, today)

            if not all_sessions:
                await update.message.reply_text(TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."))
                return

            # Формируем страницы пагинации (по 1 тренировке на страницу, но с разворачиванием both)
            session_pages = []
            for session in all_sessions:
                session_dict = dict(session)
                session_pages.append([session_dict])

            # Сохраняем в context для навигации
            context.user_data["board_my_session_pages"] = session_pages
            context.user_data["board_my_session_index"] = 0

            # Показываем первую карточку
            await show_board_my_card(update, context, 0, edit=False)

    except Exception as e:
        print(f"⚠️ Ошибка handle_board_my: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(TEXT2[lang].get("error_generic", "⚠️ Произошла ошибка. Попробуйте позже."))
        return


async def show_board_my_card(update: Update, context: ContextTypes.DEFAULT_TYPE, session_index: int, edit: bool = False):
    """Показывает карточку тренировки из списка 'Мои записи'"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    query = update.callback_query
    message = query.message if query else update.effective_message

    try:
        session_pages = context.user_data.get("board_my_session_pages", [])

        if not session_pages:
            await update.message.reply_text(TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."))
            return

        context.user_data["board_my_session_index"] = session_index

        # Проверяем границы индекса
        if session_index < 0 or session_index >= len(session_pages):
            await update.message.reply_text(TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."))
            return

        # Получаем текущую страницу (может содержать несколько сессий)
        current_page = session_pages[session_index]
        sessions_to_show = current_page

        # Получаем информацию о зале из первой сессии
        first_session = sessions_to_show[0]
        gym_name = first_session.get('gym_name', '')
        session_date = first_session.get('session_date')

        # Заголовок с названием зала
        if gym_name in ("other", "free", None, ""):
            title = TEXT2[lang].get("meetups_today_free", "🧗 Свободная тренировка")
            address = ""
            photo_url = "https://i.postimg.cc/qN0BBrzV/bouldering.jpg"
        else:
            title = f"🧗 {gym_name}"
            # Получаем информацию о зале из списков GYMS_SPB и GYMS_MSK
            gym_info = {}
            # Ищем адрес в списках залов
            for gym in GYMS_SPB + GYMS_MSK:
                if gym[0] == gym_name and len(gym) > 2:
                    gym_info['address'] = gym[2]
                    break

            address = gym_info.get('address', '')
            photo_url = "https://i.postimg.cc/qN0BBrzV/bouldering.jpg"
            if address:
                address = f"📍 {address}"

        # Формируем текст карточки
        cards_text = f"{title}\n"
        if address:
            cards_text += f"{address}\n"

        today = datetime.now().date()

        # Проверяем участие пользователя в тренировках на эту дату
        async with db_pool.acquire() as conn:
            user_gym_session = await conn.fetchrow("""
                SELECT gs.id FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, session_date)

            user_board_session = await conn.fetchrow("""
                SELECT bs.id FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date = $2
            """, user_id, session_date)

        user_gym_session_id = user_gym_session['id'] if user_gym_session else None
        user_board_session_id = user_board_session['id'] if user_board_session else None

        # Обрабатываем сессии на странице
        # Если сессия с climb_type='both', разворачиваем её в две секции
        sections_to_display = []
        for session in sessions_to_show:
            climb_type = session['climb_type']

            if climb_type == 'both':
                # Разворачиваем в две секции: bouldering и lead
                sections_to_display.append({
                    **session,
                    'climb_type': 'bouldering',
                    'display_climb_type': 'bouldering'
                })
                sections_to_display.append({
                    **session,
                    'climb_type': 'lead',
                    'display_climb_type': 'lead'
                })
            else:
                sections_to_display.append({
                    **session,
                    'display_climb_type': climb_type
                })

        # Формируем текст карточки
        for section in sections_to_display:
            display_climb_type = section['display_climb_type']
            session_time = section['session_time'].strftime("%H:%M") if section['session_time'] else "19:00"
            session_date = section.get('session_date', today)
            participants = section['participants_count'] or 0

            # Тип тренировки
            if display_climb_type == "bouldering":
                type_label = TEXT2[lang]["meetups_card_bouldering"]
            else:
                type_label = TEXT2[lang]["meetups_card_lead"]

            # Формируем дату с днем недели
            if session_date == today:
                date_label = TEXT2[lang]['meetups_card_today']
            else:
                # Форматируем дату и добавляем день недели
                weekday_key = f"weekday_{session_date.strftime('%a').lower()[:3]}"
                weekday = TEXT2[lang].get(weekday_key, "")
                date_formatted = session_date.strftime("%d.%m")
                date_label = f"{date_formatted} {weekday}"

            cards_text += f"\n{type_label} · {date_label} · 🕖 {session_time}\n"
            cards_text += TEXT2[lang]["meetups_card_participants"].format(count=participants) + "\n"

        # Добавляем индикатор страницы
        total_pages = len(session_pages)
        if total_pages > 1:
            cards_text += f"\n📄 Тренировка {session_index + 1} из {total_pages}"

        # Кнопки действий - для секций на текущей странице
        keyboard = []

        for section in sections_to_display:
            session_id = section['id']
            display_climb_type = section['display_climb_type']
            session_type = section.get('session_type', 'gym')  # по умолчанию gym

            # Определяем тип для кнопки
            if display_climb_type == "bouldering":
                btn_label = f"{TEXT2[lang]['meetups_btn_join']} ({TEXT2[lang]['meetups_card_bouldering']})"
            else:
                btn_label = f"{TEXT2[lang]['meetups_btn_join']} ({TEXT2[lang]['meetups_card_lead']})"

            # Проверяем участие в зависимости от типа сессии
            is_user_in_session = False
            if session_type == 'board':
                is_user_in_session = (user_board_session_id and user_board_session_id == session_id)
                callback_prefix = "board"
            else:
                is_user_in_session = (user_gym_session_id and user_gym_session_id == session_id)
                callback_prefix = "meetup"

            if is_user_in_session:
                # Пользователь уже записан на эту тренировку
                keyboard.append([
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_chat"], callback_data=f"{callback_prefix}_chat_{session_id}"),
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_participants"], callback_data=f"{callback_prefix}_parts_{session_id}"),
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_leave"], callback_data=f"{callback_prefix}_leave_{session_id}")
                ])
            else:
                # Кнопка присоединения
                keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"{callback_prefix}_join_{session_id}")])

        # Навигация: ◀️ назад, ▶️ вперед
        nav_row = []
        if session_index > 0:
            nav_row.append(InlineKeyboardButton("◀️", callback_data="board_my_nav_prev"))
        # Показываем ▶️ только если это не последняя страница
        if session_index < total_pages - 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data="board_my_nav_next"))
        if nav_row:
            keyboard.append(nav_row)

        # Отправляем/редактируем сообщение
        if edit and message:
            has_photo = bool(message.photo)
            if has_photo:
                try:
                    await message.edit_caption(
                        caption=cards_text,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                except Exception as e:
                    print(f"⚠️ Edit caption failed: {e}, trying edit_media")
                    try:
                        await message.edit_media(
                            media=InputMediaPhoto(media=photo_url, caption=cards_text),
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    except:
                        pass
            else:
                # Переходим от текста к фото — удаляем и отправляем новое
                try:
                    await message.delete()
                except:
                    pass
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_url,
                    caption=cards_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            try:
                if message:
                    await message.delete()
            except:
                pass
            try:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_url,
                    caption=cards_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                print(f"❌ Send photo failed: {e}")

    except Exception as e:
        import traceback
        print(f"❌ Ошибка show_board_my_card: {e}")
        traceback.print_exc()


async def handle_board_my_nav_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Навигация назад в списке 'Мои записи'"""
    query = update.callback_query
    await query.answer()

    current_index = context.user_data.get("board_my_session_index", 0)

    # Переходим к предыдущей тренировке
    if current_index > 0:
        await show_board_my_card(update, context, current_index - 1, edit=True)


async def handle_board_my_nav_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Навигация вперёд в списке 'Мои записи'"""
    query = update.callback_query
    await query.answer()

    current_index = context.user_data.get("board_my_session_index", 0)
    session_pages = context.user_data.get("board_my_session_pages", [])

    # Переходим к следующей странице, если она есть
    next_index = current_index + 1
    if next_index < len(session_pages):
        await show_board_my_card(update, context, next_index, edit=True)


async def send_board_push_if_needed(context, city_name, exclude_user_id=None):
    """Пуш о новой активности — ТОЛЬКО для городов кроме СПб/МСК (кулдаун 3 часа)"""

    # Пропускаем СПб и МСК — у них daily push в 17:00
    if city_name and ("Петербург" in city_name or "Petersburg" in city_name or 
                      "Москва" in city_name or "Moscow" in city_name):
        return

    now = datetime.now()

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT last_push_time FROM city_push_log WHERE city = $1
            """, city_name)
            last_push = row['last_push_time'] if row else None

            if last_push and now - last_push < timedelta(hours=3):
                return

            await conn.execute("""
                INSERT INTO city_push_log (city, last_push_time)
                VALUES ($1, $2)
                ON CONFLICT (city) DO UPDATE SET last_push_time = EXCLUDED.last_push_time
            """, city_name, now)

            users = await conn.fetch("""
                SELECT user_id, language FROM users
                WHERE (city = $1 OR city_other = $1)
                  AND is_deleted = FALSE
            """, city_name)

        for user in users:
            uid, lang = user['user_id'], user['language'] or 'ru'
            if uid == exclude_user_id:
                continue

            try:
                text = TEXT2[lang].get("board_new_activity_push", 
                    "🧗 Кто-то планирует тренировку в твоём городе! Присоединяйся!")
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton(TEXTS[lang]["menu_board"], callback_data="menu_board")
                ]])

                await context.bot.send_message(
                    chat_id=uid,
                    text=text,
                    reply_markup=keyboard
                )
            except Exception as e:
                if "bot was blocked" not in str(e).lower():
                    print(f"⚠️ Board push error for {uid}: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка send_board_push_if_needed: {e}")

async def menu_board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback для кнопки menu_board — перенаправляет в handle_meetups_menu"""
    await handle_meetups_menu(update, context)

######################### Новые чаты ################################# 
async def handle_proxy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.message.from_user.id
        text = update.message.text.strip()
        msg = update.message
    elif update.callback_query:
        await update.callback_query.answer()
        user_id = update.callback_query.from_user.id
        text = None
        msg = update.callback_query.message
    else:
        return

    async with db_pool.acquire() as conn:
        # Язык
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        end_chat_label = TEXTS[lang]["btn_end_chat"]

        # === Завершение чата ===
        if text == end_chat_label:
            partner_id = context.user_data.get("chat_with")

            if not partner_id:
                row = await conn.fetchrow("""
                    SELECT partner_id FROM user_chats
                    WHERE user_id = $1
                    ORDER BY last_message_time DESC
                    LIMIT 1
                """, user_id)
                if row:
                    partner_id = row['partner_id']
                    context.user_data["chat_with"] = partner_id

            if not partner_id:
                await msg.reply_text(TEXT2[lang]["err_no_active_chat"])
                return

            await conn.execute("""
                UPDATE user_chats SET notified_about_new_message = FALSE
                WHERE user_id = $1 AND partner_id = $2
            """, user_id, partner_id)

            context.user_data["chat_with"] = None
            context.user_data["chat_continue_shown"] = False

            menu_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton(TEXTS[lang]["chats_active"])],
                [KeyboardButton(TEXTS[lang]["offline_muted"])],
                [KeyboardButton(TEXTS[lang]["chats_back"])]
            ], resize_keyboard=True)

            await msg.reply_text(TEXT2[lang]["chat_ended_self"], reply_markup=menu_keyboard)
            return

        if text == TEXT2[lang]["btn_back"] and context.user_data.get("confirming_exit"):
            context.user_data["confirming_exit"] = False
            chat_menu = ReplyKeyboardMarkup([[KeyboardButton(end_chat_label)]], resize_keyboard=True)
            await msg.reply_text(TEXT2[lang]["chat_continue"], reply_markup=chat_menu)
            return

        chat_with = context.user_data.get("chat_with")

        # 🔁 Восстанавливаем из базы, если chat_with не установлен
        if not chat_with:
            row = await conn.fetchrow("""
                SELECT partner_id FROM user_chats
                WHERE user_id = $1
                ORDER BY last_message_time DESC
                LIMIT 1
            """, user_id)
            if row:
                chat_with = row['partner_id']
                context.user_data["chat_with"] = chat_with

        if not chat_with:
            await msg.reply_text(TEXT2[lang]["err_no_active_chat"])
            return

        # 🔇 Проверка на mute
        row = await conn.fetchrow("""
            SELECT 1 FROM muted_users WHERE user_id = $1 AND muted_user_id = $2
        """, chat_with, user_id)
        if row:
            return

        chat_id = f"{min(user_id, chat_with)}_{max(user_id, chat_with)}"

        # ✅ Обновление таблиц
        for uid, pid in [(user_id, chat_with), (chat_with, user_id)]:
            await conn.execute("""
                INSERT INTO user_chats (user_id, partner_id, is_archived, last_message_time)
                VALUES ($1, $2, FALSE, NOW())
                ON CONFLICT (user_id, partner_id) DO UPDATE
                SET is_archived = FALSE, last_message_time = NOW()
            """, uid, pid)

        # 💬 Сохраняем сообщение
        await conn.execute("""
            INSERT INTO chat_messages (chat_id, sender_id, message)
            VALUES ($1, $2, $3)
        """, chat_id, user_id, text)

        # 🕓 Обновляем активность
        for uid, pid in [(user_id, chat_with), (chat_with, user_id)]:
            await conn.execute("""
                UPDATE user_chats SET last_message_time = NOW(), is_archived = FALSE
                WHERE user_id = $1 AND partner_id = $2
            """, uid, pid)

        # 🔔 Уведомление
        row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", user_id)
        sender_name = row['name'] if row and row['name'] else TEXT2[lang]["default_user"]

        notify_lang = lang
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", chat_with)
        if row and row['language']:
            notify_lang = row['language']

        partner_data = context.application.user_data.get(chat_with)
        if partner_data and partner_data.get("chat_with") == user_id:
            try:
                await context.bot.send_message(
                    chat_id=chat_with,
                    text=f"*{sender_name}:* {text}",
                    parse_mode="Markdown"
                )
                await conn.execute("""
                    UPDATE user_chats SET last_read_time = NOW()
                    WHERE user_id = $1 AND partner_id = $2
                """, chat_with, user_id)
            except Exception as e:
                print(f"⚠️ Ошибка при отправке live-сообщения: {e}")
        else:
            row = await conn.fetchrow("""
                SELECT last_read_time, last_notified_at, notified_about_new_message
                FROM user_chats
                WHERE user_id = $1 AND partner_id = $2
            """, chat_with, user_id)
            last_read, last_notified, already_notified = (row['last_read_time'], row['last_notified_at'], row['notified_about_new_message']) if row else (None, None, False)

            should_notify = (
                not already_notified and
                (last_read is None or last_notified is None or last_read > last_notified)
            )

            if should_notify:
                open_btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("👤", callback_data=f"profile_{user_id}"),
                    InlineKeyboardButton(TEXT2[notify_lang]["open_chat_btn"],
                                         callback_data=f"open_chat_{user_id}")
                ]])
                try:
                    await context.bot.send_message(
                        chat_id=chat_with,
                        text=TEXT2[notify_lang]["new_message_push"].format(name=sender_name),
                        reply_markup=open_btn
                    )
                    await conn.execute("""
                        UPDATE user_chats
                        SET last_notified_at = NOW(), notified_about_new_message = TRUE
                        WHERE user_id = $1 AND partner_id = $2
                    """, chat_with, user_id)
                except Exception as e:
                    print(f"⚠️ Не удалось отправить уведомление: {e}")


async def start_chat(from_user_id: int, to_user_id: int, context: ContextTypes.DEFAULT_TYPE):
    chat_id = f"{min(from_user_id, to_user_id)}_{max(from_user_id, to_user_id)}"

    async with db_pool.acquire() as conn:
        # Создаём или восстанавливаем связи в обе стороны
        for uid, pid in [(from_user_id, to_user_id), (to_user_id, from_user_id)]:
            await conn.execute("""
                INSERT INTO user_chats (user_id, partner_id, is_archived, last_message_time)
                VALUES ($1, $2, FALSE, NOW())
                ON CONFLICT (user_id, partner_id) DO UPDATE
                SET is_archived = FALSE, last_message_time = NOW()
            """, uid, pid)

        # Устанавливаем кому с кем сейчас общается
        context.user_data["chat_with"] = to_user_id

        # Имя отправителя
        row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", from_user_id)
        sender_name = row['name'] if row and row['name'] else TEXT2["ru"]["default_user"]

        # Уведомление получателю
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", to_user_id)
        lang = row['language'] if row and row['language'] else "ru"

    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("👤", callback_data=f"profile_{from_user_id}"),
        InlineKeyboardButton(TEXT2[lang]["open_chat_btn"],
                             callback_data=f"open_chat_{from_user_id}")
    ]])
    await context.bot.send_message(
        chat_id=to_user_id,
        text=TEXT2[lang]["new_message_push"].format(name=sender_name),
        reply_markup=btn
    )

    # Уведомление себе
    lang = context.user_data.get("lang", "ru")
    await context.bot.send_message(
        chat_id=from_user_id,
        text=TEXT2[lang]["write_confirm_success"]
    )

async def handle_write_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    from_user_id = query.from_user.id
    to_user_id = int(query.data.replace("write_", ""))
    await start_chat(from_user_id, to_user_id, context)


async def handle_open_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    partner_id = int(query.data.replace("open_chat_", ""))

    # Обновляем состояние
    context.user_data["chat_with"] = partner_id
    context.user_data["chat_page"] = 0
    context.user_data.pop("chat_msg_id", None)

    async with db_pool.acquire() as conn:
        # Язык
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        # Имя собеседника
        row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", partner_id)
        partner_name = row['name'] if row and row['name'] else TEXT2[lang]["default_user"]

        # Снимаем архив (если был)
        for uid, pid in [(user_id, partner_id), (partner_id, user_id)]:
            await conn.execute("""
                UPDATE user_chats SET is_archived = FALSE, last_message_time = NOW()
                WHERE user_id = $1 AND partner_id = $2
            """, uid, pid)

    # Заголовок
    await query.message.reply_text(f"👤 {partner_name}\n\n{TEXT2[lang]['chat_history_intro']}")

    # Сразу отправляем клавиатуру — до show_chat_page
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(TEXTS[lang]["btn_end_chat"])]],
        resize_keyboard=True
    )

    # Показ истории
    await show_chat_page(
        chat_id=query.message.chat_id,
        user_id=user_id,
        partner_id=partner_id,
        context=context,
        page=0
    )


def get_active_chats_keyboard(user_id: int, page: int = 0, lang: str = "ru", all_chats: list = None, max_page: int = 0):
    """Генерирует клавиатуру для пагинации 'Активные чаты' (5 чатов на странице)
    Поддерживает как 1x1 чаты (partner_id), так и групповые (chat_type='group')
    """
    if not all_chats:
        return InlineKeyboardMarkup([])

    buttons = []
    for chat in all_chats:
        chat_type = chat.get('chat_type', 'direct')
        name_display = chat.get('name_display', 'User')
        label = f"✉️" + (f" ({chat['unread']})" if chat['unread'] > 0 else "")

        if chat_type == 'group':
            # Групповой чат тренировки (структура как у 1x1 чатов)
            chat_id = chat['chat_id']
            buttons.append([
                InlineKeyboardButton(name_display, callback_data=f"meetup_chat_open_{chat_id}"),
                InlineKeyboardButton(label, callback_data=f"meetup_chat_open_{chat_id}")
            ])
        else:
            # 1x1 чат
            partner_id = chat['partner_id']
            buttons.append([
                InlineKeyboardButton(name_display, callback_data=f"profile_{partner_id}"),
                InlineKeyboardButton(label, callback_data=f"open_chat_{partner_id}"),
                InlineKeyboardButton("🔇", callback_data=f"mute_from_request_{partner_id}"),
                InlineKeyboardButton("❌", callback_data=f"confirm_delete_chat_{partner_id}")
            ])

    # Навигация (◀️ ▶️)
    nav_buttons = []
    if page < max_page:  # Есть ещё страницы вперёд (к старым)
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"active_chats_page_nav_{page+1}"))
    if page > 0:  # Есть предыдущие страницы (к новым)
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"active_chats_page_nav_{page-1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)


async def show_active_chats_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_first: bool = False):
    """Показывает страницу 'Активные чаты' (5 чатов на странице)
    Объединяет 1x1 чаты и групповые чаты тренировок
    """
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    async with db_pool.acquire() as conn:
        # 1. Получаем все активные 1x1 чаты (не архивированные, не мьютированные)
        direct_chats = await conn.fetch("""
            SELECT uc.partner_id, uc.last_read_time, uc.last_message_time
            FROM user_chats uc
            LEFT JOIN muted_users mu ON mu.user_id = uc.user_id AND mu.muted_user_id = uc.partner_id
            WHERE uc.user_id = $1 AND mu.muted_user_id IS NULL AND uc.is_archived = FALSE
        """, user_id)

        # 2. Получаем все активные групповые чаты тренировок (ИЗОЛИРОВАННАЯ система)
        group_chats = await conn.fetch("""
            SELECT mcm.chat_id, mcm.last_read_ts, mca.last_message_ts, gc.chat_name
            FROM meetup_chat_members mcm
            JOIN meetup_chat_activity mca ON mca.chat_id = mcm.chat_id
            JOIN group_chats gc ON gc.id = mcm.chat_id
            WHERE mcm.user_id = $1 AND mcm.is_active = TRUE
        """, user_id)

        # Подготовляем данные с именами и непрочитанными сообщениями
        all_chats_with_data = []

        # 1x1 чаты
        for chat_row in direct_chats:
            partner_id = chat_row['partner_id']
            last_read = chat_row['last_read_time']
            last_msg = chat_row['last_message_time']

            user_row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", partner_id)
            name = user_row['name'] if user_row and user_row['name'] else TEXT2[lang]["default_user"]

            unread_row = await conn.fetchrow("""
                SELECT COUNT(*) FROM chat_messages
                WHERE chat_id = $1 AND sender_id = $2 AND timestamp > COALESCE($3, TIMESTAMP '2000-01-01')
            """, f"{min(user_id, partner_id)}_{max(user_id, partner_id)}", partner_id, last_read)
            unread = unread_row['count']

            all_chats_with_data.append({
                'chat_type': 'direct',
                'partner_id': partner_id,
                'name_display': name,
                'unread': unread,
                'last_message_time': last_msg
            })

        # Групповые чаты
        for chat_row in group_chats:
            chat_id = chat_row['chat_id']
            last_read = chat_row['last_read_ts']
            last_msg = chat_row['last_message_ts']
            chat_name = chat_row['chat_name'] or "🧗 Тренировка"

            # Считаем непрочитанные сообщения (от других участников)
            unread_row = await conn.fetchrow("""
                SELECT COUNT(*) FROM group_chat_messages
                WHERE chat_id = $1 AND sender_id != $2 AND sent_at > COALESCE($3, TIMESTAMP '2000-01-01')
            """, chat_id, user_id, last_read)
            unread = unread_row['count']

            all_chats_with_data.append({
                'chat_type': 'group',
                'chat_id': chat_id,
                'name_display': chat_name,
                'unread': unread,
                'last_message_time': last_msg
            })

        # Сортируем по времени последнего сообщения
        all_chats_with_data.sort(key=lambda x: x.get('last_message_time') or datetime.min, reverse=True)

        if not all_chats_with_data:
            if is_first:
                await update.message.reply_text(TEXT2[lang]["no_chats_yet"])
            else:
                try:
                    await update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
                except BadRequest:
                    pass
            return

    # Вычисляем максимальный номер страницы
    max_page = (len(all_chats_with_data) - 1) // LIKES_PROFILES_PER_PAGE
    page = max(0, min(page, max_page))

    # Сохраняем текущую страницу в контексте
    context.user_data["active_chats_page"] = page

    keyboard = get_active_chats_keyboard(user_id, page, lang, all_chats_with_data, max_page)

    # Проверяем, нужно ли обновить текст (возвращение из меню подтверждения)
    update_text = context.user_data.get("_restore_active_chats", False)

    if is_first:
        # Первый показ - отправляем новое сообщение
        await update.message.reply_text(
            TEXT2[lang]["chat_list"],
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # Пагинация - обновляем существующее меню
        if update_text:
            # Возвращение из меню подтверждения - обновляем и текст и клавиатуру
            try:
                await update.callback_query.message.edit_text(
                    "" + TEXT2[lang]["chat_list"],
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except BadRequest:
                pass  # Query expired - ignore
            # Очищаем флаг
            context.user_data["_restore_active_chats"] = False
        else:
            # Простая пагинация - обновляем только клавиатуру
            try:
                await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)
            except BadRequest:
                pass  # Query expired - ignore


async def handle_active_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список активных чатов с пагинацией"""
    await show_active_chats_page(update, context, page=0, is_first=True)


# ===================== ПАГИНАЦИЯ ЛАЙКОВ =====================
# ПАРАМЕТР СТРАНИЦЫ: profiles_per_page = 1 (строка ниже) - изменить для показа нескольких профилей сразу

LIKES_PROFILES_PER_PAGE = 5  # ← ИЗМЕНИ ЗДЕСЬ, если нужно показывать больше профилей на странице

def get_sent_likes_keyboard(user_id: int, page: int = 0, lang: str = "ru", all_liked: list = None, max_page: int = 0):
    """Генерирует клавиатуру для пагинации 'Мои лайки' (5 профилей на странице)"""
    if not all_liked:
        return InlineKeyboardMarkup([])

    buttons = []
    for user in all_liked:
        liked_id = user['to_user_id']
        buttons.append([
            InlineKeyboardButton(user.get('name_display', 'User'), callback_data=f"profile_{liked_id}"),
            InlineKeyboardButton("✉️", callback_data=f"open_chat_{liked_id}")
        ])

    # Навигация (◀️ ▶️)
    # ◀️ влево = старые пользователи (page+1), ▶️ вправо = новые пользователи (page-1)
    nav_buttons = []
    if page < max_page:  # Есть ещё страницы вперёд (к старым)
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"sent_likes_page_nav_{page+1}"))
    if page > 0:  # Есть предыдущие страницы (к новым)
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"sent_likes_page_nav_{page-1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)


def get_liked_me_keyboard(user_id: int, page: int = 0, lang: str = "ru", all_likers: list = None, max_page: int = 0):
    """Генерирует клавиатуру для пагинации 'Кто меня лайкнул' (5 профилей на странице)"""
    if not all_likers:
        return InlineKeyboardMarkup([])

    buttons = []
    for user in all_likers:
        liker_id = user['from_user_id']
        buttons.append([
            InlineKeyboardButton(user.get('name_display', 'User'), callback_data=f"profile_{liker_id}"),
            InlineKeyboardButton("✉️", callback_data=f"open_chat_{liker_id}")
        ])

    nav_buttons = []
    if page < max_page:  # Есть ещё страницы вперёд (к старым)
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"liked_me_page_nav_{page+1}"))
    if page > 0:  # Есть предыдущие страницы (к новым)
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"liked_me_page_nav_{page-1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)


def get_mutual_likes_keyboard(user_id: int, page: int = 0, lang: str = "ru", all_mutual: list = None, max_page: int = 0):
    """Генерирует клавиатуру для пагинации 'Взаимные лайки' (5 профилей на странице)"""
    if not all_mutual:
        return InlineKeyboardMarkup([])

    buttons = []
    for user in all_mutual:
        mutual_id = user['to_user_id']
        buttons.append([
            InlineKeyboardButton(user.get('name_display', 'User'), callback_data=f"profile_{mutual_id}"),
            InlineKeyboardButton("✉️", callback_data=f"open_chat_{mutual_id}")
        ])

    nav_buttons = []
    if page < max_page:  # Есть ещё страницы вперёд (к старым)
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"mutual_likes_page_nav_{page+1}"))
    if page > 0:  # Есть предыдущие страницы (к новым)
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"mutual_likes_page_nav_{page-1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)


def get_hidden_users_keyboard(user_id: int, page: int = 0, lang: str = "ru", all_hidden: list = None, max_page: int = 0):
    """Генерирует клавиатуру для пагинации 'Скрытые пользователи' (5 профилей на странице)"""
    if not all_hidden:
        return InlineKeyboardMarkup([])

    buttons = []
    for user in all_hidden:
        hidden_id = user['user_id']
        buttons.append([
            InlineKeyboardButton(user.get('name_display', 'User'), callback_data=f"profile_{hidden_id}"),
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_restore_hidden"], callback_data=f"unhide_{hidden_id}")
        ])

    nav_buttons = []
    if page < max_page:  # Есть ещё страницы вперёд (к старым)
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"hidden_users_page_nav_{page+1}"))
    if page > 0:  # Есть предыдущие страницы (к новым)
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"hidden_users_page_nav_{page-1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)


async def show_hidden_users_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_first: bool = False):
    """Показывает страницу 'Скрытые пользователи' (5 профилей на странице)"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    async with db_pool.acquire() as conn:
        # Сначала считаем всех для определения max_page
        count_result = await conn.fetchval("""
            SELECT COUNT(DISTINCT u.user_id)
            FROM users u
            JOIN hidden_users h ON u.user_id = h.hidden_user_id
            WHERE h.user_id = $1
        """, user_id)

        if not count_result or count_result == 0:
            if is_first:
                await update.message.reply_text(TEXT2[lang]["hidden_list_empty"])
            else:
                # Если список опустел при обновлении - показываем пустое меню
                try:
                    await update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
                except BadRequest:
                    pass  # Query expired - ignore
            return

        # Вычисляем максимальный номер страницы
        max_page = (count_result - 1) // LIKES_PROFILES_PER_PAGE
        page = max(0, min(page, max_page))
        offset = page * LIKES_PROFILES_PER_PAGE

        # Загружаем только нужную страницу профилей с информацией о бусте
        page_hidden = await conn.fetch("""
            SELECT DISTINCT u.user_id, u.name, u.is_founder, u.boost_expires_at
            FROM users u
            JOIN hidden_users h ON u.user_id = h.hidden_user_id
            WHERE h.user_id = $1
            ORDER BY u.name
            LIMIT $2 OFFSET $3
        """, user_id, LIKES_PROFILES_PER_PAGE, offset)

    # Подготовка данных профилей с бустом (локально, без доп. запросов)
    page_hidden_with_display = []
    for record in page_hidden:
        name = record['name'] or TEXT2[lang].get("default_user", "User")
        if record['is_founder']:
            name_display = f"{name} 💎"
        elif record['boost_expires_at'] and record['boost_expires_at'] > datetime.now():
            name_display = f"{name} 🗯"
        else:
            name_display = name
        page_hidden_with_display.append(dict(record, name_display=name_display))

    keyboard = get_hidden_users_keyboard(user_id, page, lang, page_hidden_with_display, max_page)

    if is_first:
        # Первый показ - отправляем новое сообщение
        await update.message.reply_text(
            TEXT2[lang].get("hidden_list_title", "👀 Скрытые пользователи"),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # Пагинация - обновляем существующее меню
        try:
            await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)
        except BadRequest:
            pass  # Query expired - ignore


async def show_sent_likes_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_first: bool = False):
    """Показывает страницу 'Мои лайки' (5 профилей на странице)"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    async with db_pool.acquire() as conn:
        # Сначала считаем всех для определения max_page
        count_result = await conn.fetchval("""
            SELECT COUNT(DISTINCT l.to_user_id)
            FROM likes l
            JOIN users u ON u.user_id = l.to_user_id
            WHERE l.from_user_id = $1 AND u.is_deleted = FALSE
        """, user_id)

        if not count_result or count_result == 0:
            if is_first:
                await update.message.reply_text(TEXT2[lang]["likes_empty"])
            return

        # Вычисляем максимальный номер страницы
        max_page = (count_result - 1) // LIKES_PROFILES_PER_PAGE
        page = max(0, min(page, max_page))
        offset = page * LIKES_PROFILES_PER_PAGE

        # Загружаем только нужную страницу профилей с информацией о бусте
        page_liked = await conn.fetch("""
            SELECT l.to_user_id, u.name, u.is_founder, u.boost_expires_at, MAX(l.timestamp) as last_like
            FROM likes l
            JOIN users u ON u.user_id = l.to_user_id
            WHERE l.from_user_id = $1 AND u.is_deleted = FALSE
            GROUP BY l.to_user_id, u.name, u.is_founder, u.boost_expires_at
            ORDER BY MAX(l.timestamp) DESC
            LIMIT $2 OFFSET $3
        """, user_id, LIKES_PROFILES_PER_PAGE, offset)

    # Подготовка данных профилей с бустом (локально, без доп. запросов)
    page_liked_with_display = []
    for record in page_liked:
        name = record['name'] or TEXT2[lang].get("default_user", "User")
        if record['is_founder']:
            name_display = f"{name} 💎"
        elif record['boost_expires_at'] and record['boost_expires_at'] > datetime.now():
            name_display = f"{name} 🗯"
        else:
            name_display = name
        page_liked_with_display.append(dict(record, name_display=name_display))

    keyboard = get_sent_likes_keyboard(user_id, page, lang, page_liked_with_display, max_page)

    if is_first:
        # Первый показ - отправляем новое сообщение
        await update.message.reply_text(
            TEXT2[lang].get("my_likes_list", "👍 Твои лайки"),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # Пагинация - обновляем существующее меню
        try:
            await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)
        except BadRequest:
            pass  # Query expired - ignore


async def show_liked_me_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_first: bool = False):
    """Показывает страницу 'Кто меня лайкнул' (5 профилей на странице)"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Определяем, откуда пришел запрос
    target_message = update.message if update.message else update.callback_query.message

    async with db_pool.acquire() as conn:
        # Сначала считаем всех лайкнувших для определения max_page
        count_result = await conn.fetchval("""
            SELECT COUNT(DISTINCT l.from_user_id)
            FROM likes l
            JOIN users u ON u.user_id = l.from_user_id
            WHERE l.to_user_id = $1 AND u.is_deleted = FALSE
        """, user_id)

        if not count_result or count_result == 0:
            if is_first:
                await target_message.reply_text(TEXT2[lang]["no_likes_yet"])
            return

        # Вычисляем максимальный номер страницы
        max_page = (count_result - 1) // LIKES_PROFILES_PER_PAGE
        page = max(0, min(page, max_page))
        offset = page * LIKES_PROFILES_PER_PAGE

        # Загружаем только нужную страницу профилей с информацией о бусте
        page_likers = await conn.fetch("""
            SELECT l.from_user_id, u.name, u.is_founder, u.boost_expires_at, MAX(l.timestamp) as last_like
            FROM likes l
            JOIN users u ON u.user_id = l.from_user_id
            WHERE l.to_user_id = $1 AND u.is_deleted = FALSE
            GROUP BY l.from_user_id, u.name, u.is_founder, u.boost_expires_at
            ORDER BY MAX(l.timestamp) DESC
            LIMIT $2 OFFSET $3
        """, user_id, LIKES_PROFILES_PER_PAGE, offset)

    # Подготовка данных профилей с бустом (локально, без доп. запросов)
    page_likers_with_display = []
    for record in page_likers:
        name = record['name'] or TEXT2[lang].get("default_user", "User")
        if record['is_founder']:
            name_display = f"{name} 💎"
        elif record['boost_expires_at'] and record['boost_expires_at'] > datetime.now():
            name_display = f"{name} 🗯"
        else:
            name_display = name
        page_likers_with_display.append(dict(record, name_display=name_display))

    keyboard = get_liked_me_keyboard(user_id, page, lang, page_likers_with_display, max_page)

    if is_first:
        await target_message.reply_text(
            TEXT2[lang]["liked_me_list"],
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        try:
            await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)
        except BadRequest:
            pass  # Query expired - ignore


async def show_mutual_likes_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_first: bool = False):
    """Показывает страницу 'Взаимные лайки' (5 профилей на странице)"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Определяем, откуда пришел запрос
    target_message = update.message if update.message else update.callback_query.message

    async with db_pool.acquire() as conn:
        # Сначала считаем всех с взаимными лайками для определения max_page
        count_result = await conn.fetchval("""
            SELECT COUNT(DISTINCT l1.to_user_id)
            FROM likes l1
            JOIN likes l2 ON l1.to_user_id = l2.from_user_id AND l1.from_user_id = l2.to_user_id
            JOIN users u ON u.user_id = l1.to_user_id
            WHERE l1.from_user_id = $1 AND u.is_deleted = FALSE
        """, user_id)

        if not count_result or count_result == 0:
            if is_first:
                await target_message.reply_text(TEXT2[lang]["no_mutual_likes"])
            return

        # Вычисляем максимальный номер страницы
        max_page = (count_result - 1) // LIKES_PROFILES_PER_PAGE
        page = max(0, min(page, max_page))
        offset = page * LIKES_PROFILES_PER_PAGE

        # Загружаем только нужную страницу профилей с информацией о бусте
        page_mutual = await conn.fetch("""
            SELECT l1.to_user_id, u.name, u.is_founder, u.boost_expires_at, MAX(l1.timestamp) as last_like
            FROM likes l1
            JOIN likes l2 ON l1.to_user_id = l2.from_user_id AND l1.from_user_id = l2.to_user_id
            JOIN users u ON u.user_id = l1.to_user_id
            WHERE l1.from_user_id = $1 AND u.is_deleted = FALSE
            GROUP BY l1.to_user_id, u.name, u.is_founder, u.boost_expires_at
            ORDER BY MAX(l1.timestamp) DESC
            LIMIT $2 OFFSET $3
        """, user_id, LIKES_PROFILES_PER_PAGE, offset)

    # Подготовка данных профилей с бустом (локально, без доп. запросов)
    page_mutual_with_display = []
    for record in page_mutual:
        name = record['name'] or TEXT2[lang].get("default_user", "User")
        if record['is_founder']:
            name_display = f"{name} 💎"
        elif record['boost_expires_at'] and record['boost_expires_at'] > datetime.now():
            name_display = f"{name} 🗯"
        else:
            name_display = name
        page_mutual_with_display.append(dict(record, name_display=name_display))

    keyboard = get_mutual_likes_keyboard(user_id, page, lang, page_mutual_with_display, max_page)

    if is_first:
        await target_message.reply_text(
            TEXT2[lang]["mutual_likes_list"],
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        try:
            await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)
        except BadRequest:
            pass  # Query expired - ignore


async def handle_sent_likes_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace("sent_likes_page_nav_", ""))
    await show_sent_likes_page(update, context, page, is_first=False)


async def handle_liked_me_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace("liked_me_page_nav_", ""))
    await show_liked_me_page(update, context, page, is_first=False)


async def handle_mutual_likes_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace("mutual_likes_page_nav_", ""))
    await show_mutual_likes_page(update, context, page, is_first=False)


async def handle_hidden_users_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace("hidden_users_page_nav_", ""))
    # Сохраняем текущую страницу в context
    context.user_data["hidden_users_page"] = page
    await show_hidden_users_page(update, context, page, is_first=False)


async def handle_active_chats_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace("active_chats_page_nav_", ""))
    # Сохраняем текущую страницу в context
    context.user_data["active_chats_page"] = page
    await show_active_chats_page(update, context, page, is_first=False)


async def handle_muted_chats_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.replace("muted_chats_page_nav_", ""))
    # Сохраняем текущую страницу в context
    context.user_data["muted_chats_page"] = page
    await show_muted_chats_page(update, context, page, is_first=False)


async def handle_liked_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кто меня лайкнул - пагинация (первая страница)"""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        # Проверка Boost
        if not await has_active_boost(user_id):
            await show_boost_upsell(update.message or update.callback_query.message, lang)
            return

        # Обновляем last_open
        now = datetime.utcnow()
        await conn.execute("""
            INSERT INTO likes_section_state (user_id, section, last_open)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, section)
            DO UPDATE SET last_open = EXCLUDED.last_open
        """, user_id, "liked_me", now)

    await show_liked_me_page(update, context, page=0, is_first=True)


async def handle_view_liked_me_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback-обработчик для инлайн-кнопки 'Кто меня лайкнул' из пуш-уведомления"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        # Проверка Boost
        if not await has_active_boost(user_id):
            await show_boost_upsell(query.message, lang)
            return

        # Время последнего открытия раздела "liked_me"
        now = datetime.utcnow()
        await conn.execute("""
            INSERT INTO likes_section_state (user_id, section, last_open)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, section)
            DO UPDATE SET last_open = EXCLUDED.last_open
        """, user_id, "liked_me", now)

    # Переходим в Меню Лайки и открываем страницу "Кто меня лайкнул"
    await show_liked_me_page(update, context, page=0, is_first=True)


async def handle_mutual_likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Взаимные лайки - пагинация (первая страница)"""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        # Проверка Boost
        if not await has_active_boost(user_id):
            await show_boost_upsell(update.message or update.callback_query.message, lang)
            return

    await show_mutual_likes_page(update, context, page=0, is_first=True)


async def handle_confirm_delete_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    partner_id = int(query.data.replace("confirm_delete_chat_", ""))
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    buttons = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_yes"], callback_data=f"delete_chat_yes_{partner_id}"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_no"], callback_data=f"delete_chat_no_{partner_id}")
    ]]

    # Редактируем текущее сообщение вместо отправки нового
    await query.message.edit_text(TEXT2[lang]["confirm_exit_prompt"],
                                  reply_markup=InlineKeyboardMarkup(buttons))

async def handle_delete_chat_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    partner_id = int(query.data.replace("delete_chat_yes_", ""))
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Скрываем чат только для этого пользователя
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE user_chats SET is_archived = TRUE
            WHERE user_id = $1 AND partner_id = $2
        """, user_id, partner_id)

    # Отправляем отбивку с сообщением об успехе
    await query.answer(TEXT2[lang]["chat_deleted"])

    # Обновляем меню - пересчитываем список чатов с пагинацией
    # Сохраняем текущую страницу из context если была
    page = context.user_data.get("active_chats_page", 0)
    # Устанавливаем флаг для обновления текста меню
    context.user_data["_restore_active_chats"] = True
    await show_active_chats_page(update, context, page=page, is_first=False)


async def handle_delete_chat_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Возвращаем меню активных чатов вместо удаления сообщения
    page = context.user_data.get("active_chats_page", 0)
    # Используем специальный флаг чтобы обновить меню
    context.user_data["_restore_active_chats"] = True
    await show_active_chats_page(update, context, page=page, is_first=False)


async def show_chat_page(chat_id, user_id, partner_id, context, page: int = 0, message_id: int = None, external_user_data=None):
    data = external_user_data if external_user_data else context.user_data
    data["chat_with"] = partner_id

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
        lang = row['language'] if row and row['language'] else "ru"

        row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", partner_id)
        partner_name = row['name'] if row and row['name'] else TEXT2[lang]["default_user"]

        chat_key = f"{min(user_id, partner_id)}_{max(user_id, partner_id)}"
        total_row = await conn.fetchrow("SELECT COUNT(*) FROM chat_messages WHERE chat_id = $1", chat_key)
        total = total_row['count']

        limit = 10
        max_page = max((total - 1) // limit, 0)
        page = max(min(page, max_page), 0)
        offset = total - (page + 1) * limit
        offset = max(offset, 0)
        fetch_limit = min(limit, total - offset)

        data["chat_page"] = page

        messages = await conn.fetch("""
            SELECT sender_id, message, timestamp FROM chat_messages
            WHERE chat_id = $1
            ORDER BY timestamp ASC
            OFFSET $2 LIMIT $3
        """, chat_key, offset, fetch_limit)

        grouped = {}
        for msg_row in messages:
            sender = msg_row['sender_id']
            msg = msg_row['message']
            ts = msg_row['timestamp']
            date_key = ts.strftime("%d.%m.%Y")
            grouped.setdefault(date_key, []).append((sender, msg))

        msg_blocks = []
        for date, msgs in grouped.items():
            msg_blocks.append(f"*🗓 {date.center(30)}*")
            for sender, msg in msgs:
                name = await get_username(sender)
                msg_blocks.append(f"*{name}:* {msg}")

        history_text = "\n".join(msg_blocks)

        buttons = []
        if page < max_page:
            buttons.append(InlineKeyboardButton("⬅️", callback_data="chat_page_next"))
        if page > 0:
            buttons.append(InlineKeyboardButton("➡️", callback_data="chat_page_prev"))
        markup = InlineKeyboardMarkup([buttons]) if buttons else None

        try:
            msg_id = message_id if message_id else data.get("chat_msg_id")
            if msg_id:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=history_text,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                data["chat_msg_id"] = msg_id
            else:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text=history_text,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                data["chat_msg_id"] = msg.message_id
        except Exception as e:
            print(f"⚠️ Ошибка редактирования/отправки чата: {e}")

        await conn.execute("""
            UPDATE user_chats SET last_read_time = NOW()
            WHERE user_id = $1 AND partner_id = $2
        """, user_id, partner_id)

    if page == 0 and not external_user_data:
        if data.get("last_shown_partner") != partner_id:
            data["chat_continue_shown"] = False
            data["last_shown_partner"] = partner_id

        if not data.get("chat_continue_shown"):
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(TEXTS[lang]["btn_end_chat"])]],
                resize_keyboard=True
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=TEXT2[lang]["chat_continue"],
                reply_markup=keyboard
            )
            data["chat_continue_shown"] = True


async def handle_chat_page_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    partner_id = context.user_data.get("chat_with")
    page = context.user_data.get("chat_page", 0)

    if partner_id is not None and page > 0:
        await show_chat_page(
            chat_id=query.message.chat_id,
            user_id=user_id,
            partner_id=partner_id,
            context=context,
            page=page - 1,
            message_id=context.user_data.get("chat_msg_id")
        )

async def handle_chat_page_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    partner_id = context.user_data.get("chat_with")
    page = context.user_data.get("chat_page", 0)

    if partner_id is not None:
        chat_key = f"{min(user_id, partner_id)}_{max(user_id, partner_id)}"
        async with db_pool.acquire() as conn:
            total_row = await conn.fetchrow("SELECT COUNT(*) FROM chat_messages WHERE chat_id = $1", chat_key)
            total = total_row['count']
        limit = 10
        max_page = (total - 1) // limit

        if page < max_page:
            await show_chat_page(
                chat_id=query.message.chat_id,
                user_id=user_id,
                partner_id=partner_id,
                context=context,
                page=page + 1,
                message_id=context.user_data.get("chat_msg_id")
            )

######################### Новый поиск #########################

async def handle_weight_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    data = query.data.replace("weightval_", "")

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.message.edit_reply_markup(
            reply_markup=get_weight_keyboard(page=page, lang=lang, prefix="weightval_")
        )
        return

    if data == "skip":
        user_sessions[user_id]["weight"] = None
        await save_partial_profile(user_id)
        context.user_data["awaiting_bio"] = True

        keyboard = [[
            InlineKeyboardButton(TEXT2[lang]["btn_skip"],
                                 callback_data="skip_bio")
        ]]
        await query.message.reply_text(
            TEXT2[lang]["ask_bio"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # сохраняем вес
    user_sessions[user_id]["weight"] = data
    await save_partial_profile(user_id)

    await query.message.reply_text(
        TEXT2[lang]["weight_saved"].format(weight=f"{data} {TEXT2[lang]['kg']}"),
        reply_markup=get_progress_keyboard(8, lang)
    )

    context.user_data["awaiting_bio"] = True
    keyboard = [[
        InlineKeyboardButton(TEXT2[lang]["btn_skip"],
                             callback_data="skip_bio")
    ]]
    await query.message.reply_text(
        TEXT2[lang]["ask_bio"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_difficulty_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    data = query.data.replace("diffval_", "")

    # Перелистывание
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.message.edit_reply_markup(
            reply_markup=get_difficulty_keyboard(page=page, lang=lang, prefix="diffval_")
        )
        return

    # Пропуск
    if data == "skip":
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]["difficulty"] = None
        await save_partial_profile(user_id)
    else:
        # Конкретный грейд
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]["difficulty"] = data
        await save_partial_profile(user_id)
        await query.message.reply_text(
            TEXT2[lang]["difficulty_saved"].format(label=data),
            reply_markup=get_progress_keyboard(5, lang)
        )

    # Следующий шаг — выбор пола
    gender_keyboard = [[
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_male"], callback_data="gender_male"),
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_female"], callback_data="gender_female")
    ], [
        InlineKeyboardButton(INLINE_TEXTS[lang]["btn_gender_skip"], callback_data="gender_skip")
    ]]

    await query.message.reply_text(
        TEXT2[lang]["ask_gender"],
        reply_markup=InlineKeyboardMarkup(gender_keyboard)
    )

async def handle_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Просто показываем общее меню инлайн-кнопок (ничего не сбрасываем!)
    await show_filters_menu(update.effective_message, context, user_id, lang, force_new=True)


async def handle_search_difficulty_bucket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    raw = query.data.replace("diffrange_", "")
    # any -> None в БД
    bucket_code = None if raw == "any" else raw

    # Сохраняем в сессию
    filters = user_sessions[user_id].setdefault("search_filters", {})
    filters["difficulty"] = bucket_code

    # Сохраняем в БД (оставляем структуру таблицы прежней)
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO search_filters (user_id, difficulty, climb_type, gender, weight_min, weight_max)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE SET
                difficulty = EXCLUDED.difficulty,
                climb_type = EXCLUDED.climb_type,
                gender = EXCLUDED.gender,
                weight_min = EXCLUDED.weight_min,
                weight_max = EXCLUDED.weight_max
            """,
            user_id,
            bucket_code,
            filters.get("climb_type"),
            filters.get("gender"),
            filters.get("weight_min"),
            filters.get("weight_max")
        )

    await query.message.reply_text(TEXT2[lang]["search_difficulty_saved"])

    # → Следующий шаг как и раньше: выбор типа лазания
    keyboard = [
        [
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_difficulty"], callback_data="search_type_difficulty"),
            InlineKeyboardButton(INLINE_TEXTS[lang]["btn_search_type_bouldering"], callback_data="search_type_bouldering"),
        ],
        [InlineKeyboardButton(INLINE_TEXTS[lang]["btn_weight_any"], callback_data="search_type_any")],
    ]
    await query.message.reply_text(TEXT2[lang]["search_choose_climb_type"], reply_markup=InlineKeyboardMarkup(keyboard))


##################################################################################
ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else None

async def cmd_reset_weights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Эта команда доступна только администратору.")
        return

    try:
        # Получаем пользователей со старыми значениями
        cursor.execute(
            "SELECT user_id FROM users WHERE weight IN ('0_50', '51_80', '81_110')"
        )
        affected_users = cursor.fetchall()

        # Обнуляем вес
        cursor.execute(
            "UPDATE users SET weight = NULL WHERE weight IN ('0_50', '51_80', '81_110')"
        )
        conn.commit()

        await update.message.reply_text(f"✅ Вес сброшен у {len(affected_users)} пользователей. Начинаю рассылку...")

        # Рассылка
        for (uid,) in affected_users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="✅ Старые категории веса успешно очищены.\nУкажи свой вес заново, чтобы находиться в поиске.",
                )
            except Exception as e:
                print(f"⚠️ Не удалось отправить сообщение пользователю {uid}: {e}")

        await update.message.reply_text("✅ Рассылка завершена.")

    except Exception as e:
        print(f"❌ Ошибка при сбросе веса: {e}")
        await update.message.reply_text("❌ Произошла ошибка при сбросе весов.")



async def cmd_reset_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Эта команда доступна только администратору.")
        return

    try:
        # Старые значения, которые нужно обнулить
        old_code_values  = ("beginner", "advanced", "pro", "начинающий", "продвинутый", "профи", "новичок")
        old_label_values = ("3–5C", "3-5C", "6A–6C", "6A-6C", "7A–9C", "7A-9C", "3–5C+", "6A–6C+", "7A–9C+")

        # Найдём пользователей с такими значениями
        cursor.execute(
            """
            SELECT user_id FROM users
            WHERE difficulty IS NOT NULL
              AND (
                    LOWER(TRIM(difficulty)) = ANY($1)
                 OR difficulty = ANY($1)
              )
            """,
            (list(old_code_values), list(old_label_values))
        )
        affected_users = cursor.fetchall()

        if not affected_users:
            await update.message.reply_text("ℹ️ Старых категорий не найдено — ничего сбрасывать не нужно.")
            return

        # Сбрасываем только старые значения в NULL
        cursor.execute(
            """
            UPDATE users
            SET difficulty = NULL
            WHERE difficulty IS NOT NULL
              AND (
                    LOWER(TRIM(difficulty)) = ANY($1)
                 OR difficulty = ANY($1)
              )
            """,
            (list(old_code_values), list(old_label_values))
        )
        conn.commit()

        await update.message.reply_text(
            f"✅ Сброшена старая категория сложности у {len(affected_users)} пользователей. Начинаю рассылку..."
        )

        # Рассылка уведомлений
        for (uid,) in affected_users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="🔄 Мы обновили систему уровней.\nПожалуйста, укажи свой уровень заново — конкретную градацию (например, 6B+)."
                )
            except Exception as e:
                print(f"⚠️ Не удалось отправить сообщение пользователю {uid}: {e}")

        await update.message.reply_text("✅ Рассылка завершена.")

    except Exception as e:
        print(f"❌ Ошибка при сбросе категорий лазания: {e}")
        await update.message.reply_text("❌ Произошла ошибка при сбросе категорий.")


async def cb_set_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    try:
        _, slug = query.data.split(":", 1)
    except ValueError:
        return

    async with db_pool.acquire() as conn:
        if slug == "none":
            await conn.execute("UPDATE users SET status_slug = NULL WHERE user_id = $1", user_id)
        else:
            await conn.execute("UPDATE users SET status_slug = $1 WHERE user_id = $2", slug, user_id)

    opts_map = {s: lbl for s, lbl in TEXT2[lang]["status_options"]}
    label = opts_map.get(slug, TEXT2[lang]["status_not_set"])

    # ✅ Отбивка с текстом
    await query.answer(TEXT2[lang].get("saved"))

    # ✅ Возвращаемся в меню профиля с 9 кнопками
    await edit_profile_menu(update, context)



################################### CRAGSY BOOST ###################################

async def handle_boost_buy_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает подтверждение покупки Boost за 10 г."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    kb = [
        [
            InlineKeyboardButton(TEXT2[lang]["boost_confirm_yes"], callback_data="boost_confirm_yes"),
            InlineKeyboardButton(TEXT2[lang]["boost_confirm_no"], callback_data="boost_confirm_no")
        ]
    ]
    await query.message.reply_text(TEXT2[lang]["boost_confirm_title"], reply_markup=InlineKeyboardMarkup(kb))


async def handle_boost_buy_confirm_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Списывает 10 г магнезии и продлевает Boost на 30 дней."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Проверка магнезии
    if await get_magnesium(user_id) < 10:
        await query.message.reply_text(TEXT2[lang]["boost_not_enough"])
        return

    # Списываем 10 г
    ok = await spend_magnesium(user_id, 10, reason="Покупка Boost за магнезию")
    if not ok:
        await query.message.reply_text(TEXT2[lang]["boost_not_enough"])
        return

    # Продлеваем Boost
    old_active = await has_active_boost(user_id)
    new_exp = await extend_boost_by_month(user_id)

    # Тексты
    date_str = new_exp.strftime("%d.%m.%Y")
    if old_active:
        await query.message.reply_text(TEXT2[lang]["boost_extended_to"].format(date=date_str))
    else:
        await query.message.reply_text(TEXT2[lang]["boost_activated_to"].format(date=date_str))


async def handle_boost_buy_confirm_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        # Полностью удалить сообщение "Confirm Boost..."
        await query.message.delete()
    except BadRequest as e:
        # Если сообщение уже удалено или не удалось — просто логируем
        if "message to delete not found" not in str(e).lower():
            print(f"⚠️ boost_confirm_no delete error: {e}")

async def handle_boost_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус Boost и дни до конца."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if await has_active_boost(user_id):
        days = await boost_days_left(user_id)
        await query.message.reply_text(TEXT2[lang]["boost_status_active"].format(days=days))
    else:
        await query.message.reply_text(TEXT2[lang]["boost_status_inactive"])


async def handle_boost_status_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус Boost (для кнопки из меню)."""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if await has_active_boost(user_id):
        days = await boost_days_left(user_id)
        await update.message.reply_text(TEXT2[lang]["boost_status_active"].format(days=days))
    else:
        await update.message.reply_text(TEXT2[lang]["boost_status_inactive"])


# === НОВЫЕ ТАРИФЫ BOOST ===

async def handle_boost_buy_14(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение покупки 14 дней Boost за 10 г."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    kb = [[
        InlineKeyboardButton("✅ Да", callback_data="boost_confirm_14_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="boost_confirm_14_no")
    ]]
    await query.message.reply_text(
        f"Подтвердить покупку Boost на 14 дней за 10 г магнезии?",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def handle_boost_buy_182(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение покупки 182 дня Boost за 110 г."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    kb = [[
        InlineKeyboardButton("✅ Да", callback_data="boost_confirm_182_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="boost_confirm_182_no")
    ]]
    await query.message.reply_text(
        f"Подтвердить покупку Boost на 182 дня за 110 г магнезии?",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def handle_boost_buy_365(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение покупки 365 дней Boost за 200 г."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    kb = [[
        InlineKeyboardButton("✅ Да", callback_data="boost_confirm_365_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="boost_confirm_365_no")
    ]]
    await query.message.reply_text(
        f"Подтвердить покупку Boost на 365 дней за 200 г магнезии?",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def handle_boost_confirm_14_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Списывает 10 г и добавляет 14 дней Boost."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if await get_magnesium(user_id) < 10:
        await query.message.reply_text("⚠️ Недостаточно магнезии")
        return

    ok = await spend_magnesium(user_id, 10, reason="Покупка 14 дней Boost")
    if not ok:
        await query.message.reply_text("⚠️ Недостаточно магнезии")
        return

    # Добавляем 14 дней
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT boost_expires_at FROM users WHERE user_id = $1", user_id)
        now = datetime.now()
        base = row['boost_expires_at'] if row and row['boost_expires_at'] and row['boost_expires_at'] > now else now
        new_exp = base + timedelta(days=14)
        await conn.execute("UPDATE users SET boost_expires_at = $1 WHERE user_id = $2", new_exp, user_id)

    await query.message.reply_text("✅ Boost активен на 14 дней!")


async def handle_boost_confirm_182_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Списывает 110 г и добавляет 182 дня Boost."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if await get_magnesium(user_id) < 110:
        await query.message.reply_text("⚠️ Недостаточно магнезии")
        return

    ok = await spend_magnesium(user_id, 110, reason="Покупка 182 дня Boost")
    if not ok:
        await query.message.reply_text("⚠️ Недостаточно магнезии")
        return

    # Добавляем 182 дня
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT boost_expires_at FROM users WHERE user_id = $1", user_id)
        now = datetime.now()
        base = row['boost_expires_at'] if row and row['boost_expires_at'] and row['boost_expires_at'] > now else now
        new_exp = base + timedelta(days=182)
        await conn.execute("UPDATE users SET boost_expires_at = $1 WHERE user_id = $2", new_exp, user_id)

    await query.message.reply_text("✅ Boost активен на 182 дня!")


async def handle_boost_confirm_365_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Списывает 200 г и добавляет 365 дней Boost."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if await get_magnesium(user_id) < 200:
        await query.message.reply_text("⚠️ Недостаточно магнезии")
        return

    ok = await spend_magnesium(user_id, 200, reason="Покупка 365 дней Boost")
    if not ok:
        await query.message.reply_text("⚠️ Недостаточно магнезии")
        return

    # Добавляем 365 дней
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT boost_expires_at FROM users WHERE user_id = $1", user_id)
        now = datetime.now()
        base = row['boost_expires_at'] if row and row['boost_expires_at'] and row['boost_expires_at'] > now else now
        new_exp = base + timedelta(days=365)
        await conn.execute("UPDATE users SET boost_expires_at = $1 WHERE user_id = $2", new_exp, user_id)

    await query.message.reply_text("✅ Boost активен на 365 дней!")


async def handle_boost_confirm_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена покупки Boost."""
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except BadRequest as e:
        if "message to delete not found" not in str(e).lower():
            print(f"⚠️ boost_confirm_no delete error: {e}")


async def handle_filters_entry_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    await show_filters_menu(target_message=update.message, context=context, user_id=user_id, lang=lang)

async def show_filters_menu(
    target_message,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    lang: str,
    force_new: bool = False,
    reply_keyboard_markup: ReplyKeyboardMarkup = None
):
    from telegram.error import BadRequest  # локально

    f = await get_search_filters_row(user_id)

    # ✅ Читаем реальный город пользователя из БД
    user_city = None
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city, city_other FROM users WHERE user_id = $1", user_id)
            if row:
                user_city = row['city_other'] if row['city'] == "Другой" else row['city']
    except Exception as e:
        print(f"⚠️ Ошибка при чтении города пользователя: {e}")

    # --- нормализация тристейта: True/False/Any(как None, "", "any", "null") ---
    def norm_tristate(v):
        if v is True or v is False:
            return v
        if v is None:
            return None
        s = str(v).strip().lower()
        if s in ("", "any", "none", "null"):
            return None
        # на всякий случай если пришёл "true"/"false" строкой
        if s in ("true", "yes", "1"):
            return True
        if s in ("false", "no", "0"):
            return False
        return None

    # --- helper: вывод "любые" ---
    def val_or_any(v) -> str:
        return v if (v and str(v).strip()) else TEXT2[lang]["filters_value_any"]

    # 1) Уровень (диапазон)
    def level_value():
        code = f.get("difficulty")
        if not code:
            return TEXT2[lang]["filters_value_any"]
        labels = dict(DIFFICULTY_RANGES)
        return labels.get(code, code)

    # 2) Тип лазания
    def type_value():
        raw = (f.get("climb_type") or "any").strip()
        if raw == "any":
            return TEXT2[lang]["filters_value_any"]
        return get_climb_label(raw, lang)

    # 3) Пол
    def gender_value():
        raw = (f.get("gender") or "any").strip()
        if raw == "any":
            return TEXT2[lang]["filters_value_any"]
        return get_gender_label(raw, lang)

    # 4) Вес
    def weight_value():
        wmin, wmax = f.get("weight_min"), f.get("weight_max")
        if wmin is None or wmax is None:
            return TEXT2[lang]["filters_value_any"]
        return f"{wmin}–{wmax}"

    # 5) С фото — три состояния
    def photo_value():
        has_photo = norm_tristate(f.get("has_photo", None))
        if has_photo is True:
            return TEXT2[lang]["filters_photo_with"]
        if has_photo is False:
            return TEXT2[lang]["filters_photo_without"]
        return TEXT2[lang]["filters_photo_any"]

    # 6) Статус — короткие подписи
    def status_value():
        slug = f.get("status_slug")
        if not slug:
            return TEXT2[lang]["filters_value_any"]
        short = {
            "gym": "🟦 Gym",
            "rock": "🟩 Outdoor",
            "weekend": "📅 Weekends",
            "lead": "🟪 Lead",
            "boulder": "🟨 Boulder",
            "chat": "💬 Chat",
            "pause": "❄️ Pause",

        }
        return short.get(slug, slug)

    # 7) Город — если фильтр не установлен, показываем реальный город пользователя
    def city_value():
        city_override = f.get("city_override")
        if city_override and str(city_override).strip():
            return city_override  # Если фильтр установлен — показываем его
        # Если фильтр не установлен — показываем реальный город пользователя из БД
        return user_city if user_city else TEXT2[lang]["filters_value_any"]

    # 8) Популярные — три состояния
    def popular_value():
        sp = norm_tristate(f.get("sort_popular", None))
        if sp is True:
            return TEXT2[lang]["filters_value_yes"]
        if sp is False:
            return TEXT2[lang]["filters_value_no"]
        return TEXT2[lang]["filters_value_any"]

    # --- ДАЙДЖЕСТ ДЛЯ РАННЕГО ВЫХОДА ---
    curr_digest = (
        f.get("difficulty"),
        (f.get("climb_type") or "any").strip(),
        (f.get("gender") or "any").strip(),
        f.get("weight_min"), f.get("weight_max"),
        norm_tristate(f.get("has_photo", None)),
        f.get("status_slug") or None,
        (f.get("city_override") or "").strip() or None,
        norm_tristate(f.get("sort_popular", None)),
    )
    prev_digest = context.user_data.get("filters_digest")

    # --- клавиатура: слева лейбл (noop), справа кликабельно ---
    lbl_level   = InlineKeyboardButton("🧗 " +  TEXT2[lang]["filter_level"],  callback_data="noop")
    lbl_type    = InlineKeyboardButton("🏔️ " +  TEXT2[lang]["filter_type"],   callback_data="noop")
    lbl_gender  = InlineKeyboardButton("🚻 " +  TEXT2[lang]["filter_gender"], callback_data="noop")
    lbl_weight  = InlineKeyboardButton("⚖️ " +  TEXT2[lang]["filter_weight"], callback_data="noop")
    lbl_photo   = InlineKeyboardButton("🗯 " +  TEXT2[lang]["sp_photo"],      callback_data="noop")
    lbl_status  = InlineKeyboardButton("🗯 " +  TEXT2[lang]["sp_status"],     callback_data="noop")
    lbl_city    = InlineKeyboardButton("🗯 " +  TEXT2[lang]["sp_city"],       callback_data="noop")
    lbl_popular = InlineKeyboardButton("🗯 " +  TEXT2[lang]["sp_popular"],    callback_data="noop")

    val_level   = InlineKeyboardButton(level_value(),   callback_data="filters_difficulty")
    val_type    = InlineKeyboardButton(type_value(),    callback_data="filters_type")
    val_gender  = InlineKeyboardButton(gender_value(),  callback_data="filters_gender")
    val_weight  = InlineKeyboardButton(weight_value(),  callback_data="filters_weight")
    val_photo   = InlineKeyboardButton(photo_value(),   callback_data="filters_photo")
    val_status  = InlineKeyboardButton(status_value(),  callback_data="filters_status")
    val_city    = InlineKeyboardButton(city_value(),    callback_data="filters_city")
    val_popular = InlineKeyboardButton(popular_value(), callback_data="filters_popular")

    keyboard = [
        [lbl_level,   val_level],
        [lbl_type,    val_type],
        [lbl_gender,  val_gender],
        [lbl_weight,  val_weight],
        [lbl_photo,   val_photo],
        [lbl_status,  val_status],
        [lbl_city,    val_city],
        [lbl_popular, val_popular],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    title  = TEXT2[lang]["filters_menu_title"]

    chat_id = target_message.chat_id
    filters_msg_id = context.user_data.get("filters_msg_id")

    # Форс из «🧰» — просто отправляем новое сообщение БЕЗ удаления старого (быстрее!)
    if force_new:
        # Не удаляем старое меню - просто отправляем новое
        # Это быстрее (экономим 1 API call на delete_message)
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=title,
            reply_markup=markup
        )
        context.user_data["filters_msg_id"] = sent.message_id
        context.user_data["filters_digest"] = curr_digest

        # Отправляем ReplyKeyboard с кнопками поиска (если передан)
        if reply_keyboard_markup:
            await context.bot.send_message(
                chat_id=chat_id,
                text=" ",
                reply_markup=reply_keyboard_markup
            )
        return

    # Если нет изменений и контейнер есть — ничего не делаем
    if prev_digest == curr_digest and filters_msg_id:
        return

    # Реактивная перерисовка - обновляем текст И кнопки
    if filters_msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=filters_msg_id,
                text=title,
                reply_markup=markup
            )
            context.user_data["filters_digest"] = curr_digest
            return
        except BadRequest as e:
            if "not modified" in str(e).lower():
                return
            # иначе создадим новое

    # Обычное создание меню (не force_new)
    sent = await target_message.reply_text(title, reply_markup=markup)
    context.user_data["filters_msg_id"] = sent.message_id
    context.user_data["filters_digest"] = curr_digest

async def handle_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


async def handle_filters_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    f = await get_search_filters_row(user_id)
    current_diff = f.get("difficulty")

    rows = []
    for code, label in DIFFICULTY_RANGES:
        marker = " ✓" if code == current_diff else ""
        rows.append([InlineKeyboardButton(label + marker, callback_data=f"search_diff_{code}")])

    marker = " ✓" if current_diff is None else ""
    rows.append([InlineKeyboardButton(TEXT2[lang]["sp_any"] + marker, callback_data="search_diff_any")])
    await q.message.edit_text(TEXT2[lang]["filters_choose_level"], reply_markup=InlineKeyboardMarkup(rows))


async def handle_filters_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    f = await get_search_filters_row(user_id)
    current_type = f.get("climb_type")

    difficulty_label = INLINE_TEXTS[lang]["btn_search_type_difficulty"]
    bouldering_label = INLINE_TEXTS[lang]["btn_search_type_bouldering"]

    if current_type == "difficulty":
        difficulty_label += " ✓"
    elif current_type == "bouldering":
        bouldering_label += " ✓"

    kb = [
        [
            InlineKeyboardButton(difficulty_label, callback_data="search_type_difficulty"),
            InlineKeyboardButton(bouldering_label, callback_data="search_type_bouldering"),
        ],
    ]

    any_label = TEXT2[lang]["sp_any"]
    if current_type not in ["difficulty", "bouldering"]:
        any_label += " ✓"
    kb.append([InlineKeyboardButton(any_label, callback_data="search_type_any")])

    await q.message.edit_text(TEXT2[lang]["filters_choose_type"], reply_markup=InlineKeyboardMarkup(kb))


async def handle_filters_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    f = await get_search_filters_row(user_id)
    current_gender = f.get("gender")

    male_label = INLINE_TEXTS[lang]["btn_gender_male"]
    female_label = INLINE_TEXTS[lang]["btn_gender_female"]

    if current_gender == "male":
        male_label += " ✓"
    elif current_gender == "female":
        female_label += " ✓"

    kb = [
        [
            InlineKeyboardButton(male_label, callback_data="search_gender_male"),
            InlineKeyboardButton(female_label, callback_data="search_gender_female"),
        ],
    ]

    any_label = TEXT2[lang]["sp_any"]
    if current_gender not in ["male", "female"]:
        any_label += " ✓"
    kb.append([InlineKeyboardButton(any_label, callback_data="search_gender_any")])

    await q.message.edit_text(TEXT2[lang]["filters_choose_gender"], reply_markup=InlineKeyboardMarkup(kb))


async def handle_filters_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    f = await get_search_filters_row(user_id)
    weight_min = f.get("weight_min")
    weight_max = f.get("weight_max")
    kb = get_search_weight_keyboard(lang, selected_min=weight_min, selected_max=weight_max)
    await q.message.edit_text(TEXT2[lang]["search_choose_weight"], reply_markup=kb)

def boost_gate_or_none(user_id: int) -> bool:
    return has_active_boost(user_id)

async def show_boost_upsell(target_message, lang):
    buttons = [
        [InlineKeyboardButton(TEXTS[lang]["boost_buy_14_btn"], callback_data="boost_buy_14")],
        [InlineKeyboardButton(TEXTS[lang]["boost_buy_182_btn"], callback_data="boost_buy_182")],
        [InlineKeyboardButton(TEXTS[lang]["boost_buy_365_btn"], callback_data="boost_buy_365")]
    ]
    await target_message.reply_text(
        TEXT2[lang]["menu_chalk_title"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_filters_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if not await has_active_boost(user_id):
        await show_boost_upsell(q.message, lang)
        return

    f = await get_search_filters_row(user_id)
    has_photo = f.get("has_photo")

    with_label = TEXT2[lang]["filters_photo_with"]
    without_label = TEXT2[lang]["filters_photo_without"]
    any_label = TEXT2[lang]["filters_photo_any"]

    if has_photo is True:
        with_label += " ✓"
    elif has_photo is False:
        without_label += " ✓"
    else:
        any_label += " ✓"

    kb = [
        [
            InlineKeyboardButton(with_label, callback_data="photo_set_yes"),
            InlineKeyboardButton(without_label, callback_data="photo_set_no"),
        ],
        [
            InlineKeyboardButton(any_label, callback_data="photo_set_any"),
        ],
    ]

    await q.message.edit_text(
        TEXT2[lang]["filters_q_photo"],
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def handle_filters_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    if not await has_active_boost(user_id):
        await show_boost_upsell(q.message, lang)
        return
    f = await get_search_filters_row(user_id)
    current_status = f.get("status_slug")

    rows = []
    for slug, label in TEXT2[lang]["status_options"]:
        marker = " ✓" if slug == current_status else ""
        rows.append([InlineKeyboardButton(label + marker, callback_data=f"filters_status_set_{slug}")])

    any_label = TEXT2[lang]["sp_any"]
    if current_status is None:
        any_label += " ✓"
    rows.append([InlineKeyboardButton(any_label, callback_data="filters_status_set_any")])
    await q.message.edit_text(TEXT2[lang]["sp_status_choose"], reply_markup=InlineKeyboardMarkup(rows))


async def handle_filters_status_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if q.data.endswith("_any"):
        new_value = None
    else:
        new_value = q.data.replace("filters_status_set_", "")

    f = await get_search_filters_row(user_id)
    old_value = f.get("status_slug")

    force_new = new_value == old_value
    if new_value != old_value:
        await upsert_search_filters(user_id, status_slug=new_value)

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)


async def handle_filters_popular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if not await has_active_boost(user_id):
        await show_boost_upsell(q.message, lang)
        return

    f = await get_search_filters_row(user_id)
    sort_popular = f.get("sort_popular")

    yes_label = TEXT2[lang]["filters_value_yes"]
    no_label = TEXT2[lang]["filters_value_no"]

    if sort_popular is True:
        yes_label += " ✓"
    elif sort_popular is False:
        no_label += " ✓"

    kb = [
        [
            InlineKeyboardButton(yes_label, callback_data="popular_set_yes"),
            InlineKeyboardButton(no_label, callback_data="popular_set_no"),
        ],
    ]

    await q.message.edit_text(
        TEXT2[lang]["filters_q_popular"],
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def handle_filters_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Фильтрация по городу через Geoapify city search
    """
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    if not await has_active_boost(user_id):
        await show_boost_upsell(query.message, lang)
        return

    set_state(context, "awaiting_filter_city_search")

    filter_city_text = TEXT2[lang].get(
        "filters_ask_city_search", 
        "🌍 Укажите город, где будем искать вам напарника для лазания\n\nВведите название города:"
    )

    await query.message.edit_text(
        filter_city_text,
        parse_mode="Markdown"
    )

async def handle_filters_city_country_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пагинация для выбора страны в фильтрах"""
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    if not context.user_data.get("filters_city_flow"):
        return

    # Извлекаем номер страницы
    page = int(q.data.split("_")[-1])
    new_markup = get_country_keyboard(context, page=page, prefix="filters_city_country_", show_custom=False)

    try:
        await q.message.edit_reply_markup(reply_markup=new_markup)
    except:
        pass

async def handle_filters_city_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    if not context.user_data.get("filters_city_flow"):
        return
    country_value = q.data.replace("filters_city_country_", "")
    context.user_data["filters_city_country"] = country_value

    # БЕЗ удаления сообщения! Просто отправляем новое сообщение с выбором города
    kb = get_city_keyboard(context, country_value, page=0, prefix="filters_city_set_", show_custom=False)
    await q.message.reply_text(TEXT2[lang]["filters_ask_city"], reply_markup=kb)


async def handle_filters_city_set_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пагинация для выбора города в фильтрах"""
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    if not context.user_data.get("filters_city_flow"):
        return

    # Извлекаем номер страницы
    page = int(q.data.split("_")[-1])
    country_value = context.user_data.get("filters_city_country")

    if not country_value:
        return

    new_markup = get_city_keyboard(context, country_value, page=page, prefix="filters_city_set_", show_custom=False)

    try:
        await q.message.edit_reply_markup(reply_markup=new_markup)
    except:
        pass


async def handle_filters_city_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]
    if not context.user_data.get("filters_city_flow"):
        return
    city_name = q.data.replace("filters_city_set_", "")

    # Проверяем, не является ли это пагинацией (page_X)
    if city_name.startswith("page_"):
        return

    # Обновляем фильтр города в БД
    await upsert_search_filters(user_id, city_override=city_name)

    # ✅ ОЧИЩАЕМ старые результаты поиска (нужен новый поиск с новым городом)
    context.user_data["search_results"] = []
    context.user_data["search_page"] = 0
    context.user_data["search_buffer"] = []
    context.user_data["search_exhausted"] = False
    context.user_data["search_seen_ids"] = set()  # 🛡️ Сброс показанных

    # Очищаем флаги
    context.user_data["filters_city_flow"] = False
    context.user_data.pop("filters_city_country", None)

    # Отправляем сообщение "Город сохранён" с форсированием меню кнопок
    keyboard = [
        [KeyboardButton(TEXTS[lang]["search_next_person"])],
        [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
        [KeyboardButton(TEXTS[lang]["search_back"])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await q.message.reply_text(
        TEXT2[lang].get("city_saved", "✅ Город сохранён!"),
        reply_markup=reply_markup
    )

    # Отправляем меню фильтров с инлайн кнопками
    await show_filters_menu(q.message, context, user_id, lang, force_new=True, reply_keyboard_markup=None)


async def handle_filters_city_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Очищаем фильтр города в БД
    await upsert_search_filters(user_id, city_override=None)

    # ✅ ОЧИЩАЕМ старые результаты поиска (нужен новый поиск с городом пользователя)
    context.user_data["search_results"] = []
    context.user_data["search_page"] = 0
    context.user_data["search_buffer"] = []
    context.user_data["search_exhausted"] = False
    context.user_data["search_seen_ids"] = set()  # 🛡️ Сброс показанных

    # Очищаем все флаги города
    context.user_data["filters_city_flow"] = False
    context.user_data["filtering_city_via_geo"] = False
    context.user_data.pop("city_search_results", None)
    context.user_data.pop("filters_city_country", None)

    # Отправляем сообщение "Фильтр очищен" с форсированием меню кнопок
    keyboard = [
        [KeyboardButton(TEXTS[lang]["search_next_person"])],
        [KeyboardButton(TEXTS[lang]["search_find"]), KeyboardButton(TEXTS[lang]["search_filters"]), KeyboardButton(TEXTS[lang]["search_hidden"])],
        [KeyboardButton(TEXTS[lang]["search_back"])]
    ]
    search_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await q.message.reply_text(
        TEXT2[lang].get("filter_cleared", "✅ Фильтр очищен!"),
        reply_markup=search_keyboard
    )

    # Отправляем меню фильтров с инлайн кнопками
    await show_filters_menu(q.message, context, user_id, lang, force_new=True, reply_keyboard_markup=None)


async def handle_photo_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    data = q.data
    if data == "photo_set_yes":
        new_value = True
    elif data == "photo_set_no":
        new_value = False
    else:
        new_value = None

    f = await get_search_filters_row(user_id)
    old_value = f.get("has_photo")

    force_new = new_value == old_value
    if new_value != old_value:
        await upsert_search_filters(user_id, has_photo=new_value)
        context.user_data["filters_dirty"] = True

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)


async def handle_popular_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    data = q.data
    new_value = data == "popular_set_yes"

    f = await get_search_filters_row(user_id)
    old_value = f.get("sort_popular")

    force_new = new_value == old_value
    if new_value != old_value:
        await upsert_search_filters(user_id, sort_popular=new_value)
        context.user_data["filters_dirty"] = True

    await show_filters_menu(q.message, context, user_id, lang, force_new=force_new)

async def handle_filters_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔙 Обработчик кнопки Назад из подменю фильтров"""
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    await show_filters_menu(q.message, context, user_id, lang)


async def handle_edit_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    await query.answer()

    opts = TEXT2[lang]["status_options"]
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"set_status:{slug}")]
        for slug, label in opts
    ]

    await safe_edit_or_reply(
        query.message,
        TEXT2[lang]["choose_status"],
        reply_markup=InlineKeyboardMarkup(buttons),
        lang=lang
    )


# ============ TELEGRAM STARS PAYMENT HANDLERS ============

async def handle_buy_chalk_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback для покупки магнезии за Stars (10г, 20г, 100г)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    # Определяем тариф с текстами на 4 языках
    data = query.data
    if data == "buy_chalk_10":
        amount = 10
        stars = 75
        title = TEXT2[lang]["invoice_chalk_10_title"]
        description = TEXT2[lang]["invoice_chalk_10_desc"]
    elif data == "buy_chalk_20":
        amount = 20
        stars = 150
        title = TEXT2[lang]["invoice_chalk_20_title"]
        description = TEXT2[lang]["invoice_chalk_20_desc"]
    elif data == "buy_chalk_100":
        amount = 100
        stars = 750
        title = TEXT2[lang]["invoice_chalk_100_title"]
        description = TEXT2[lang]["invoice_chalk_100_desc"]
    else:
        return

    # Отправляем invoice
    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=title,
        description=description,
        payload=f"chalk_{amount}",
        provider_token="",  # Пустая строка для Telegram Stars
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label=title, amount=stars)]
    )


async def handle_buy_founder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback для покупки Founder статуса за 10000 Stars"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    # Отправляем invoice с текстами на 4 языках
    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=TEXT2[lang]["invoice_founder_title"],
        description=TEXT2[lang]["invoice_founder_desc"],
        payload="founder_status",
        provider_token="",  # Пустая строка для Telegram Stars
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label="💎 Founder", amount=5000)]
    )


async def send_photo_reminders():
    """Рассылка напоминаний о загрузке фото всем пользователям без фото"""
    if not application or not application.bot:
        return

    try:
        async with db_pool.acquire() as conn:
            # 1️⃣ ОЧИСТКА: Удаляем записи старше 45 дней (для повторной отправки)
            await conn.execute("""
                DELETE FROM photo_reminders_log 
                WHERE sent_at < NOW() - INTERVAL '45 days'
            """)
            print("🗑️ Очистка старых записей (>45 дней) выполнена")

            # 2️⃣ Получаем пользователей без фото, которым ещё не отправляли ИЛИ прошло 45 дней
            users = await conn.fetch("""
                SELECT u.user_id, u.language 
                FROM users u
                WHERE u.has_real_photo = FALSE 
                AND u.is_deleted = FALSE
                AND NOT EXISTS (
                    SELECT 1 FROM photo_reminders_log WHERE user_id = u.user_id
                )
            """)

            sent_count = 0
            failed_count = 0

            for user_row in users:
                user_id = user_row['user_id']
                user_lang = user_row['language'] or 'ru'

                try:
                    keyboard = [[
                        InlineKeyboardButton("🖼 " + TEXT2.get(user_lang, {}).get("field_photo", "Photo"), 
                                           callback_data="photo_reminder_update"),
                        InlineKeyboardButton("⏭ " + TEXT2.get(user_lang, {}).get("btn_skip", "Skip"), 
                                           callback_data="photo_reminder_skip")
                    ]]

                    # Отправляем фото с текстом
                    with open("assets/photo_reminder.jpg", "rb") as photo_file:
                        await application.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_file,
                            caption=TEXT2.get(user_lang, {}).get("photo_reminder_msg", "📸 Don't forget to add a photo!"),
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )

                    # Логируем отправку
                    await conn.execute(
                        "INSERT INTO photo_reminders_log (user_id, reminder_day) VALUES ($1, $2)",
                        user_id, 1
                    )
                    sent_count += 1
                except Exception as e:
                    print(f"⚠️ Ошибка отправки напоминания юзеру {user_id}: {e}")
                    failed_count += 1

            print(f"✅ Рассылка завершена: отправлено {sent_count}, ошибок {failed_count}")

    except Exception as e:
        print(f"❌ Ошибка send_photo_reminders: {e}")


async def handle_photo_reminder_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для редактирования фото из напоминания"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Получаем язык пользователя
    await ensure_lang(context, user_id)
    context.user_data["lang"] = context.user_data.get("lang", "ru")

    # Переходим к редактированию фото (как в профиле)
    await edit_photo_prompt(update, context)


async def handle_photo_reminder_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скип напоминания о фото"""
    query = update.callback_query
    await query.answer(TEXT2.get(context.user_data.get("lang", "ru"), {}).get("saved", "✓ Сохранено"))
    await query.message.delete()


async def handle_admin_send_photo_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ функция - рассылка напоминаний всем 400 юзерам"""
    query = update.callback_query
    user_id = query.from_user.id

    # Проверка админа (ID 123456789 - заглушка)
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    if user_id not in ADMIN_IDS:
        await query.answer("❌ Only admin", show_alert=True)
        return

    await query.answer("✅ Starting reminders...")
    await query.message.reply_text("📨 Рассылка напоминаний начата...")

    # Запускаем рассылку асинхронно
    await send_photo_reminders()

    await query.message.reply_text("✅ Рассылка завершена!")


async def reset_photo_reminders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для админа - сброс счетчика напоминаний о фото для теста"""
    user_id = update.effective_user.id

    # Проверка админа
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only admin")
        return

    try:
        async with db_pool.acquire() as conn:
            # Полностью очищаем photo_reminders_log
            await conn.execute("DELETE FROM photo_reminders_log")

        await update.message.reply_text("✅ Счетчик напоминаний о фото сброшен! Все записи удалены.")
    except Exception as e:
        print(f"❌ Ошибка сброса счетчика: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pre-checkout handler - валидация перед оплатой"""
    query = update.pre_checkout_query

    # Проверяем валидность заказа
    if query.invoice_payload in ["chalk_10", "chalk_20", "chalk_100", "founder_status"]:
        # Подтверждаем оплату
        await query.answer(ok=True)
    else:
        # Отклоняем с ошибкой
        await query.answer(ok=False, error_message="Something went wrong. Please try again.")


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик успешной оплаты - начисление магнезии/статуса"""
    payment = update.message.successful_payment
    user_id = update.message.from_user.id

    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    payload = payment.invoice_payload
    amount_paid = payment.total_amount

    # Логируем транзакцию
    print(f"💰 Payment received: User {user_id}, Payload: {payload}, Amount: {amount_paid} Stars")
    print(f"Telegram Charge ID: {payment.telegram_payment_charge_id}")

    # Обрабатываем разные типы покупок
    if payload == "founder_status":
        # Выдаём статус Founder
        async with db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE users 
                SET is_founder = TRUE
                WHERE user_id = $1
            """, user_id)

        # Начисляем 500г магнезии через правильную функцию
        await add_magnesium(user_id, 500.0, "Founder status purchase (5,000⭐)")

        # Отправляем подтверждение
        await update.message.reply_markdown(TEXT2[lang]["chalk_founder_success"])

    elif payload.startswith("chalk_"):
        # Выдаём магнезию
        chalk_amount = int(payload.replace("chalk_", ""))

        # Начисляем магнезию через правильную функцию
        await add_magnesium(user_id, float(chalk_amount), f"Telegram Stars purchase ({amount_paid}⭐)")

        # Отправляем подтверждение
        await update.message.reply_text(
            TEXT2[lang]["chalk_stars_success"].format(amount=chalk_amount)
        )


# ===== MEETUPS (🤝 Встречи) =====

async def handle_meetups_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню встреч — показываем подменю с кнопками + выбор зала"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Устанавливаем режим встреч
    context.user_data["in_meetups_mode"] = True
    context.user_data["meetups_gym_index"] = 0

    # Определяем источник (кнопка меню или callback)
    is_callback = update.callback_query is not None
    if is_callback:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = row['city'] if row else None

            # Проверяем, в каких залах пользователь записан на тренировки (дефолтные + кастомные, любые даты)
            today = datetime.now().date()

            # === НОВЫЙ БЛОК: Подсчёт участников по залам ===
            gym_participants = {}

            # Считаем из gym_sessions
            gym_counts = await conn.fetch("""
                SELECT gs.gym_name, COUNT(DISTINCT gsp.user_id) as cnt
                FROM gym_sessions gs
                JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                WHERE gs.session_date >= $1 AND gs.gym_name IS NOT NULL
                GROUP BY gs.gym_name
            """, today)

            # Считаем из board_sessions
            board_counts = await conn.fetch("""
                SELECT bs.gym_name, COUNT(DISTINCT bsp.user_id) as cnt
                FROM board_sessions bs
                JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.session_date >= $1 AND bs.gym_name IS NOT NULL AND bs.status = 'active'
                GROUP BY bs.gym_name
            """, today)

            # Объединяем
            for row in gym_counts:
                if row['gym_name']:
                    gym_participants[row['gym_name']] = row['cnt']
            for row in board_counts:
                if row['gym_name']:
                    gym_participants[row['gym_name']] = gym_participants.get(row['gym_name'], 0) + row['cnt']

            # === НОВЫЙ БЛОК: Подсчёт для "Другая локация" ===
            # Подсчёт для "Другая локация" — только по городу пользователя
            known_gyms = set(g[0] for g in GYMS_SPB + GYMS_MSK)

            # Определяем city_key пользователя
            user_city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    user_city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    user_city_key = "msk"
                else:
                    user_city_key = user_city

            # Считаем только кастомные локации в городе пользователя
            other_location_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT bsp.user_id)
                FROM board_sessions bs
                JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.session_date >= $1 
                  AND bs.status = 'active'
                  AND bs.city_key = $2
                  AND (bs.gym_name IS NULL OR bs.gym_name NOT IN (SELECT unnest($3::text[])))
            """, today, user_city_key, list(known_gyms)) or 0
            # === КОНЕЦ НОВОГО БЛОКА ===

            # === Подсчёт для "Свободная тренировка" (gym_sessions с gym_name IS NULL) ===
            free_training_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT gsp.user_id)
                FROM gym_sessions gs
                JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                WHERE gs.session_date >= $1 AND gs.gym_name IS NULL
            """, today) or 0
            
            # Получаем залы из gym_sessions (дефолтные тренировки)
            gym_sessions_gyms = await conn.fetch("""
                SELECT DISTINCT gs.gym_name
                FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date >= $2
            """, user_id, today)

            # Получаем залы из board_sessions (кастомные тренировки)
            board_sessions_gyms = await conn.fetch("""
                SELECT DISTINCT bs.gym_name
                FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date >= $2
            """, user_id, today)

            # Объединяем списки залов в set для уникальности
            user_gyms = set()
            for row in gym_sessions_gyms:
                if row['gym_name']:
                    user_gyms.add(row['gym_name'])
            for row in board_sessions_gyms:
                if row['gym_name']:
                    user_gyms.add(row['gym_name'])

            # Проверяем, записан ли пользователь в "свободную тренировку" (дефолтные gym_sessions без gym_name)
            has_free_training = any(row['gym_name'] is None for row in gym_sessions_gyms)

            # Проверяем, записан ли пользователь в "другую локацию" (кастомные board_sessions с нестандартным gym_name)
            known_gyms = set(g[0] for g in GYMS_SPB + GYMS_MSK)
            has_custom_location = any(
                row['gym_name'] is not None and row['gym_name'] not in known_gyms 
                for row in board_sessions_gyms
            )

        # 1. Показываем ReplyKeyboard с кнопками подменю (как было в board)
        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(TEXTS[lang]["board_city"])],
            [KeyboardButton(TEXTS[lang]["board_create"]),
             KeyboardButton(TEXTS[lang]["board_my"])],
            [KeyboardButton(TEXTS[lang]["board_back"])]
        ], resize_keyboard=True)

        # 2. Определяем залы по городу для InlineKeyboard
        inline_keyboard = []

        if user_city and ("Петербург" in user_city or "Petersburg" in user_city):
            # СПб — показываем залы парами
            for i in range(0, len(GYMS_SPB), 2):
                row_btns = []
                for gym in GYMS_SPB[i:i+2]:
                    gym_name = gym[0]
                    count = gym_participants.get(gym_name, 0)

                    # Формируем label с количеством
                    if count > 0:
                        gym_label = f"{gym_name} · {count} 👤"
                    else:
                        gym_label = gym_name

                    row_btns.append(InlineKeyboardButton(gym_label, callback_data=f"meetup_gym_{gym_name}"))
                inline_keyboard.append(row_btns)

            # Показываем кнопку "Другая локация" с количеством
            other_label = TEXT2[lang]["meetups_other_location"]
            if other_location_count > 0:
                other_label = f"{other_label} · {other_location_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(other_label, callback_data="meetup_gym_other")])

        elif user_city and ("Москва" in user_city or "Moscow" in user_city):
        # Москва — показываем залы парами
            for i in range(0, len(GYMS_MSK), 2):
                row_btns = []
                for gym in GYMS_MSK[i:i+2]:
                    gym_name = gym[0]
                    count = gym_participants.get(gym_name, 0)
    
                    # Формируем label с количеством
                    if count > 0:
                        gym_label = f"{gym_name} · {count} 👤"
                    else:
                        gym_label = gym_name
    
                    row_btns.append(InlineKeyboardButton(gym_label, callback_data=f"meetup_gym_{gym_name}"))
                inline_keyboard.append(row_btns)

            # Показываем кнопку "Другая локация" с количеством
            other_label = TEXT2[lang]["meetups_other_location"]
            if other_location_count > 0:
                other_label = f"{other_label} · {other_location_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(other_label, callback_data="meetup_gym_other")])

        else:
            # Другие города — свободная тренировка + другая локация
            free_label = TEXT2[lang]["meetups_free_training"]
            if free_training_count > 0:
                free_label = f"{free_label} · {free_training_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(free_label, callback_data="meetup_gym_free")])
    
            # Добавляем кнопку "Другая локация" с количеством
            other_label = TEXT2[lang]["meetups_other_location"]
            if other_location_count > 0:
                other_label = f"{other_label} · {other_location_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(other_label, callback_data="meetup_gym_other")])

        # Если вызвано через callback (возврат) — удаляем старое сообщение с фото
        if is_callback:
            try:
                await message.delete()
            except:
                pass

        # Сначала отправляем сообщение с ReplyKeyboard (переход в подменю)
        await context.bot.send_message(
            chat_id=user_id,
            text=TEXTS[lang]["board_menu_title"],
            reply_markup=reply_keyboard
        )

        # Затем отправляем выбор зала с InlineKeyboard
        await context.bot.send_message(
            chat_id=user_id,
            text=TEXT2[lang]["meetups_choose_gym"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard)
        )
    except Exception as e:
        print(f"❌ Ошибка handle_meetups_menu: {e}")

def group_sessions_into_pages(all_sessions, today):
    """
    Группирует сессии в страницы для пагинации.
    Дефолтные на одну дату = одна страница.
    Кастомные = по одной странице.
    """
    session_pages = []
    i = 0
    while i < len(all_sessions):
        current_session = all_sessions[i]

        # Если дефолтная - группируем все дефолтные на ту же дату
        if current_session.get('is_default', False):
            page_sessions = [current_session]
            session_date = current_session.get('session_date', today)

            j = i + 1
            while j < len(all_sessions):
                next_session = all_sessions[j]
                if (next_session.get('is_default', False) and
                    next_session.get('session_date', today) == session_date):
                    page_sessions.append(next_session)
                    j += 1
                else:
                    break

            session_pages.append(page_sessions)
            i = j
        else:
            # Кастомная - одна страница
            session_pages.append([current_session])
            i += 1

    return session_pages


async def reload_gym_sessions(conn, gym_name, user_id):
    """
    Перезагружает сессии для зала (gym + board), группирует и возвращает.
    Используется после join/leave для обновления карточки.
    """
    today = datetime.now().date()

    # Получаем city_key
    user_row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
    user_city = user_row['city'] if user_row else "unknown"
    city_key = None
    if user_city:
        if "Петербург" in user_city or "Petersburg" in user_city:
            city_key = "spb"
        elif "Москва" in user_city or "Moscow" in user_city:
            city_key = "msk"
        
        else:
            # Для других городов используем сам город как city_key
            city_key = user_city

    # Получаем gym_sessions
    if gym_name in ("other", "free"):
        gym_sessions = await conn.fetch("""
            SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                   COUNT(gsp.user_id) AS participants_count,
                   'gym' as session_type
            FROM gym_sessions gs
            LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
            WHERE gs.city_key = $1 AND gs.gym_name IS NULL AND gs.session_date >= $2
            GROUP BY gs.id
            ORDER BY gs.session_date, gs.session_time
        """, city_key, today)
    else:
        gym_sessions = await conn.fetch("""
            SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                   COUNT(gsp.user_id) AS participants_count,
                   'gym' as session_type
            FROM gym_sessions gs
            LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
            WHERE gs.gym_name = $1 AND gs.session_date >= $2
            GROUP BY gs.id
            ORDER BY gs.session_date, gs.session_time
        """, gym_name, today)

    # Получаем board_sessions
    known_gyms = set(g[0] for g in GYMS_SPB + GYMS_MSK)

    if gym_name == "other":
        # Кастомные локации — gym_name не в списке известных залов
        board_sessions = await conn.fetch("""
            SELECT bs.id, bs.gym_name, bs.climb_type, bs.session_time, bs.session_date,
                   FALSE as is_default,
                   COUNT(bsp.user_id) AS participants_count,
                   'board' as session_type
            FROM board_sessions bs
            LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
            WHERE bs.city_key = $1 
              AND bs.gym_name IS NOT NULL
              AND bs.gym_name NOT IN (SELECT unnest($3::text[]))
              AND bs.session_date >= $2 AND bs.status = 'active'
            GROUP BY bs.id
            ORDER BY bs.session_date, bs.session_time
        """, city_key, today, list(known_gyms))
    elif gym_name == "free":
        # Свободные тренировки — gym_name IS NULL
        board_sessions = await conn.fetch("""
            SELECT bs.id, bs.gym_name, bs.climb_type, bs.session_time, bs.session_date,
                   FALSE as is_default,
                   COUNT(bsp.user_id) AS participants_count,
                   'board' as session_type
            FROM board_sessions bs
            LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
            WHERE bs.city_key = $1 AND bs.gym_name IS NULL
              AND bs.session_date >= $2 AND bs.status = 'active'
            GROUP BY bs.id
            ORDER BY bs.session_date, bs.session_time
        """, city_key, today)
        
    else:
        board_sessions = await conn.fetch("""
            SELECT bs.id, bs.gym_name, bs.climb_type, bs.session_time, bs.session_date,
                   FALSE as is_default,
                   COUNT(bsp.user_id) AS participants_count,
                   'board' as session_type
            FROM board_sessions bs
            LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
            WHERE bs.gym_name = $1
              AND bs.session_date >= $2 AND bs.status = 'active'
            GROUP BY bs.id
            ORDER BY bs.session_date, bs.session_time
        """, gym_name, today)

    # Объединяем и сортируем
    all_sessions = list(gym_sessions) + list(board_sessions)
    all_sessions.sort(key=lambda s: (
        s['session_date'] if s['session_date'] else today,
        s['session_time'] if s['session_time'] else datetime.strptime("00:00", "%H:%M").time()
    ))

    # Группируем
    session_pages = group_sessions_into_pages(all_sessions, today)

    return session_pages


async def show_meetup_gym_by_index(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int, edit: bool = False):
    """Показывает карточку зала по индексу (для кнопок board_city/board_show_more)"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    try:
        # Используем сохранённый список залов, если есть
        gyms_list = context.user_data.get("meetups_gyms_list")

        if not gyms_list:
            # Fallback: определяем список залов по городу
            async with db_pool.acquire() as conn:
                row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
                user_city = row['city'] if row else None

            if user_city and ("Петербург" in user_city or "Petersburg" in user_city):
                gyms_list = [g[0] for g in GYMS_SPB]
            elif user_city and ("Москва" in user_city or "Moscow" in user_city):
                gyms_list = [g[0] for g in GYMS_MSK]
            else:
                gyms_list = ["free"]
            context.user_data["meetups_gyms_list"] = gyms_list

        # Циклическая пагинация
        if index >= len(gyms_list):
            index = 0
        if index < 0:
            index = len(gyms_list) - 1

        # Сохраняем состояние навигации
        context.user_data["meetups_gym_index"] = index
        gym_name = gyms_list[index]
        context.user_data["meetup_selected_gym"] = gym_name

        # Загружаем сессии для этого зала (gym_sessions + board_sessions)
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = row['city'] if row else "unknown"

            today = datetime.now().date()

            # Определяем city_key
            city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    city_key = "msk"
                else:
                    # Для других городов используем сам город как city_key
                    city_key = user_city

            # Получаем gym_sessions для этого зала (все будущие и сегодняшние)
            if gym_name in ("other", "free"):
                gym_sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count,
                           'gym' as session_type
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.city_key = $1 AND gs.gym_name IS NULL AND gs.session_date >= $2
                    GROUP BY gs.id
                    ORDER BY gs.session_date, gs.session_time
                """, city_key, today)

                # Для "Другая локация" НЕ создаём дефолтные сессии
                gym_sessions = list(gym_sessions)
            else:
                gym_sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count,
                           'gym' as session_type
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.gym_name = $1 AND gs.session_date >= $2
                    GROUP BY gs.id
                    ORDER BY gs.session_date, gs.session_time
                """, gym_name, today)

                gym_sessions = list(gym_sessions)

                # Если нет gym_sessions — создаём дефолтные
                if not gym_sessions:
                    default_time = datetime.strptime("19:00", "%H:%M").time()
                    tz = get_timezone_for_city(user_city)

                    # Определяем типы тренировок для этого зала
                    gym_climb_type = get_gym_climb_type(gym_name)
                    if gym_climb_type == "bouldering":
                        climb_types_to_create = ["bouldering"]
                    else:
                        climb_types_to_create = ["bouldering", "lead"]

                    for climb_type in climb_types_to_create:
                        await conn.execute("""
                            INSERT INTO gym_sessions (gym_name, city_key, climb_type, session_date, session_time, is_default, timezone)
                            VALUES ($1, $2, $3, $4, $5, TRUE, $6)
                        """, gym_name, city_key, climb_type, today, default_time, tz)

                    gym_sessions = await conn.fetch("""
                        SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                               COUNT(gsp.user_id) AS participants_count,
                               'gym' as session_type
                        FROM gym_sessions gs
                        LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                        WHERE gs.gym_name = $1 AND gs.session_date >= $2
                        GROUP BY gs.id
                        ORDER BY gs.session_date, gs.session_time
                    """, gym_name, today)
                    gym_sessions = list(gym_sessions)

            # Загружаем board_sessions для этого зала
            if gym_name in ("other", "free"):
                board_sessions = await conn.fetch("""
                    SELECT bs.id, bs.climb_type, bs.session_time, bs.session_date,
                           FALSE as is_default,
                           COUNT(bsp.user_id) AS participants_count,
                           'board' as session_type
                    FROM board_sessions bs
                    LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    WHERE bs.city_key = $1 AND bs.gym_name IS NULL
                      AND bs.session_date >= $2 AND bs.status = 'active'
                    GROUP BY bs.id
                    ORDER BY bs.session_date, bs.session_time
                """, city_key, today)
            else:
                board_sessions = await conn.fetch("""
                    SELECT bs.id, bs.climb_type, bs.session_time, bs.session_date,
                           FALSE as is_default,
                           COUNT(bsp.user_id) AS participants_count,
                           'board' as session_type
                    FROM board_sessions bs
                    LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    WHERE bs.gym_name = $1
                      AND bs.session_date >= $2 AND bs.status = 'active'
                    GROUP BY bs.id
                    ORDER BY bs.session_date, bs.session_time
                """, gym_name, today)

            # Объединяем gym_sessions и board_sessions
            all_sessions = gym_sessions + list(board_sessions)

            # Сортируем все сессии по дате, затем по времени
            all_sessions.sort(key=lambda s: (
                s['session_date'] if s['session_date'] else today,
                s['session_time'] if s['session_time'] else datetime.strptime("00:00", "%H:%M").time()
            ))

        # Группируем сессии для пагинации
        session_pages = group_sessions_into_pages(all_sessions, today)

        # Сохраняем сгруппированные страницы
        context.user_data["meetups_session_pages"] = [[dict(s) for s in page] for page in session_pages]
        context.user_data["meetups_session_index"] = 0

        # Сохраняем информацию о зале (адрес)
        gym_info = {}
        if gym_name not in ("other", "free"):
            # Ищем адрес в списках залов
            for gym in GYMS_SPB + GYMS_MSK:
                if gym[0] == gym_name and len(gym) > 2:
                    gym_info['address'] = gym[2]
                    break
        context.user_data["meetup_gym_info"] = gym_info

        # Показываем карточку тренировки (через новый механизм)
        await show_session_card(update, context, 0, edit=edit)

    except Exception as e:
        print(f"❌ Ошибка show_meetup_gym_by_index: {e}")


async def show_gym_list(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    """Показывает список залов для выбора (inline кнопки)"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    query = update.callback_query
    message = query.message if query else update.effective_message

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = row['city'] if row else None

            today = datetime.now().date()

            # === Подсчёт участников по залам ===
            gym_participants = {}

            gym_counts = await conn.fetch("""
                SELECT gs.gym_name, COUNT(DISTINCT gsp.user_id) as cnt
                FROM gym_sessions gs
                JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                WHERE gs.session_date >= $1 AND gs.gym_name IS NOT NULL
                GROUP BY gs.gym_name
            """, today)

            board_counts = await conn.fetch("""
                SELECT bs.gym_name, COUNT(DISTINCT bsp.user_id) as cnt
                FROM board_sessions bs
                JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.session_date >= $1 AND bs.gym_name IS NOT NULL AND bs.status = 'active'
                GROUP BY bs.gym_name
            """, today)

            for row in gym_counts:
                if row['gym_name']:
                    gym_participants[row['gym_name']] = row['cnt']
            for row in board_counts:
                if row['gym_name']:
                    gym_participants[row['gym_name']] = gym_participants.get(row['gym_name'], 0) + row['cnt']

            # Подсчёт для "Другая локация" — только по городу пользователя
            known_gyms = set(g[0] for g in GYMS_SPB + GYMS_MSK)

            # Определяем city_key пользователя
            user_city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    user_city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    user_city_key = "msk"
                else:
                    user_city_key = user_city

            # Считаем только кастомные локации в городе пользователя
            other_location_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT bsp.user_id)
                FROM board_sessions bs
                JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.session_date >= $1 
                  AND bs.status = 'active'
                  AND bs.city_key = $2
                  AND (bs.gym_name IS NULL OR bs.gym_name NOT IN (SELECT unnest($3::text[])))
            """, today, user_city_key, list(known_gyms)) or 0

            # Считаем только кастомные локации в городе пользователя
            other_location_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT bsp.user_id)
                FROM board_sessions bs
                JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.session_date >= $1 
                  AND bs.status = 'active'
                  AND bs.city_key = $2
                  AND (bs.gym_name IS NULL OR bs.gym_name NOT IN (SELECT unnest($3::text[])))
            """, today, user_city_key, list(known_gyms)) or 0

            # Подсчёт для "Свободная тренировка"
            free_training_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT gsp.user_id)
                FROM gym_sessions gs
                JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                WHERE gs.session_date >= $1 AND gs.gym_name IS NULL
            """, today) or 0

        # Формируем inline клавиатуру с залами
        inline_keyboard = []

        if user_city and ("Петербург" in user_city or "Petersburg" in user_city):
            for i in range(0, len(GYMS_SPB), 2):
                row_btns = []
                for gym in GYMS_SPB[i:i+2]:
                    gym_name = gym[0]
                    count = gym_participants.get(gym_name, 0)

                    if count > 0:
                        gym_label = f"{gym_name} · {count} 👤"
                    else:
                        gym_label = gym_name

                    row_btns.append(InlineKeyboardButton(gym_label, callback_data=f"meetup_gym_{gym_name}"))
                inline_keyboard.append(row_btns)

            # Другая локация с количеством
            other_label = TEXT2[lang]["meetups_other_location"]
            if other_location_count > 0:
                other_label = f"{other_label} · {other_location_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(other_label, callback_data="meetup_gym_other")])

        elif user_city and ("Москва" in user_city or "Moscow" in user_city):
            for i in range(0, len(GYMS_MSK), 2):
                row_btns = []
                for gym in GYMS_MSK[i:i+2]:
                    gym_name = gym[0]
                    count = gym_participants.get(gym_name, 0)

                    if count > 0:
                        gym_label = f"{gym_name} · {count} 👤"
                    else:
                        gym_label = gym_name

                    row_btns.append(InlineKeyboardButton(gym_label, callback_data=f"meetup_gym_{gym_name}"))
                inline_keyboard.append(row_btns)

            # Другая локация с количеством
            other_label = TEXT2[lang]["meetups_other_location"]
            if other_location_count > 0:
                other_label = f"{other_label} · {other_location_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(other_label, callback_data="meetup_gym_other")])

        else:
            # Другие города — свободная тренировка + другая локация
            free_label = TEXT2[lang]["meetups_free_training"]
            if free_training_count > 0:
                free_label = f"{free_label} · {free_training_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(free_label, callback_data="meetup_gym_free")])

            # Добавляем кнопку "Другая локация" с количеством
            other_label = TEXT2[lang]["meetups_other_location"]
            if other_location_count > 0:
                other_label = f"{other_label} · {other_location_count} 👤"
            inline_keyboard.append([InlineKeyboardButton(other_label, callback_data="meetup_gym_other")])

        if edit and message:
            has_photo = bool(message.photo)
            if has_photo:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=TEXT2[lang]["meetups_choose_gym"],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard)
                )
                try:
                    await message.delete()
                except:
                    pass
            else:
                await message.edit_text(
                    text=TEXT2[lang]["meetups_choose_gym"],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard)
                )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=TEXT2[lang]["meetups_choose_gym"],
                reply_markup=InlineKeyboardMarkup(inline_keyboard)
            )

    except Exception as e:
        print(f"❌ Ошибка show_gym_list: {e}")
        
async def show_session_card(update: Update, context: ContextTypes.DEFAULT_TYPE, session_index: int, edit: bool = False):
    """Показывает карточку зала с тренировками (одна или несколько на странице)"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    query = update.callback_query
    message = query.message if query else update.effective_message

    try:
        session_pages = context.user_data.get("meetups_session_pages", [])
        gym_name = context.user_data.get("meetup_selected_gym", "")
        gym_info = context.user_data.get("meetup_gym_info", {})

        if not session_pages:
            # Возвращаемся к списку залов при пустом списке тренировок
            await show_gym_list(update, context, edit=edit)
            return

        context.user_data["meetups_session_index"] = session_index

        # DEBUG: Логируем пагинацию
        print(f"🔍 DEBUG show_session_card:")
        print(f"  session_index={session_index}")
        print(f"  Всего session_pages: {len(session_pages)}")

        # Проверяем границы индекса
        if session_index < 0 or session_index >= len(session_pages):
            await show_gym_list(update, context, edit=edit)
            return

        # Получаем текущую страницу (может содержать несколько сессий)
        current_page = session_pages[session_index]
        sessions_to_show = current_page

        # Получаем реальное название зала из данных сессии
        actual_gym_name = sessions_to_show[0].get('gym_name', '')

        # Заголовок с названием зала и адресом
        # Если gym_name = "other" или "free", берем реальное название из данных сессии
        if gym_name in ("other", "free"):
            # Для кастомных локаций используем название из данных сессии
            if actual_gym_name and actual_gym_name not in ("other", "free", None, ""):
                title = f"🧗 {actual_gym_name}"
                address = ""
            else:
                title = TEXT2[lang]["meetups_today_free"]
                address = ""
        else:
            title = f"🧗 {gym_name}"
            address = gym_info.get('address', '')
            if address:
                address = f"📍 {address}"

        # Формируем текст карточки
        cards_text = f"{title}\n"
        if address:
            cards_text += f"{address}\n"

        # Получаем дату первой тренировки на странице для проверки участия
        today = datetime.now().date()
        page_session_date = sessions_to_show[0].get('session_date', today)

        # Проверяем участие пользователя в тренировках на эту дату
        async with db_pool.acquire() as conn:
            user_gym_session = await conn.fetchrow("""
                SELECT gs.id FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, page_session_date)

            user_board_session = await conn.fetchrow("""
                SELECT bs.id FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date = $2
            """, user_id, page_session_date)

        user_gym_session_id = user_gym_session['id'] if user_gym_session else None
        user_board_session_id = user_board_session['id'] if user_board_session else None

        # Обрабатываем сессии на странице
        # Если сессия с climb_type='both', разворачиваем её в две секции
        sections_to_display = []
        for session in sessions_to_show:
            climb_type = session['climb_type']

            if climb_type == 'both':
                # Разворачиваем в две секции: bouldering и lead
                sections_to_display.append({
                    **session,
                    'climb_type': 'bouldering',
                    'display_climb_type': 'bouldering'
                })
                sections_to_display.append({
                    **session,
                    'climb_type': 'lead',
                    'display_climb_type': 'lead'
                })
            else:
                sections_to_display.append({
                    **session,
                    'display_climb_type': climb_type
                })

        # Формируем текст карточки
        for section in sections_to_display:
            display_climb_type = section['display_climb_type']
            session_time = section['session_time'].strftime("%H:%M") if section['session_time'] else "19:00"
            session_date = section.get('session_date', today)
            participants = section['participants_count'] or 0

            # Тип тренировки
            if display_climb_type == "bouldering":
                type_label = TEXT2[lang]["meetups_card_bouldering"]
            else:
                type_label = TEXT2[lang]["meetups_card_lead"]

            # Формируем дату с днем недели
            if session_date == today:
                date_label = TEXT2[lang]['meetups_card_today']
            else:
                # Форматируем дату и добавляем день недели
                weekday_key = f"weekday_{session_date.strftime('%a').lower()[:3]}"
                weekday = TEXT2[lang].get(weekday_key, "")
                date_formatted = session_date.strftime("%d.%m")
                date_label = f"{date_formatted} {weekday}"

            cards_text += f"\n{type_label} · {date_label} · 🕖 {session_time}\n"
            cards_text += TEXT2[lang]["meetups_card_participants"].format(count=participants) + "\n"

        # Добавляем индикатор страницы
        total_pages = len(session_pages)
        if total_pages > 1:
            cards_text += f"\n📄 Тренировка {session_index + 1} из {total_pages}"

        # Кнопки действий - для секций на текущей странице
        keyboard = []

        for section in sections_to_display:
            session_id = section['id']
            display_climb_type = section['display_climb_type']
            session_type = section.get('session_type', 'gym')  # по умолчанию gym

            # Определяем тип для кнопки
            if display_climb_type == "bouldering":
                btn_label = f"{TEXT2[lang]['meetups_btn_join']} ({TEXT2[lang]['meetups_card_bouldering']})"
            else:
                btn_label = f"{TEXT2[lang]['meetups_btn_join']} ({TEXT2[lang]['meetups_card_lead']})"

            # Проверяем участие в зависимости от типа сессии
            is_user_in_session = False
            if session_type == 'board':
                is_user_in_session = (user_board_session_id and user_board_session_id == session_id)
                callback_prefix = "board"
            else:
                is_user_in_session = (user_gym_session_id and user_gym_session_id == session_id)
                callback_prefix = "meetup"

            if is_user_in_session:
                # Пользователь уже записан на эту тренировку
                keyboard.append([
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_chat"], callback_data=f"{callback_prefix}_chat_{session_id}"),
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_participants"], callback_data=f"{callback_prefix}_parts_{session_id}"),
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_leave"], callback_data=f"{callback_prefix}_leave_{session_id}")
                ])
            else:
                # Кнопка присоединения
                keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"{callback_prefix}_join_{session_id}")])

        # Навигация: ◀️ назад, ▶️ вперед
        nav_row = []
        nav_row.append(InlineKeyboardButton("◀️", callback_data="meetup_nav_prev"))
        # Показываем ▶️ только если это не последняя страница
        if session_index < total_pages - 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data="meetup_nav_next"))
        keyboard.append(nav_row)

        # Используем фото зала (для универсальности берем первое)
        photo_url = gym_info.get('photo_url', "https://i.postimg.cc/wjTfYn4n/Chat-GPT-Image-Jan-11-2026-08-18-43-PM.png")

        # Отправляем/редактируем сообщение
        if edit and message:
            has_photo = bool(message.photo)
            if has_photo:
                try:
                    await message.edit_caption(
                        caption=cards_text,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                except Exception as e:
                    print(f"⚠️ Edit caption failed: {e}, trying edit_media")
                    try:
                        await message.edit_media(
                            media=InputMediaPhoto(media=photo_url, caption=cards_text),
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    except:
                        pass
            else:
                # Переходим от текста к фото — удаляем и отправляем новое
                try:
                    await message.delete()
                except:
                    pass
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_url,
                    caption=cards_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            try:
                if message:
                    await message.delete()
            except:
                pass
            try:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_url,
                    caption=cards_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                print(f"❌ Send photo failed: {e}")

    except Exception as e:
        import traceback
        print(f"❌ Ошибка show_session_card: {e}")
        traceback.print_exc()


async def handle_meetup_nav_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Навигация назад: к предыдущей тренировке или к списку залов"""
    query = update.callback_query
    await query.answer()

    current_index = context.user_data.get("meetups_session_index", 0)

    # Если первая тренировка — возвращаемся к списку залов
    if current_index == 0:
        await show_gym_list(update, context, edit=True)
    else:
        # Переходим к предыдущей тренировке
        await show_session_card(update, context, current_index - 1, edit=True)


async def handle_meetup_nav_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Навигация вперёд: к следующей тренировке"""
    query = update.callback_query
    await query.answer()

    current_index = context.user_data.get("meetups_session_index", 0)
    session_pages = context.user_data.get("meetups_session_pages", [])

    # Переходим к следующей странице, если она есть
    next_index = current_index + 1
    if next_index < len(session_pages):
        await show_session_card(update, context, next_index, edit=True)


async def show_gym_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE, gym_name: str, edit: bool = False):
    """Показывает карточки тренировок зала (переиспользуемая функция)"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    query = update.callback_query
    message = query.message if query else update.effective_message

    try:
        async with db_pool.acquire() as conn:
            user_row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = user_row['city'] if user_row else "unknown"

            today = datetime.now().date()

            # Получаем сессии для этого зала
            sessions = await conn.fetch("""
                SELECT gs.id, gs.climb_type, gs.session_time, gs.is_default,
                       COUNT(gsp.user_id) AS participants_count
                FROM gym_sessions gs
                LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                WHERE gs.gym_name = $1 AND gs.session_date = $2
                GROUP BY gs.id
                ORDER BY gs.session_time
            """, gym_name if gym_name not in ("other", "free") else None, today)

            # Определяем city_key
            city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    city_key = "msk"
                else:
                    # Для других городов используем сам город как city_key
                    city_key = user_city

            # Если нет сессий — создаём дефолтные
            if not sessions and gym_name not in ("other", "free"):
                default_time = datetime.strptime("19:00", "%H:%M").time()
                tz = get_timezone_for_city(user_city)

                for climb_type in ["bouldering", "lead"]:
                    await conn.execute("""
                        INSERT INTO gym_sessions (gym_name, city_key, climb_type, session_date, session_time, is_default, timezone)
                        VALUES ($1, $2, $3, $4, $5, TRUE, $6)
                    """, gym_name, city_key, climb_type, today, default_time, tz)

                sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.gym_name = $1 AND gs.session_date = $2
                    GROUP BY gs.id
                    ORDER BY gs.session_time
                """, gym_name, today)

            # Для free/other
            if gym_name in ("other", "free") and not sessions:
                default_time = datetime.strptime("19:00", "%H:%M").time()
                tz = get_timezone_for_city(user_city)

                for climb_type in ["bouldering", "lead"]:
                    await conn.execute("""
                        INSERT INTO gym_sessions (gym_name, city_key, climb_type, session_date, session_time, is_default, timezone)
                        VALUES (NULL, $1, $2, $3, $4, TRUE, $5)
                    """, city_key, climb_type, today, default_time, tz)

                sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.city_key = $1 AND gs.gym_name IS NULL AND gs.session_date = $2
                    GROUP BY gs.id
                    ORDER BY gs.session_time
                """, city_key, today)

            # Проверяем участие пользователя
            user_session = await conn.fetchrow("""
                SELECT gs.id, gs.climb_type, gs.gym_name, gs.session_time
                FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, today)

        # Формируем заголовок
        if gym_name in ("other", "free"):
            title = TEXT2[lang]["meetups_today_free"]
        else:
            title = TEXT2[lang]["meetups_today_at_gym"].format(gym_name=gym_name)

        # Формируем карточки
        cards_text = f"{title}\n\n"
        keyboard = []

        for session in sessions:
            session_id = session['id']
            climb_type = session['climb_type']
            session_time = session['session_time'].strftime("%H:%M") if session['session_time'] else "19:00"
            participants = session['participants_count'] or 0

            if climb_type == "bouldering":
                type_label = TEXT2[lang]["meetups_card_bouldering"]
            else:
                type_label = TEXT2[lang]["meetups_card_lead"]

            cards_text += f"{type_label} · {TEXT2[lang]['meetups_card_today']} · ~{session_time}\n"
            cards_text += TEXT2[lang]["meetups_card_participants"].format(count=participants) + "\n\n"

            if user_session and user_session['id'] == session_id:
                keyboard.append([
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_chat"], callback_data=f"meetup_chat_{session_id}_board"),
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_participants"], callback_data=f"meetup_parts_{session_id}"),
                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_leave"], callback_data=f"meetup_leave_{session_id}")
                ])
            else:
                keyboard.append([InlineKeyboardButton(
                    f"{TEXT2[lang]['meetups_btn_join']} ({type_label})",
                    callback_data=f"meetup_join_{session_id}"
                )])

        # Добавляем индикатор страницы и навигацию
        current_index = context.user_data.get("meetups_gym_index", 0)

        # Подсчитываем общее количество залов + кастомных тренировок
        gyms_list = context.user_data.get("meetups_gyms_list", [gym_name])
        total_pages = len(gyms_list)

        # Добавляем счётчик страниц в текст
        if total_pages > 1:
            cards_text += f"\n📍 Зал {current_index + 1} из {total_pages}"

        # Навигация: ◀️ назад, ▶️ следующий зал
        nav_row = []
        nav_row.append(InlineKeyboardButton("◀️", callback_data="meetup_nav_prev"))
        if total_pages > 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data="meetup_nav_next"))
        keyboard.append(nav_row)

        # Выбираем картинку
        if sessions and sessions[0]['climb_type'] == "bouldering":
            photo_url = "https://postimg.cc/qN0BBrzV"
        else:
            photo_url = "https://postimg.cc/5YPbnQmG"

        if edit and message:
            has_photo = bool(message and message.photo)
            if has_photo:
                await message.edit_caption(caption=cards_text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                try:
                    await message.delete()
                except:
                    pass
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_url,
                    caption=cards_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            try:
                if message:
                    await message.delete()
            except:
                pass
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo_url,
                caption=cards_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        print(f"❌ Ошибка show_gym_sessions: {e}")
        try:
            await context.bot.send_message(chat_id=user_id, text="⚠️ Ошибка загрузки тренировок")
        except:
            pass


async def handle_meetup_gym_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора зала — загрузка тренировок и показ первой карточки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    gym_name = query.data.replace("meetup_gym_", "")
    context.user_data["meetup_selected_gym"] = gym_name

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = row['city'] if row else "unknown"

            today = datetime.now().date()

            # Определяем city_key
            city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    city_key = "msk"
                else:
                    # Для других городов используем сам город как city_key
                    city_key = user_city

            # Получаем gym_sessions для этого зала (все будущие и сегодняшние)
            if gym_name in ("other", "free"):
                gym_sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count,
                           'gym' as session_type
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.city_key = $1 AND gs.gym_name IS NULL AND gs.session_date >= $2
                    GROUP BY gs.id
                    ORDER BY gs.session_date, gs.session_time
                """, city_key, today)

                gym_sessions = list(gym_sessions)

                # Если нет gym_sessions — создаём дефолтные
                if not gym_sessions:
                    default_time = datetime.strptime("19:00", "%H:%M").time()
                    tz = get_timezone_for_city(user_city)

                    # Определяем типы тренировок для этого зала
                    gym_climb_type = get_gym_climb_type(gym_name)
                    if gym_climb_type == "bouldering":
                        climb_types_to_create = ["bouldering"]
                    else:
                        climb_types_to_create = ["bouldering", "lead"]

                    for climb_type in climb_types_to_create:
                        await conn.execute("""
                            INSERT INTO gym_sessions (gym_name, city_key, climb_type, session_date, session_time, is_default, timezone)
                            VALUES ($1, $2, $3, $4, $5, TRUE, $6)
                        """, None, city_key, climb_type, today, default_time, tz)

                    gym_sessions = await conn.fetch("""
                        SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                               COUNT(gsp.user_id) AS participants_count,
                               'gym' as session_type
                        FROM gym_sessions gs
                        LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                        WHERE gs.city_key = $1 AND gs.gym_name IS NULL AND gs.session_date >= $2
                        GROUP BY gs.id
                        ORDER BY gs.session_date, gs.session_time
                    """, city_key, today)
                    gym_sessions = list(gym_sessions)
            else:
                gym_sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count,
                           'gym' as session_type
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.gym_name = $1 AND gs.session_date >= $2
                    GROUP BY gs.id
                    ORDER BY gs.session_date, gs.session_time
                """, gym_name, today)

                gym_sessions = list(gym_sessions)

                # Если нет gym_sessions — создаём дефолтные
                if not gym_sessions:
                    default_time = datetime.strptime("19:00", "%H:%M").time()
                    tz = get_timezone_for_city(user_city)

                    # Определяем типы тренировок для этого зала
                    gym_climb_type = get_gym_climb_type(gym_name)
                    if gym_climb_type == "bouldering":
                        climb_types_to_create = ["bouldering"]
                    else:
                        climb_types_to_create = ["bouldering", "lead"]

                    for climb_type in climb_types_to_create:
                        await conn.execute("""
                            INSERT INTO gym_sessions (gym_name, city_key, climb_type, session_date, session_time, is_default, timezone)
                            VALUES ($1, $2, $3, $4, $5, TRUE, $6)
                        """, gym_name, city_key, climb_type, today, default_time, tz)

                    gym_sessions = await conn.fetch("""
                        SELECT gs.id, gs.climb_type, gs.session_time, gs.session_date, gs.is_default,
                               COUNT(gsp.user_id) AS participants_count,
                               'gym' as session_type
                        FROM gym_sessions gs
                        LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                        WHERE gs.gym_name = $1 AND gs.session_date >= $2
                        GROUP BY gs.id
                        ORDER BY gs.session_date, gs.session_time
                    """, gym_name, today)
                    gym_sessions = list(gym_sessions)

            # Загружаем board_sessions для этого зала
            if gym_name in ("other", "free"):
                board_sessions = await conn.fetch("""
                    SELECT bs.id, bs.climb_type, bs.session_time, bs.session_date,
                           FALSE as is_default,
                           COUNT(bsp.user_id) AS participants_count,
                           'board' as session_type
                    FROM board_sessions bs
                    LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    WHERE bs.city_key = $1 AND bs.gym_name IS NULL
                      AND bs.session_date >= $2 AND bs.status = 'active'
                    GROUP BY bs.id
                    ORDER BY bs.session_date, bs.session_time
                """, city_key, today)
            else:
                board_sessions = await conn.fetch("""
                    SELECT bs.id, bs.climb_type, bs.session_time, bs.session_date,
                           FALSE as is_default,
                           COUNT(bsp.user_id) AS participants_count,
                           'board' as session_type
                    FROM board_sessions bs
                    LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    WHERE bs.gym_name = $1
                      AND bs.session_date >= $2 AND bs.status = 'active'
                    GROUP BY bs.id
                    ORDER BY bs.session_date, bs.session_time
                """, gym_name, today)

            # Объединяем gym_sessions и board_sessions
            all_sessions = gym_sessions + list(board_sessions)

            # Сортируем все сессии по дате, затем по времени
            all_sessions.sort(key=lambda s: (
                s['session_date'] if s['session_date'] else today,
                s['session_time'] if s['session_time'] else datetime.strptime("00:00", "%H:%M").time()
            ))

        # Группируем сессии для пагинации
        session_pages = group_sessions_into_pages(all_sessions, today)

        # Сохраняем сгруппированные страницы в контекст
        context.user_data["meetups_session_pages"] = [[dict(s) for s in page] for page in session_pages]
        context.user_data["meetups_session_index"] = 0

        # Сохраняем информацию о зале (адрес)
        gym_info = {}
        if gym_name not in ("other", "free"):
            # Ищем адрес в списках залов
            for gym in GYMS_SPB + GYMS_MSK:
                if gym[0] == gym_name and len(gym) > 2:
                    gym_info['address'] = gym[2]
                    break
        context.user_data["meetup_gym_info"] = gym_info

        # Показываем первую карточку тренировки
        await show_session_card(update, context, 0, edit=False)

    except Exception as e:
        import traceback
        print(f"❌ Ошибка handle_meetup_gym_selection: {e}")
        traceback.print_exc()
        await context.bot.send_message(chat_id=user_id, text="⚠️ Ошибка загрузки тренировок")


async def handle_meetup_other_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора 'Другая локация' — показываем только board_sessions с кастомными локациями"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    context.user_data["meetup_selected_gym"] = "other"

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = row['city'] if row else "unknown"

            today = datetime.now().date()

            # Определяем city_key
            city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    city_key = "msk"
                else:
                    # Для других городов используем сам город как city_key
                    city_key = user_city

            # Получаем список известных залов
            known_gyms = set()
            for gym in GYMS_SPB + GYMS_MSK:
                known_gyms.add(gym[0])

            # Загружаем только board_sessions с кастомными локациями
            # (gym_name не NULL и не входит в список известных залов)
            board_sessions = await conn.fetch("""
                SELECT bs.id, bs.gym_name, bs.climb_type, bs.session_time, bs.session_date,
                       FALSE as is_default,
                       COUNT(bsp.user_id) AS participants_count,
                       'board' as session_type
                FROM board_sessions bs
                LEFT JOIN board_session_participants bsp ON bs.id = bsp.session_id
                WHERE bs.city_key = $1
                  AND bs.gym_name IS NOT NULL
                  AND bs.session_date >= $2
                  AND bs.status = 'active'
                GROUP BY bs.id, bs.gym_name
                ORDER BY bs.session_date, bs.session_time
            """, city_key, today)

            # Фильтруем: оставляем только те, где gym_name не в списке известных залов
            custom_sessions = [s for s in board_sessions if s['gym_name'] not in known_gyms]

            if not custom_sessions:
                # Нет тренировок в других локациях - показываем сообщение с кнопкой создания
                keyboard = [[InlineKeyboardButton(
                    TEXT2[lang].get("board_create_btn", "✏️ Создать объявление"),
                    callback_data="board_create_start"
                )]]

                try:
                    await query.message.delete()
                except:
                    pass

                await context.bot.send_message(
                    chat_id=user_id,
                    text=TEXT2[lang].get("meetups_other_empty",
                        "📭 На данный момент никто не создал объявление о тренировке в другой локации.\n\n"
                        "Хочешь позвать на тренировку?"),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return

            # Группируем сессии для пагинации (кастомные = по одной на страницу)
            session_pages = []
            for session in custom_sessions:
                session_dict = dict(session)
                session_pages.append([session_dict])

            # Сохраняем в контекст
            context.user_data["meetups_session_pages"] = session_pages
            context.user_data["meetups_session_index"] = 0
            context.user_data["meetup_gym_info"] = {}

            # Показываем первую карточку тренировки
            await show_session_card(update, context, 0, edit=False)

    except Exception as e:
        import traceback
        print(f"❌ Ошибка handle_meetup_other_location: {e}")
        traceback.print_exc()
        await context.bot.send_message(chat_id=user_id, text="⚠️ Ошибка загрузки тренировок")


async def handle_board_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса создания board через inline-кнопку"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Удаляем предыдущее сообщение
    try:
        await query.message.delete()
    except:
        pass

    # Инициализируем процесс создания board (аналогично board_create)
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    buttons = [[
        InlineKeyboardButton(TEXT2[lang]["board_date_today"].format(
            date=today.strftime("%d.%m (%a)")), callback_data="board_date_today")
    ], [
        InlineKeyboardButton(TEXT2[lang]["board_date_tomorrow"].format(
            date=tomorrow.strftime("%d.%m (%a)")), callback_data="board_date_tomorrow")
    ], [
        InlineKeyboardButton(TEXT2[lang]["board_date_custom"],
                             callback_data="board_date_custom")
    ]]

    context.user_data["board"] = {}
    context.user_data["awaiting_board_date"] = True

    await context.bot.send_message(
        chat_id=user_id,
        text=TEXT2[lang]["board_create_intro"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_meetup_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вступление в тренировку — сначала спрашиваем уровень"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("meetup_join_", ""))
    context.user_data["meetup_joining_session"] = session_id

    try:
        async with db_pool.acquire() as conn:
            # Получаем дату сессии, на которую пользователь хочет записаться
            target_session = await conn.fetchrow("""
                SELECT session_date FROM gym_sessions WHERE id = $1
            """, session_id)

            if not target_session:
                await query.message.reply_text("Ошибка: тренировка не найдена")
                return

            target_date = target_session['session_date']

            # Проверяем, не участвует ли уже в тренировке на эту дату
            # Проверяем и кастомные (board_sessions), и дефолтные (gym_sessions) тренировки
            existing_gym = await conn.fetchrow("""
                SELECT gs.id FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, target_date)

            existing_board = await conn.fetchrow("""
                SELECT bs.id FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date = $2
            """, user_id, target_date)

            if existing_gym or existing_board:
                await query.message.reply_text(TEXT2[lang]["meetups_already_joined"])
                return

            # Берём уровень из профиля
            user_row = await conn.fetchrow("SELECT difficulty FROM users WHERE user_id = $1", user_id)
            user_difficulty = user_row['difficulty'] if user_row else None

        # Если уровень есть — сразу вступаем
        if user_difficulty:
            await complete_meetup_join(update, context, session_id, user_difficulty, has_level_dialog=False)
        else:
            # Спрашиваем уровень - сохраняем ID карточки для последующего удаления
            context.user_data["meetup_card_message_id"] = query.message.message_id
            keyboard = get_difficulty_range_keyboard(lang, prefix="meetup_level_")
            await query.message.reply_text(
                TEXT2[lang]["meetups_pick_level"],
                reply_markup=keyboard
            )
    except Exception as e:
        print(f"❌ Ошибка handle_meetup_join: {e}")


async def handle_meetup_level_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор уровня при вступлении"""
    query = update.callback_query
    await query.answer()

    level = query.data.replace("meetup_level_", "")
    if level == "skip":
        level = None

    session_id = context.user_data.get("meetup_joining_session")
    if not session_id:
        return

    await complete_meetup_join(update, context, session_id, level, has_level_dialog=True)


async def build_session_card_text(conn, session_id: int, user_id: int, lang: str) -> tuple:
    """Формирует текст карточки сессии и клавиатуру (единый формат)"""
    session = await conn.fetchrow("""
        SELECT gs.*, COUNT(gsp.user_id) AS participants_count
        FROM gym_sessions gs
        LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
        WHERE gs.id = $1
        GROUP BY gs.id
    """, session_id)

    if not session:
        return None, None, None

    # Получаем участников с уровнями
    participants = await conn.fetch("""
        SELECT u.name, gsp.difficulty
        FROM gym_session_participants gsp
        JOIN users u ON gsp.user_id = u.user_id
        WHERE gsp.session_id = $1
        ORDER BY gsp.joined_at
    """, session_id)

    # Проверяем участие пользователя
    is_participant = await conn.fetchval("""
        SELECT 1 FROM gym_session_participants WHERE session_id = $1 AND user_id = $2
    """, session_id, user_id)

    climb_type = session['climb_type']
    session_time = session['session_time'].strftime("%H:%M") if session['session_time'] else "19:00"
    gym_name = session['gym_name'] or TEXT2[lang].get("meetups_today_free", "🏟 Договариваемся о локации в чате")

    # Формируем заголовок карточки
    if climb_type == "bouldering":
        type_label = TEXT2[lang]["meetups_card_bouldering"]
    else:
        type_label = TEXT2[lang]["meetups_card_lead"]

    text = f"{type_label} · {TEXT2[lang]['meetups_card_today']} · ~{session_time}\n"
    text += f"🏟 {gym_name}\n\n"

    # Список участников с уровнями
    if participants:
        text += TEXT2[lang].get("meetups_participants_list", "👥 Участники:") + "\n"
        for p in participants:
            diff = f" ({p['difficulty']})" if p['difficulty'] else ""
            text += f"• {p['name']}{diff}\n"
    else:
        text += TEXT2[lang].get("meetups_no_participants_yet", "👥 Пока никого нет") + "\n"

    # Кнопки
    keyboard = []
    if is_participant:
        keyboard.append([
            InlineKeyboardButton(TEXT2[lang]["meetups_btn_chat"], callback_data=f"meetup_chat_{session_id}_board"),
            InlineKeyboardButton(TEXT2[lang]["meetups_btn_participants"], callback_data=f"meetup_parts_{session_id}"),
            InlineKeyboardButton(TEXT2[lang]["meetups_btn_leave"], callback_data=f"meetup_leave_{session_id}")
        ])
    else:
        keyboard.append([InlineKeyboardButton(
            TEXT2[lang]['meetups_btn_join'],
            callback_data=f"meetup_join_{session_id}"
        )])

    keyboard.append([InlineKeyboardButton("◀", callback_data=f"meetup_gym_{session['gym_name'] or 'free'}")])

    return text, InlineKeyboardMarkup(keyboard), climb_type


async def handle_meetup_back_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к карточке сессии (из участников)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Сбрасываем режим группового чата
    context.user_data["current_group_chat_session"] = None
    context.user_data["awaiting"] = None

    # Перезагружаем список сессий с актуальным количеством участников
    gym_name = context.user_data.get("meetup_selected_gym", "")

    try:
        async with db_pool.acquire() as conn:
            today = datetime.now().date()

            # Получаем city_key
            user_row = await conn.fetchrow("SELECT city FROM users WHERE user_id = $1", user_id)
            user_city = user_row['city'] if user_row else "unknown"
            city_key = None
            if user_city:
                if "Петербург" in user_city or "Petersburg" in user_city:
                    city_key = "spb"
                elif "Москва" in user_city or "Moscow" in user_city:
                    city_key = "msk"

            # Получаем обновлённые сессии
            if gym_name in ("other", "free"):
                sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.city_key = $1 AND gs.gym_name IS NULL AND gs.session_date = $2
                    GROUP BY gs.id
                    ORDER BY gs.session_time
                """, city_key, today)
            else:
                sessions = await conn.fetch("""
                    SELECT gs.id, gs.climb_type, gs.session_time, gs.is_default,
                           COUNT(gsp.user_id) AS participants_count
                    FROM gym_sessions gs
                    LEFT JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    WHERE gs.gym_name = $1 AND gs.session_date = $2
                    GROUP BY gs.id
                    ORDER BY gs.session_time
                """, gym_name, today)

            # Обновляем список в контексте
            context.user_data["meetups_sessions_list"] = [dict(s) for s in sessions]
    except Exception as e:
        print(f"❌ Ошибка handle_meetup_back_session: {e}")

    # Возвращаемся к той же странице (индексу), которая была открыта
    session_index = context.user_data.get("meetups_session_index", 0)
    await show_session_card(update, context, session_index, edit=True)


async def complete_meetup_join(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: int, difficulty: str, has_level_dialog: bool = False):
    """Завершение вступления в тренировку"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    query = update.callback_query

    try:
        async with db_pool.acquire() as conn:
            # Добавляем участника
            await conn.execute("""
                INSERT INTO gym_session_participants (session_id, user_id, difficulty)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
            """, session_id, user_id, difficulty)

            # 🎁 Награда за вступление — 1г магнезии (раз в день)
            today = datetime.now().date()
            already_rewarded_today = await conn.fetchval("""
                SELECT 1 FROM magnesium_log 
                WHERE user_id = $1 
                  AND reason = 'join_training'
                  AND timestamp::date = $2
            """, user_id, today)

            if not already_rewarded_today:
                await add_magnesium(user_id, 1, "join_training")
                balance = await get_magnesium(user_id)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=TEXT2[lang].get("magnesium_join_gift", 
                        "🎁 +1г магнезии за запись на тренировку!\nБаланс: {balance}г").format(balance=balance)
                )

            # Пуш для малых городов при вступлении
            user_row = await conn.fetchrow("SELECT city, city_other FROM users WHERE user_id = $1", user_id)
            if user_row:
                push_city = user_row['city_other'] if user_row['city'] == "Другой" else user_row['city']
                if push_city:
                    await send_board_push_if_needed(context, push_city, exclude_user_id=user_id)

            # Создаём групповой чат если его нет
            chat_row = await conn.fetchrow("SELECT id FROM group_chats WHERE session_id = $1", session_id)
            if not chat_row:
                session_row = await conn.fetchrow("SELECT session_date FROM gym_sessions WHERE id = $1", session_id)
                chat_name = f"🧗 {session_row['session_date'].strftime('%d.%m.%y')}" if session_row else "🧗 Тренировка"
                chat_row = await conn.fetchrow("""
                    INSERT INTO group_chats (session_id, chat_name)
                    VALUES ($1, $2)
                    RETURNING id
                """, session_id, chat_name)

            chat_id = chat_row['id']

            # Добавляем в meetup_chat_members (ИЗОЛИРОВАННАЯ система для активных чатов)
            await conn.execute("""
                INSERT INTO meetup_chat_members (user_id, chat_id, session_id, is_active)
                VALUES ($1, $2, $3, TRUE)
                ON CONFLICT (user_id, chat_id) DO UPDATE SET is_active = TRUE, joined_at = NOW()
            """, user_id, chat_id, session_id)

            # Добавляем/обновляем активность чата
            await conn.execute("""
                INSERT INTO meetup_chat_activity (chat_id, session_id, last_message_ts)
                VALUES ($1, $2, NOW())
                ON CONFLICT (chat_id) DO NOTHING
            """, chat_id, session_id)

            # Перезагружаем список сессий с обновлённым количеством участников
            gym_name = context.user_data.get("meetup_selected_gym", "")
            session_pages = await reload_gym_sessions(conn, gym_name, user_id)

            # Обновляем в контексте
            context.user_data["meetups_session_pages"] = [[dict(s) for s in page] for page in session_pages]

        # Если был диалог выбора уровня, удаляем только сообщение с выбором уровня
        if has_level_dialog:
            # Удаляем сообщение с выбором уровня
            try:
                if query and query.message:
                    await query.message.delete()
            except:
                pass

            # Получаем ID карточки для редактирования
            card_message_id = context.user_data.get("meetup_card_message_id")
            context.user_data.pop("meetup_card_message_id", None)

            # Плавное обновление карточки на месте
            # Редактируем карточку напрямую через bot API
            current_index = context.user_data.get("meetups_session_index", 0)

            if card_message_id:
                # Формируем обновлённую карточку
                try:
                    session_pages = context.user_data.get("meetups_session_pages", [])
                    gym_info = context.user_data.get("meetup_gym_info", {})

                    if session_pages and current_index < len(session_pages):
                        current_page = session_pages[current_index]
                        gym_name = context.user_data.get("meetup_selected_gym", "")

                        # Формируем текст и клавиатуру как в show_session_card
                        # (упрощённая версия для плавного обновления)
                        sessions_to_show = current_page

                        # Заголовок
                        actual_gym_name = sessions_to_show[0].get('gym_name', '')
                        if gym_name in ("other", "free"):
                            if actual_gym_name and actual_gym_name not in ("other", "free", None, ""):
                                title = f"🧗 {actual_gym_name}"
                                address = ""
                            else:
                                title = TEXT2[lang]["meetups_today_free"]
                                address = ""
                        else:
                            title = f"🧗 {gym_name}"
                            address = gym_info.get('address', '')
                            if address:
                                address = f"📍 {address}"

                        cards_text = f"{title}\n"
                        if address:
                            cards_text += f"{address}\n"

                        # Получаем дату страницы для проверки участия
                        today = datetime.now().date()
                        page_session_date = sessions_to_show[0].get('session_date', today)

                        # Проверяем участие пользователя в тренировках на эту дату
                        async with db_pool.acquire() as conn:
                            user_gym_session = await conn.fetchrow("""
                                SELECT gs.id FROM gym_session_participants gsp
                                JOIN gym_sessions gs ON gsp.session_id = gs.id
                                WHERE gsp.user_id = $1 AND gs.session_date = $2
                            """, user_id, page_session_date)

                            user_board_session = await conn.fetchrow("""
                                SELECT bs.id FROM board_session_participants bsp
                                JOIN board_sessions bs ON bsp.session_id = bs.id
                                WHERE bsp.user_id = $1 AND bs.session_date = $2
                            """, user_id, page_session_date)

                        user_gym_session_id = user_gym_session['id'] if user_gym_session else None
                        user_board_session_id = user_board_session['id'] if user_board_session else None

                        # Разворачиваем секции для отображения (как в show_session_card)
                        sections_to_display = []
                        for session in sessions_to_show:
                            climb_type = session['climb_type']
                            if climb_type == 'both':
                                sections_to_display.append({**session, 'climb_type': 'bouldering', 'display_climb_type': 'bouldering'})
                                sections_to_display.append({**session, 'climb_type': 'lead', 'display_climb_type': 'lead'})
                            else:
                                sections_to_display.append({**session, 'display_climb_type': climb_type})

                        # Формируем карточку
                        for section in sections_to_display:
                            display_climb_type = section['display_climb_type']
                            session_time = section['session_time'].strftime("%H:%M") if section.get('session_time') else "19:00"
                            participants = section.get('participants_count', 0)

                            if display_climb_type == "bouldering":
                                type_label = TEXT2[lang]["meetups_card_bouldering"]
                            else:
                                type_label = TEXT2[lang]["meetups_card_lead"]

                            session_date = section.get('session_date', today)
                            if session_date == today:
                                date_label = TEXT2[lang]['meetups_card_today']
                            else:
                                weekday_key = f"weekday_{session_date.strftime('%a').lower()[:3]}"
                                weekday = TEXT2[lang].get(weekday_key, "")
                                date_formatted = session_date.strftime("%d.%m")
                                date_label = f"{date_formatted} {weekday}"

                            cards_text += f"\n{type_label} · {date_label} · 🕖 {session_time}\n"
                            cards_text += TEXT2[lang]["meetups_card_participants"].format(count=participants) + "\n"

                        # Формируем кнопки для секций на странице
                        keyboard = []
                        for section in sections_to_display:
                            section_session_id = section['id']
                            display_climb_type = section['display_climb_type']
                            session_type = section.get('session_type', 'gym')

                            # Определяем префикс для callback
                            callback_prefix = "board" if session_type == 'board' else "meetup"

                            # Проверяем участие
                            is_user_in_session = False
                            if session_type == 'board':
                                is_user_in_session = (user_board_session_id and user_board_session_id == section_session_id)
                            else:
                                is_user_in_session = (user_gym_session_id and user_gym_session_id == section_session_id)

                            if is_user_in_session:
                                # Участник записан - показываем чат, участники, выйти
                                keyboard.append([
                                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_chat"], callback_data=f"{callback_prefix}_chat_{section_session_id}"),
                                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_participants"], callback_data=f"{callback_prefix}_parts_{section_session_id}"),
                                    InlineKeyboardButton(TEXT2[lang]["meetups_btn_leave"], callback_data=f"{callback_prefix}_leave_{section_session_id}")
                                ])
                            else:
                                # Кнопка присоединения
                                if display_climb_type == "bouldering":
                                    btn_label = f"{TEXT2[lang]['meetups_btn_join']} ({TEXT2[lang]['meetups_card_bouldering']})"
                                else:
                                    btn_label = f"{TEXT2[lang]['meetups_btn_join']} ({TEXT2[lang]['meetups_card_lead']})"
                                keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"{callback_prefix}_join_{section_session_id}")])

                        # Навигация
                        nav_row = []
                        nav_row.append(InlineKeyboardButton("◀️", callback_data="meetup_nav_prev"))
                        total_pages = len(session_pages)
                        if current_index < total_pages - 1:
                            nav_row.append(InlineKeyboardButton("▶️", callback_data="meetup_nav_next"))
                        keyboard.append(nav_row)

                        # Редактируем карточку
                        await context.bot.edit_message_caption(
                            chat_id=user_id,
                            message_id=card_message_id,
                            caption=cards_text,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    else:
                        # Если нет данных - показываем новую карточку
                        await show_session_card(update, context, current_index, edit=False)
                except Exception as e:
                    print(f"❌ Ошибка при плавном обновлении карточки: {e}")
                    # Fallback: показываем новую карточку
                    await show_session_card(update, context, current_index, edit=False)
            else:
                # Если нет сохранённого message_id - показываем новую карточку
                await show_session_card(update, context, current_index, edit=False)
        else:
            # Плавный UX: редактируем текущую карточку с обновлёнными данными
            current_index = context.user_data.get("meetups_session_index", 0)
            await show_session_card(update, context, current_index, edit=True)

    except Exception as e:
        print(f"❌ Ошибка complete_meetup_join: {e}")


async def handle_meetup_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выход из тренировки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("meetup_leave_", ""))
    gym_name = context.user_data.get("meetup_selected_gym", "free")

    # Проверяем, находимся ли в режиме board_my
    is_board_my_mode = "board_my_session_pages" in context.user_data

    try:
        async with db_pool.acquire() as conn:
            # Удаляем участника
            await conn.execute("""
                DELETE FROM gym_session_participants
                WHERE session_id = $1 AND user_id = $2
            """, session_id, user_id)

            # Удаляем из meetup_chat_members (выход из группового чата)
            chat_row = await conn.fetchrow("SELECT id FROM group_chats WHERE session_id = $1", session_id)
            if chat_row:
                await conn.execute("""
                    UPDATE meetup_chat_members SET is_active = FALSE
                    WHERE chat_id = $1 AND user_id = $2
                """, chat_row['id'], user_id)

            # Проверяем, остались ли участники
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM gym_session_participants WHERE session_id = $1
            """, session_id)

            # Если это кастомная сессия и нет участников — удаляем
            session_row = await conn.fetchrow("SELECT is_default, created_by, gym_name FROM gym_sessions WHERE id = $1", session_id)
            if session_row and not session_row['is_default'] and count == 0:
                await conn.execute("DELETE FROM gym_sessions WHERE id = $1", session_id)
                await conn.execute("DELETE FROM group_chats WHERE session_id = $1", session_id)
                await conn.execute("DELETE FROM meetup_chat_members WHERE session_id = $1", session_id)
                await conn.execute("DELETE FROM meetup_chat_activity WHERE session_id = $1", session_id)

            gym_name = session_row['gym_name'] if session_row and session_row['gym_name'] else gym_name

            if is_board_my_mode:
                # Режим board_my: перезагружаем список тренировок пользователя
                today = datetime.now().date()
                all_sessions = await conn.fetch("""
                    SELECT
                        gs.id, gs.gym_name, gs.climb_type, gs.session_date, gs.session_time,
                        'gym' AS session_type,
                        COUNT(gsp2.user_id) AS participants_count
                    FROM gym_sessions gs
                    JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    LEFT JOIN gym_session_participants gsp2 ON gs.id = gsp2.session_id
                    WHERE gsp.user_id = $1 AND gs.session_date >= $2
                    GROUP BY gs.id

                    UNION ALL

                    SELECT
                        bs.id, bs.gym_name, bs.climb_type, bs.session_date, bs.session_time,
                        'board' AS session_type,
                        COUNT(bsp2.user_id) AS participants_count
                    FROM board_sessions bs
                    JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    LEFT JOIN board_session_participants bsp2 ON bs.id = bsp2.session_id
                    WHERE bsp.user_id = $1 AND bs.session_date >= $2
                    GROUP BY bs.id

                    ORDER BY session_date, session_time
                """, user_id, today)

                if not all_sessions:
                    # Список пуст - удаляем кнопки и показываем сообщение
                    try:
                        await query.message.edit_caption(
                            caption=TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."),
                            reply_markup=None
                        )
                    except:
                        try:
                            await query.message.edit_text(
                                text=TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."),
                                reply_markup=None
                            )
                        except:
                            pass
                    # Очищаем данные пагинации
                    context.user_data.pop("board_my_session_pages", None)
                    context.user_data.pop("board_my_session_index", None)
                    return

                # Формируем новые страницы пагинации
                session_pages = []
                for session in all_sessions:
                    session_dict = dict(session)
                    session_pages.append([session_dict])

                context.user_data["board_my_session_pages"] = session_pages

                # Определяем новый индекс для показа
                current_index = context.user_data.get("board_my_session_index", 0)
                new_index = min(current_index, len(session_pages) - 1)

                # Показываем карточку с корректным индексом
                await show_board_my_card(update, context, new_index, edit=True)
            else:
                # Обычный режим handle_meetups_menu: перезагружаем список тренировок зала
                session_pages = await reload_gym_sessions(conn, gym_name, user_id)
                context.user_data["meetups_session_pages"] = [[dict(s) for s in page] for page in session_pages]

                # Определяем новый индекс для показа (сохраняем текущую позицию)
                current_index = context.user_data.get("meetups_session_index", 0)
                new_index = min(current_index, len(session_pages) - 1) if session_pages else 0

                # Плавный UX: показываем карточку с сохранением текущей позиции
                await show_session_card(update, context, new_index, edit=True)

    except Exception as e:
        print(f"❌ Ошибка handle_meetup_leave: {e}")


async def handle_meetup_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ списка участников тренировки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("meetup_parts_", ""))
    context.user_data["meetup_viewing_session"] = session_id

    try:
        async with db_pool.acquire() as conn:
            participants = await conn.fetch("""
                SELECT u.user_id, u.name, gsp.difficulty
                FROM gym_session_participants gsp
                JOIN users u ON gsp.user_id = u.user_id
                WHERE gsp.session_id = $1
                ORDER BY gsp.joined_at
            """, session_id)

        # Формируем список с кнопками (profile_ паттерн для существующего хэндлера)
        keyboard = []
        if not participants:
            text = TEXT2[lang].get("meetups_no_participants", "👥 Пока никого нет")
        else:
            for p in participants:
                name = p['name']
                diff = p['difficulty'] or ""
                label = f"👤 {name} ({diff})" if diff else f"👤 {name}"
                participant_id = p['user_id']
                keyboard.append([
                    InlineKeyboardButton(label, callback_data=f"profile_{participant_id}"),
                    InlineKeyboardButton("🚫", callback_data=f"report_group_{participant_id}_{session_id}")
                ])
            text = TEXT2[lang]["meetups_participants_title"]
        keyboard.append([InlineKeyboardButton("◀️", callback_data=f"meetup_back_session_{session_id}")])

        # Плавный переход: проверяем тип сообщения
        has_photo = bool(query.message.photo)
        if has_photo:
            # Если было фото - редактируем caption
            await query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Если текстовое - просто редактируем
            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        print(f"❌ Ошибка handle_meetup_participants: {e}")

async def handle_group_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения в групповой чат (аналогично 1x1 handle_proxy_message)"""
    user_id = update.effective_user.id
    session_id = context.user_data.get("current_group_chat_session")
    is_board = context.user_data.get("current_group_chat_is_board", False)

    if not session_id:
        return False

    message_text = update.message.text if update.message and update.message.text else None
    if not message_text:
        return False

    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    # Проверка глобального бана
    async with db_pool.acquire() as conn:
        is_banned = await conn.fetchval("""
            SELECT 1 FROM hidden_users 
            WHERE user_id = 0 AND hidden_user_id = $1 
            AND (hide_until IS NULL OR hide_until > CURRENT_TIMESTAMP)
        """, user_id)

        if is_banned:
            await update.message.reply_text(
                TEXT2[lang].get("group_chat_banned", "🚫 Вы временно ограничены в отправке сообщений")
            )
            return True

    # Кнопка выхода из чата (сворачивание)
    end_chat_label = TEXTS[lang].get("btn_end_chat", "❌ Завершить")

    # Проверяем команду выхода (сворачивание чата, НЕ выход из тренировки)
    if message_text == end_chat_label:
        context.user_data["current_group_chat_session"] = None
        context.user_data["current_group_chat_id"] = None
        context.user_data["current_group_chat_is_board"] = None

        # Возвращаем в меню чатов
        menu_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(TEXTS[lang]["chats_active"])],
            [KeyboardButton(TEXTS[lang]["offline_muted"])],
            [KeyboardButton(TEXTS[lang]["chats_back"])]
        ], resize_keyboard=True)

        await update.message.reply_text(
            TEXT2[lang].get("chat_ended_self", "✅ Чат свёрнут"),
            reply_markup=menu_keyboard
        )
        return True

    try:
        async with db_pool.acquire() as conn:
            # Проверяем что сессия ещё существует
            if is_board:
                session_exists = await conn.fetchval(
                    "SELECT id FROM board_sessions WHERE id = $1 AND status = 'active'", session_id)
            else:
                session_exists = await conn.fetchval(
                    "SELECT id FROM gym_sessions WHERE id = $1", session_id)

            if not session_exists:
                context.user_data["current_group_chat_session"] = None
                context.user_data["current_group_chat_id"] = None
                context.user_data["current_group_chat_is_board"] = None
                await update.message.reply_text(TEXT2[lang].get("meetups_session_expired", "⏰ Тренировка завершена"))
                return True

            # Получаем chat_id
            chat_row = await conn.fetchrow(
                "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = $2", 
                session_id, is_board)

            if not chat_row:
                # Создаём чат
                session_info = await get_session_info(conn, session_id, is_board)
                chat_name = f"🧗 {session_info.get('gym_name', 'Тренировка')} · {session_info.get('date_str', '')}"

                await conn.execute("""
                    INSERT INTO group_chats (session_id, chat_name, is_board)
                    VALUES ($1, $2, $3)
                """, session_id, chat_name, is_board)
                chat_row = await conn.fetchrow(
                    "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = $2", 
                    session_id, is_board)

            chat_id = chat_row['id']
            chat_name = chat_row['chat_name'] or "🧗 Тренировка"

            # Сохраняем сообщение
            await conn.execute("""
                INSERT INTO group_chat_messages (chat_id, sender_id, message_text)
                VALUES ($1, $2, $3)
            """, chat_id, user_id, message_text)

            # Обновляем активность чата
            await conn.execute("""
                INSERT INTO meetup_chat_activity (chat_id, session_id, last_message_ts)
                VALUES ($1, $2, NOW())
                ON CONFLICT (chat_id) DO UPDATE SET last_message_ts = NOW()
            """, chat_id, session_id)

            # Обновляем last_read для отправителя
            await conn.execute("""
                UPDATE meetup_chat_members SET last_read_ts = NOW(), notified_once = FALSE
                WHERE user_id = $1 AND chat_id = $2
            """, user_id, chat_id)

            # Получаем участников
            participants = await conn.fetch("""
                SELECT mcm.user_id, mcm.notified_once
                FROM meetup_chat_members mcm
                WHERE mcm.chat_id = $1 AND mcm.user_id != $2 AND mcm.is_active = TRUE
            """, chat_id, user_id)

            # Имя отправителя
            sender_row = await conn.fetchrow("SELECT name FROM users WHERE user_id = $1", user_id)
            sender_name = sender_row['name'] if sender_row else "Участник"

        # Отправляем сообщения другим участникам
        for p in participants:
            try:
                partner_id = p['user_id']
                partner_data = context.application.user_data.get(partner_id)
                notified_once = p['notified_once']

                # Язык получателя
                async with db_pool.acquire() as conn:
                    lang_row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", partner_id)
                    partner_lang = lang_row['language'] if lang_row else 'ru'

                # Если партнёр тоже в этом чате — показываем сообщение напрямую
                if partner_data and partner_data.get("current_group_chat_session") == session_id:
                    await context.bot.send_message(
                        chat_id=partner_id,
                        text=f"*{sender_name}:*\n{message_text}",
                        parse_mode="Markdown"
                    )
                    # Обновляем last_read для активного получателя
                    async with db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE meetup_chat_members SET last_read_ts = NOW()
                            WHERE user_id = $1 AND chat_id = $2
                        """, partner_id, chat_id)
                elif not notified_once:
                    # Первое сообщение — отправляем пуш с кнопками (как в 1x1)
                    keyboard = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                TEXT2[partner_lang].get("meetups_btn_participants", "👥 Участники"), 
                                callback_data=f"group_chat_participants_{session_id}_{1 if is_board else 0}"
                            ),
                            InlineKeyboardButton(
                                TEXT2[partner_lang].get("open_chat_btn", "✉️ Открыть"), 
                                callback_data=f"group_chat_open_{session_id}_{1 if is_board else 0}"
                            )
                        ]
                    ])

                    await context.bot.send_message(
                        chat_id=partner_id,
                        text=TEXT2[partner_lang].get("group_chat_new_message", 
                            "💬 *{chat_name}*\n{sender} написал(а) сообщение").format(
                                chat_name=chat_name, sender=sender_name),
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )

                    # Ставим флаг notified_once
                    async with db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE meetup_chat_members SET notified_once = TRUE
                            WHERE chat_id = $1 AND user_id = $2
                        """, chat_id, partner_id)

            except Exception as e:
                print(f"⚠️ Не удалось отправить сообщение участнику {p['user_id']}: {e}")

        return True

    except Exception as e:
        print(f"❌ Ошибка handle_group_chat_message: {e}")
        return False


async def get_session_info(conn, session_id: int, is_board: bool) -> dict:
    """Получает информацию о сессии для названия чата"""
    if is_board:
        row = await conn.fetchrow("""
            SELECT gym_name, session_date FROM board_sessions WHERE id = $1
        """, session_id)
    else:
        row = await conn.fetchrow("""
            SELECT gym_name, session_date FROM gym_sessions WHERE id = $1
        """, session_id)

    if row:
        date_str = row['session_date'].strftime("%d.%m") if row['session_date'] else ""
        return {
            'gym_name': row['gym_name'] or "Тренировка",
            'date_str': date_str
        }
    return {'gym_name': 'Тренировка', 'date_str': ''}


async def handle_group_chat_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открытие группового чата из пуша (по session_id)"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Парсим callback: group_chat_open_{session_id}_{is_board}
    parts = query.data.replace("group_chat_open_", "").split("_")
    session_id = int(parts[0])
    is_board = parts[1] == "1" if len(parts) > 1 else False

    try:
        async with db_pool.acquire() as conn:
            # Получаем или создаём чат
            chat_row = await conn.fetchrow(
                "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = $2", 
                session_id, is_board)

            if not chat_row:
                session_info = await get_session_info(conn, session_id, is_board)
                chat_name = f"🧗 {session_info.get('gym_name', 'Тренировка')} · {session_info.get('date_str', '')}"
                await conn.execute("""
                    INSERT INTO group_chats (session_id, chat_name, is_board)
                    VALUES ($1, $2, $3)
                """, session_id, chat_name, is_board)
                chat_row = await conn.fetchrow(
                    "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = $2", 
                    session_id, is_board)

            chat_id = chat_row['id']

            # Сохраняем в контекст
            context.user_data["current_group_chat_session"] = session_id
            context.user_data["current_group_chat_id"] = chat_id
            context.user_data["current_group_chat_is_board"] = is_board

            # Обновляем last_read_ts и сбрасываем notified_once
            await conn.execute("""
                UPDATE meetup_chat_members SET last_read_ts = NOW(), notified_once = FALSE
                WHERE user_id = $1 AND chat_id = $2
            """, user_id, chat_id)

        # Сбрасываем флаги пагинации
        context.user_data["group_chat_page"] = 0
        context.user_data["group_chat_prompt_shown"] = False
        context.user_data.pop("group_chat_msg_id", None)

        # Показываем первую страницу с пагинацией
        await show_group_chat_page(user_id, context, page=0)

    except Exception as e:
        print(f"❌ Ошибка handle_group_chat_open: {e}")

async def handle_group_chat_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ участников группового чата (edit_reply_markup, как в карточках тренировок)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Парсим callback: group_chat_participants_{session_id}_{is_board}
    parts = query.data.replace("group_chat_participants_", "").split("_")
    session_id = int(parts[0])
    is_board = parts[1] == "1" if len(parts) > 1 else False

    try:
        async with db_pool.acquire() as conn:
            # Получаем участников
            if is_board:
                participants = await conn.fetch("""
                    SELECT u.user_id, u.name, u.difficulty
                    FROM board_session_participants bsp
                    JOIN users u ON bsp.user_id = u.user_id
                    WHERE bsp.session_id = $1
                    ORDER BY bsp.joined_at
                """, session_id)
            else:
                participants = await conn.fetch("""
                    SELECT u.user_id, u.name, gsp.difficulty
                    FROM gym_session_participants gsp
                    JOIN users u ON gsp.user_id = u.user_id
                    WHERE gsp.session_id = $1
                    ORDER BY gsp.joined_at
                """, session_id)

        # Формируем кнопки участников
        keyboard = []
        for p in participants:
            name = p['name'] or TEXT2[lang]["default_user"]
            diff = p['difficulty'] or ""
            label = f"👤 {name} ({diff})" if diff else f"👤 {name}"
            participant_id = p['user_id']
            keyboard.append([
                InlineKeyboardButton(label, callback_data=f"profile_{participant_id}"),
                InlineKeyboardButton("🚫", callback_data=f"report_group_{participant_id}_{session_id}")
            ])

        markup = InlineKeyboardMarkup(keyboard)
        # Кнопка назад (возврат к исходным кнопкам пуша)
        keyboard.append([InlineKeyboardButton("◀️", callback_data=f"group_chat_back_{session_id}_{1 if is_board else 0}")])

        # Плавный переход: только меняем кнопки, текст остаётся
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        print(f"❌ Ошибка handle_group_chat_participants: {e}")

async def handle_group_chat_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к исходным кнопкам пуша (Участники / Перейти к чату)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Парсим callback: group_chat_back_{session_id}_{is_board}
    parts = query.data.replace("group_chat_back_", "").split("_")
    session_id = int(parts[0])
    is_board = parts[1] == "1" if len(parts) > 1 else False

    # Восстанавливаем исходные кнопки пуша
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXT2[lang].get("meetups_btn_participants", "👥 Участники"), 
                callback_data=f"group_chat_participants_{session_id}_{1 if is_board else 0}"
            ),
            InlineKeyboardButton(
                TEXT2[lang].get("group_chat_btn_open", "💬 Перейти к чату"), 
                callback_data=f"group_chat_open_{session_id}_{1 if is_board else 0}"
            )
        ]
    ])

    await query.message.edit_reply_markup(reply_markup=keyboard)

async def show_group_chat_page(user_id: int, context: ContextTypes.DEFAULT_TYPE, page: int = 0, edit_message_id: int = None):
    """Показ страницы группового чата с пагинацией (аналог show_chat_page для 1x1)"""

    session_id = context.user_data.get("current_group_chat_session")
    chat_id = context.user_data.get("current_group_chat_id")
    is_board = context.user_data.get("current_group_chat_is_board", False)

    if not chat_id:
        return

    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    async with db_pool.acquire() as conn:
        # Получаем название чата
        chat_row = await conn.fetchrow("SELECT chat_name FROM group_chats WHERE id = $1", chat_id)
        chat_name = chat_row['chat_name'] if chat_row else "🧗 Тренировка"

        # Считаем общее количество сообщений
        total_row = await conn.fetchrow(
            "SELECT COUNT(*) FROM group_chat_messages WHERE chat_id = $1", chat_id)
        total = total_row['count']

        limit = 10
        max_page = max((total - 1) // limit, 0)
        page = max(min(page, max_page), 0)
        offset = total - (page + 1) * limit
        offset = max(offset, 0)
        fetch_limit = min(limit, total - offset)

        context.user_data["group_chat_page"] = page

        # Получаем сообщения
        messages = await conn.fetch("""
            SELECT gcm.message_text, gcm.sent_at, u.name
            FROM group_chat_messages gcm
            JOIN users u ON gcm.sender_id = u.user_id
            WHERE gcm.chat_id = $1
            ORDER BY gcm.sent_at ASC
            OFFSET $2 LIMIT $3
        """, chat_id, offset, fetch_limit)

        # Группируем по датам
        grouped = {}
        for msg in messages:
            date_key = msg['sent_at'].strftime("%d.%m.%Y")
            grouped.setdefault(date_key, []).append(msg)

        # Формируем текст
        msg_blocks = []
        for date, msgs in grouped.items():
            msg_blocks.append(f"*🗓 {date}*")
            for msg in msgs:
                time_str = msg['sent_at'].strftime("%H:%M")
                msg_blocks.append(f"*{msg['name']}* ({time_str}):\n{msg['message_text']}")

        if msg_blocks:
            history_text = "\n\n".join(msg_blocks)
        else:
            history_text = f"*{chat_name}*\n\n_Пока нет сообщений. Напиши первым!_"

        # Обновляем last_read_ts
        await conn.execute("""
            UPDATE meetup_chat_members SET last_read_ts = NOW(), notified_once = FALSE
            WHERE user_id = $1 AND chat_id = $2
        """, user_id, chat_id)

    # Кнопки пагинации
    buttons = []
    if page < max_page:
        buttons.append(InlineKeyboardButton("⬅️", callback_data="group_chat_page_next"))
    if page > 0:
        buttons.append(InlineKeyboardButton("➡️", callback_data="group_chat_page_prev"))
    markup = InlineKeyboardMarkup([buttons]) if buttons else None

    try:
        msg_id = edit_message_id or context.user_data.get("group_chat_msg_id")
        if msg_id:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=msg_id,
                text=history_text,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            context.user_data["group_chat_msg_id"] = msg_id
        else:
            msg = await context.bot.send_message(
                chat_id=user_id,
                text=history_text,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            context.user_data["group_chat_msg_id"] = msg.message_id
    except Exception as e:
        print(f"⚠️ Ошибка show_group_chat_page: {e}")

    # Показываем prompt и клавиатуру только на первой странице
    if page == 0 and not context.user_data.get("group_chat_prompt_shown"):
        chat_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(TEXTS[lang]["btn_end_chat"])]],
            resize_keyboard=True
        )
        await context.bot.send_message(
            chat_id=user_id,
            text=TEXT2[lang].get("chat_write_prompt", "✍️ Напиши сообщение:"),
            reply_markup=chat_keyboard
        )
        context.user_data["group_chat_prompt_shown"] = True

async def handle_group_chat_page_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к более новым сообщениям"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    page = context.user_data.get("group_chat_page", 0)

    if page > 0:
        await show_group_chat_page(user_id, context, page - 1, query.message.message_id)


async def handle_group_chat_page_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к более старым сообщениям"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    page = context.user_data.get("group_chat_page", 0)

    await show_group_chat_page(user_id, context, page + 1, query.message.message_id)

async def handle_group_chat_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Жалоба на участника группового чата"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    # Парсим: report_group_{reported_id}_{session_id}
    data = query.data.replace("report_group_", "")
    parts = data.split("_")
    reported_id = int(parts[0])
    session_id = int(parts[1])

    # Сохраняем для следующего шага
    context.user_data["report_target_id"] = reported_id
    context.user_data["report_from_group"] = session_id

    # Показываем меню выбора причины (как в 1x1)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_abuse"], callback_data="report_reason_abuse")],
        [InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_photo"], callback_data="report_reason_photo")],
        [InlineKeyboardButton(INLINE_TEXTS[lang]["btn_report_spam"], callback_data="report_reason_spam")],
        [InlineKeyboardButton(TEXT2[lang].get("btn_cancel", "❌ Отмена"), callback_data="report_reason_cancel")]
    ])

    await query.message.reply_text(
        TEXT2[lang].get("report_choose_reason", "📋 Выберите причину жалобы:"),
        reply_markup=keyboard
    )


async def handle_group_report_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора причины жалобы из группового чата"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data.get("lang", "ru")

    reported_id = context.user_data.get("report_target_id")
    session_id = context.user_data.get("report_from_group")

    if not reported_id:
        await query.message.edit_text("⚠️ Ошибка")
        return

    reason_key = query.data.replace("report_reason_", "")

    if reason_key == "cancel":
        await query.message.edit_text(TEXT2[lang].get("report_cancelled", "❌ Отменено"))
        return

    # Маппинг причин
    reason_map = {
        "abuse": "Оскорбления",
        "photo": "Неприемлемое фото", 
        "spam": "Спам"
    }
    reason = reason_map.get(reason_key, "Другое")

    # Сохраняем жалобу
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_reports (reporter_id, reported_id, reason, timestamp)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT DO NOTHING
        """, user_id, reported_id, reason)

    # Проверяем санкции
    await check_user_reports_and_apply_sanctions(reported_id)

    # Очищаем контекст
    context.user_data.pop("report_target_id", None)
    context.user_data.pop("report_from_group", None)

    await query.message.edit_text(
        TEXT2[lang].get("report_sent", "✅ Жалоба отправлена. Спасибо!")
    )
# ==================== BOARD SESSION HANDLERS ====================

async def handle_board_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вступление в board тренировку"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("board_join_", ""))

    try:
        async with db_pool.acquire() as conn:
            # Получаем дату сессии, на которую пользователь хочет записаться
            target_session = await conn.fetchrow("""
                SELECT session_date FROM board_sessions WHERE id = $1
            """, session_id)

            if not target_session:
                await query.message.reply_text("Ошибка: тренировка не найдена")
                return

            target_date = target_session['session_date']

            # Проверяем, не участвует ли уже в тренировке на эту дату
            # Проверяем и кастомные (board_sessions), и дефолтные (gym_sessions) тренировки
            existing_board = await conn.fetchrow("""
                SELECT bs.id FROM board_session_participants bsp
                JOIN board_sessions bs ON bsp.session_id = bs.id
                WHERE bsp.user_id = $1 AND bs.session_date = $2
            """, user_id, target_date)

            existing_gym = await conn.fetchrow("""
                SELECT gs.id FROM gym_session_participants gsp
                JOIN gym_sessions gs ON gsp.session_id = gs.id
                WHERE gsp.user_id = $1 AND gs.session_date = $2
            """, user_id, target_date)

            if existing_board or existing_gym:
                await query.message.reply_text(TEXT2[lang]["meetups_already_joined"])
                return

            # Берём уровень из профиля
            user_row = await conn.fetchrow("SELECT difficulty FROM users WHERE user_id = $1", user_id)
            user_difficulty = user_row['difficulty'] if user_row else None

        # Вступаем (используем тот же complete, но передаём is_board=True)
        await complete_board_join(update, context, session_id, user_difficulty)

    except Exception as e:
        print(f"❌ Ошибка handle_board_join: {e}")


async def complete_board_join(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: int, difficulty: str, has_level_dialog: bool = False):
    """Завершение вступления в board тренировку"""
    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    query = update.callback_query

    try:
        async with db_pool.acquire() as conn:
            # Добавляем участника
            await conn.execute("""
                INSERT INTO board_session_participants (session_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            """, session_id, user_id)

            # 🎁 Награда за вступление — 1г магнезии (раз в день)
            today = datetime.now().date()
            already_rewarded_today = await conn.fetchval("""
                SELECT 1 FROM magnesium_log 
                WHERE user_id = $1 
                  AND reason = 'join_training'
                  AND timestamp::date = $2
            """, user_id, today)

            if not already_rewarded_today:
                await add_magnesium(user_id, 1, "join_training")
                balance = await get_magnesium(user_id)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=TEXT2[lang].get("magnesium_join_gift", 
                        "🎁 +1г магнезии за запись на тренировку!\nБаланс: {balance}г").format(balance=balance)
                )

            # Создаём групповой чат если его нет
            chat_row = await conn.fetchrow("SELECT id FROM group_chats WHERE session_id = $1 AND is_board = TRUE", session_id)
            if not chat_row:
                session_row = await conn.fetchrow("SELECT session_date FROM board_sessions WHERE id = $1", session_id)
                chat_name = f"🧗 {session_row['session_date'].strftime('%d.%m.%y')}" if session_row else "🧗 Тренировка"
                chat_row = await conn.fetchrow("""
                    INSERT INTO group_chats (session_id, chat_name, is_board)
                    VALUES ($1, $2, TRUE)
                    RETURNING id
                """, session_id, chat_name)

            chat_id = chat_row['id']

            # Добавляем в meetup_chat_members
            await conn.execute("""
                INSERT INTO meetup_chat_members (user_id, chat_id, session_id, is_active)
                VALUES ($1, $2, $3, TRUE)
                ON CONFLICT (user_id, chat_id) DO UPDATE SET is_active = TRUE, joined_at = NOW()
            """, user_id, chat_id, session_id)

            # Добавляем/обновляем активность чата
            await conn.execute("""
                INSERT INTO meetup_chat_activity (chat_id, session_id, last_message_ts)
                VALUES ($1, $2, NOW())
                ON CONFLICT (chat_id) DO NOTHING
            """, chat_id, session_id)

            # Перезагружаем список сессий с обновлённым количеством участников
            gym_name = context.user_data.get("meetup_selected_gym", "")
            session_pages = await reload_gym_sessions(conn, gym_name, user_id)
            context.user_data["meetups_session_pages"] = [[dict(s) for s in page] for page in session_pages]

        # Если был диалог выбора уровня, удаляем промежуточные сообщения (на будущее)
        if has_level_dialog:
            # Удаляем сообщение с выбором уровня
            try:
                if query and query.message:
                    await query.message.delete()
            except:
                pass

            # Удаляем оригинальную карточку с кнопкой "Я приду"
            card_message_id = context.user_data.get("meetup_card_message_id")
            if card_message_id:
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=card_message_id)
                except:
                    pass
                context.user_data.pop("meetup_card_message_id", None)

            # Показываем новую карточку с обновленными данными
            current_index = context.user_data.get("meetups_session_index", 0)
            await show_session_card(update, context, current_index, edit=False)
        else:
            # Плавный UX: редактируем текущую карточку с обновлёнными данными
            current_index = context.user_data.get("meetups_session_index", 0)
            await show_session_card(update, context, current_index, edit=True)

    except Exception as e:
        print(f"❌ Ошибка complete_board_join: {e}")


async def handle_board_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выход из board тренировки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("board_leave_", ""))
    gym_name = context.user_data.get("meetup_selected_gym", "free")

    # Проверяем, находимся ли в режиме board_my
    is_board_my_mode = "board_my_session_pages" in context.user_data

    try:
        async with db_pool.acquire() as conn:
            # Удаляем участника
            await conn.execute("""
                DELETE FROM board_session_participants
                WHERE session_id = $1 AND user_id = $2
            """, session_id, user_id)

            # Удаляем из meetup_chat_members (выход из группового чата)
            chat_row = await conn.fetchrow("SELECT id FROM group_chats WHERE session_id = $1 AND is_board = TRUE", session_id)
            if chat_row:
                await conn.execute("""
                    UPDATE meetup_chat_members SET is_active = FALSE
                    WHERE chat_id = $1 AND user_id = $2
                """, chat_row['id'], user_id)

            # Проверяем, остались ли участники
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM board_session_participants WHERE session_id = $1
            """, session_id)

            # Если нет участников — удаляем board сессию
            session_row = await conn.fetchrow("SELECT gym_name FROM board_sessions WHERE id = $1", session_id)
            if session_row and count == 0:
                await conn.execute("DELETE FROM board_sessions WHERE id = $1", session_id)
                await conn.execute("DELETE FROM group_chats WHERE session_id = $1 AND is_board = TRUE", session_id)
                await conn.execute("DELETE FROM meetup_chat_members WHERE session_id = $1", session_id)
                await conn.execute("DELETE FROM meetup_chat_activity WHERE session_id = $1", session_id)

            gym_name = session_row['gym_name'] if session_row and session_row['gym_name'] else gym_name

            if is_board_my_mode:
                # Режим board_my: перезагружаем список тренировок пользователя
                today = datetime.now().date()
                all_sessions = await conn.fetch("""
                    SELECT
                        gs.id, gs.gym_name, gs.climb_type, gs.session_date, gs.session_time,
                        'gym' AS session_type,
                        COUNT(gsp2.user_id) AS participants_count
                    FROM gym_sessions gs
                    JOIN gym_session_participants gsp ON gs.id = gsp.session_id
                    LEFT JOIN gym_session_participants gsp2 ON gs.id = gsp2.session_id
                    WHERE gsp.user_id = $1 AND gs.session_date >= $2
                    GROUP BY gs.id

                    UNION ALL

                    SELECT
                        bs.id, bs.gym_name, bs.climb_type, bs.session_date, bs.session_time,
                        'board' AS session_type,
                        COUNT(bsp2.user_id) AS participants_count
                    FROM board_sessions bs
                    JOIN board_session_participants bsp ON bs.id = bsp.session_id
                    LEFT JOIN board_session_participants bsp2 ON bs.id = bsp2.session_id
                    WHERE bsp.user_id = $1 AND bs.session_date >= $2
                    GROUP BY bs.id

                    ORDER BY session_date, session_time
                """, user_id, today)

                if not all_sessions:
                    # Список пуст - удаляем кнопки и показываем сообщение
                    try:
                        await query.message.edit_caption(
                            caption=TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."),
                            reply_markup=None
                        )
                    except:
                        try:
                            await query.message.edit_text(
                                text=TEXT2[lang].get("board_my_empty", "📭 Вы пока не записаны ни на одну тренировку."),
                                reply_markup=None
                            )
                        except:
                            pass
                    # Очищаем данные пагинации
                    context.user_data.pop("board_my_session_pages", None)
                    context.user_data.pop("board_my_session_index", None)
                    return

                # Формируем новые страницы пагинации
                session_pages = []
                for session in all_sessions:
                    session_dict = dict(session)
                    session_pages.append([session_dict])

                context.user_data["board_my_session_pages"] = session_pages

                # Определяем новый индекс для показа
                current_index = context.user_data.get("board_my_session_index", 0)
                new_index = min(current_index, len(session_pages) - 1)

                # Показываем карточку с корректным индексом
                await show_board_my_card(update, context, new_index, edit=True)
            else:
                # Обычный режим handle_meetups_menu: перезагружаем список тренировок зала с актуальными данными
                session_pages = await reload_gym_sessions(conn, gym_name, user_id)
                context.user_data["meetups_session_pages"] = [[dict(s) for s in page] for page in session_pages]

                # Определяем новый индекс для показа (сохраняем текущую позицию)
                current_index = context.user_data.get("meetups_session_index", 0)
                new_index = min(current_index, len(session_pages) - 1) if session_pages else 0

                # Плавный UX: показываем карточку с сохранением текущей позиции
                await show_session_card(update, context, new_index, edit=True)

    except Exception as e:
        print(f"❌ Ошибка handle_board_leave: {e}")


async def handle_board_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ списка участников board тренировки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("board_parts_", ""))
    context.user_data["board_viewing_session"] = session_id

    try:
        async with db_pool.acquire() as conn:
            participants = await conn.fetch("""
                SELECT u.user_id, u.name
                FROM board_session_participants bsp
                JOIN users u ON bsp.user_id = u.user_id
                WHERE bsp.session_id = $1
                ORDER BY bsp.joined_at
            """, session_id)

        # Формируем список с кнопками (profile_ паттерн для существующего хэндлера)
        keyboard = []

        if not participants:
            text = TEXT2[lang].get("meetups_no_participants", "👥 Пока никого нет")
        else:
            for p in participants:
                name = p['name']
                label = f"👤 {name}"
                participant_id = p['user_id']
                keyboard.append([
                    InlineKeyboardButton(label, callback_data=f"profile_{participant_id}"),
                    InlineKeyboardButton("🚫", callback_data=f"report_group_{participant_id}_{session_id}")
                ])
            text = TEXT2[lang].get("meetups_participants_title", "👥 Участники")

        keyboard.append([InlineKeyboardButton("◀", callback_data=f"board_back_session_{session_id}")])

        # Плавный переход: проверяем тип сообщения
        # Board карточки всегда отправляются как фото с caption через show_session_card
        has_photo = bool(query.message.photo)
        has_caption = query.message.caption is not None

        if has_photo or has_caption:
            # Если было фото - редактируем caption
            await query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Если текстовое - просто редактируем
            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        print(f"❌ Ошибка handle_board_participants: {e}")


async def handle_board_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открытие группового чата board тренировки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    session_id = int(query.data.replace("board_chat_", ""))

    try:
        async with db_pool.acquire() as conn:
            # Создаём чат если его нет
            chat_row = await conn.fetchrow(
                "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = TRUE", session_id)

            if not chat_row:
                session_info = await get_session_info(conn, session_id, is_board=True)
                chat_name = f"🧗 {session_info.get('gym_name', 'Тренировка')} · {session_info.get('date_str', '')}"

                await conn.execute("""
                    INSERT INTO group_chats (session_id, chat_name, is_board)
                    VALUES ($1, $2, TRUE)
                """, session_id, chat_name)
                chat_row = await conn.fetchrow(
                    "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = TRUE", session_id)

            chat_id = chat_row['id']

            # Сохраняем в контекст
            context.user_data["current_group_chat_session"] = session_id
            context.user_data["current_group_chat_id"] = chat_id
            context.user_data["current_group_chat_is_board"] = True

            # Обновляем last_read_ts и сбрасываем notified_once
            await conn.execute("""
                UPDATE meetup_chat_members SET last_read_ts = NOW(), notified_once = FALSE
                WHERE user_id = $1 AND chat_id = $2
            """, user_id, chat_id)

        # Сбрасываем флаги пагинации
        context.user_data["group_chat_page"] = 0
        context.user_data["group_chat_prompt_shown"] = False
        context.user_data.pop("group_chat_msg_id", None)

        # Показываем первую страницу с пагинацией
        await show_group_chat_page(user_id, context, page=0)

    except Exception as e:
        print(f"❌ Ошибка handle_board_chat: {e}")

async def handle_board_back_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к карточке board сессии (из участников)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Сбрасываем режим группового чата
    context.user_data["current_group_chat_session"] = None
    context.user_data["current_group_chat_is_board"] = None
    context.user_data["awaiting"] = None

    # Перезагружаем текущую карточку сессии
    current_index = context.user_data.get("meetups_session_index", 0)
    await show_session_card(update, context, current_index, edit=True)


async def handle_meetup_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа на опрос после тренировки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    try:
        # Парсим данные: meetup_fb_good_123 или meetup_fb_bad_123
        parts = data.split("_")
        rating = parts[2]  # good или bad
        session_id = int(parts[3])

        async with db_pool.acquire() as conn:
            # Проверяем что ещё не отвечали
            existing = await conn.fetchval("""
                SELECT 1 FROM training_feedback WHERE user_id = $1 AND session_id = $2
            """, user_id, session_id)

            if existing:
                await query.message.edit_text("✅ Спасибо, ты уже ответил!")
                return

            # Сохраняем ответ
            await conn.execute("""
                INSERT INTO training_feedback (session_id, user_id, rating)
                VALUES ($1, $2, $3)
            """, session_id, user_id, rating)

        thanks_text = {
            'good': "👍 Отлично! Рады, что тренировка понравилась!",
            'bad': "👎 Жаль. Надеемся, следующая будет лучше!"
        }.get(rating, "✅ Спасибо за отзыв!")

        await query.message.edit_text(thanks_text)

    except Exception as e:
        print(f"❌ Ошибка handle_meetup_feedback: {e}")
        await query.message.edit_text("✅ Спасибо за отзыв!")

async def handle_meetup_chat_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открытие группового чата из 'Активные чаты' (по chat_id)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    chat_id = int(query.data.replace("meetup_chat_open_", ""))

    try:
        async with db_pool.acquire() as conn:
            # Получаем session_id и is_board по chat_id
            chat_row = await conn.fetchrow(
                "SELECT session_id, chat_name, is_board FROM group_chats WHERE id = $1", chat_id)
            if not chat_row:
                await query.message.reply_text("⚠️ Чат не найден")
                return

            session_id = chat_row['session_id']
            is_board = chat_row['is_board']

            # Сохраняем в контекст
            context.user_data["current_group_chat_session"] = session_id
            context.user_data["current_group_chat_id"] = chat_id
            context.user_data["current_group_chat_is_board"] = is_board

            # Обновляем last_read_ts и сбрасываем notified_once
            await conn.execute("""
                UPDATE meetup_chat_members SET last_read_ts = NOW(), notified_once = FALSE
                WHERE user_id = $1 AND chat_id = $2
            """, user_id, chat_id)

        # Сбрасываем флаги пагинации
        context.user_data["group_chat_page"] = 0
        context.user_data["group_chat_prompt_shown"] = False
        context.user_data.pop("group_chat_msg_id", None)

        # Показываем первую страницу с пагинацией
        await show_group_chat_page(user_id, context, page=0)

    except Exception as e:
        print(f"❌ Ошибка handle_meetup_chat_open: {e}")


async def handle_meetup_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открытие группового чата тренировки из карточки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    # Парсим callback: meetup_chat_{session_id} или meetup_chat_{session_id}_board
    data = query.data.replace("meetup_chat_", "")
    if "_board" in data:
        session_id = int(data.replace("_board", ""))
        is_board = True
    else:
        session_id = int(data)
        is_board = False

    try:
        async with db_pool.acquire() as conn:
            # Получаем или создаём чат
            chat_row = await conn.fetchrow(
                "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = $2", 
                session_id, is_board)

            if not chat_row:
                session_info = await get_session_info(conn, session_id, is_board)
                chat_name = f"🧗 {session_info.get('gym_name', 'Тренировка')} · {session_info.get('date_str', '')}"

                await conn.execute("""
                    INSERT INTO group_chats (session_id, chat_name, is_board)
                    VALUES ($1, $2, $3)
                """, session_id, chat_name, is_board)
                chat_row = await conn.fetchrow(
                    "SELECT id, chat_name FROM group_chats WHERE session_id = $1 AND is_board = $2", 
                    session_id, is_board)

            chat_id = chat_row['id']

            # Сохраняем в контекст
            context.user_data["current_group_chat_session"] = session_id
            context.user_data["current_group_chat_id"] = chat_id
            context.user_data["current_group_chat_is_board"] = is_board

            # Обновляем last_read_ts и сбрасываем notified_once
            await conn.execute("""
                UPDATE meetup_chat_members SET last_read_ts = NOW(), notified_once = FALSE
                WHERE user_id = $1 AND chat_id = $2
            """, user_id, chat_id)

        # Сбрасываем флаги пагинации
        context.user_data["group_chat_page"] = 0
        context.user_data["group_chat_prompt_shown"] = False
        context.user_data.pop("group_chat_msg_id", None)

        # Показываем первую страницу с пагинацией
        await show_group_chat_page(user_id, context, page=0)

    except Exception as e:
        print(f"❌ Ошибка handle_meetup_chat: {e}")


async def handle_meetup_chat_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выход из группового чата через кнопку в 'Активные чаты'"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await ensure_lang(context, user_id)
    lang = context.user_data["lang"]

    chat_id = int(query.data.replace("meetup_chat_leave_", ""))

    try:
        async with db_pool.acquire() as conn:
            # Получаем session_id
            chat_row = await conn.fetchrow("SELECT session_id FROM group_chats WHERE id = $1", chat_id)
            if chat_row:
                session_id = chat_row['session_id']

                # Удаляем из участников тренировки
                await conn.execute("""
                    DELETE FROM gym_session_participants 
                    WHERE session_id = $1 AND user_id = $2
                """, session_id, user_id)

                # Деактивируем в meetup_chat_members
                await conn.execute("""
                    UPDATE meetup_chat_members SET is_active = FALSE
                    WHERE chat_id = $1 AND user_id = $2
                """, chat_id, user_id)

                # Проверяем остались ли участники (для кастомных сессий)
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM gym_session_participants WHERE session_id = $1
                """, session_id)

                session_row = await conn.fetchrow("SELECT is_default FROM gym_sessions WHERE id = $1", session_id)
                if session_row and not session_row['is_default'] and count == 0:
                    await conn.execute("DELETE FROM gym_sessions WHERE id = $1", session_id)
                    await conn.execute("DELETE FROM group_chats WHERE session_id = $1", session_id)
                    await conn.execute("DELETE FROM meetup_chat_members WHERE session_id = $1", session_id)
                    await conn.execute("DELETE FROM meetup_chat_activity WHERE session_id = $1", session_id)

        # Сбрасываем состояние чата
        context.user_data["current_group_chat_session"] = None
        context.user_data["current_group_chat_id"] = None
        context.user_data["current_group_chat_is_board"] = None
        context.user_data["group_chat_page"] = None
        context.user_data["group_chat_prompt_shown"] = None
        context.user_data.pop("group_chat_msg_id", None)

        await query.answer(TEXT2[lang].get("meetups_left", "✅ Вы вышли"))

        # Обновляем список активных чатов
        await show_active_chats_page(update, context, page=0, is_first=False)

    except Exception as e:
        print(f"❌ Ошибка handle_meetup_chat_leave: {e}")

# ===== /MEETUPS =====


# Глобальный обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает все ошибки, возникающие в боте"""
    import traceback
    from telegram.error import NetworkError, TimedOut, RetryAfter

    # Логируем ошибку
    print(f"❌ Exception while handling an update: {context.error}")

    # Если это сетевая ошибка (ReadError, TimedOut и т.д.) - просто логируем
    if isinstance(context.error, (NetworkError, TimedOut)):
        print(f"⚠️ Network error occurred: {type(context.error).__name__} - будет автоматический retry")
        return

    # Если это RetryAfter - ждем указанное время
    if isinstance(context.error, RetryAfter):
        print(f"⏳ RetryAfter error: waiting {context.error.retry_after} seconds")
        await asyncio.sleep(context.error.retry_after)
        return

    # Для остальных ошибок выводим полный traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    print(f"Full traceback:\n{tb_string}")

    # Пытаемся уведомить пользователя, если возможно
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте еще раз или обратитесь к администратору."
            )
    except Exception as e:
        print(f"❌ Не удалось отправить сообщение об ошибке пользователю: {e}")


# Регистрируем обработчик ошибок
application.add_error_handler(error_handler)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("admin", admin_panel))
application.add_handler(CommandHandler("reset_reports", reset_user_reports))
application.add_handler(CommandHandler("delete", confirm_delete_profile))
application.add_handler(CommandHandler("unhide_all", handle_unhide_all))
application.add_handler(CommandHandler("reset_referrals", reset_referrals))
application.add_handler(CommandHandler("reset_founder", reset_founder))
application.add_handler(CommandHandler("reset_boost", reset_boost))
application.add_handler(CommandHandler("reset_meetups", reset_meetups))
application.add_handler(CommandHandler("dump", dump_users))
application.add_handler(CommandHandler("reset_weights", cmd_reset_weights))
application.add_handler(CommandHandler("reset_difficulty", cmd_reset_difficulty))
application.add_handler(CommandHandler("reset_fotoreminder", reset_photo_reminders_cmd))


# Обработка Объявления
application.add_handler(CallbackQueryHandler(handle_board_date_selection, pattern="^board_date_"))
application.add_handler(CallbackQueryHandler(handle_board_time_selection, pattern="^board_time_"))
application.add_handler(CallbackQueryHandler(handle_board_climb_type, pattern="^board_climb_"))
application.add_handler(CallbackQueryHandler(handle_board_difficulty, pattern="^boarddiff_"))
application.add_handler(CallbackQueryHandler(handle_board_gym_selection, pattern="^board_gym_sel_"))
application.add_handler(CallbackQueryHandler(handle_board_publish, pattern="^board_publish$"))
application.add_handler(CallbackQueryHandler(handle_board_remove, pattern="^board_remove$"))
application.add_handler(CallbackQueryHandler(handle_board_edit, pattern="^board_edit$"))
application.add_handler(CallbackQueryHandler(handle_toggle_profile, pattern="^toggle_profile_"))
application.add_handler(CallbackQueryHandler(handle_board_status_info, pattern="^board_status_active$"))
application.add_handler(CallbackQueryHandler(handle_board_status_removed, pattern="^board_status_removed$"))
application.add_handler(CallbackQueryHandler(handle_time_page_nav, pattern="^time_page_"))
application.add_handler(CallbackQueryHandler(handle_board_city_next, pattern="^board_city_next$"))
application.add_handler(CallbackQueryHandler(handle_search_difficulty_bucket, pattern=r"^diffrange_"))
application.add_handler(CallbackQueryHandler(cb_set_status, pattern=r"^set_status:"))
application.add_handler(CallbackQueryHandler(handle_edit_status, pattern="^edit_status$"))
application.add_handler(CallbackQueryHandler(handle_group_chat_report, pattern="^report_group_"))
application.add_handler(CallbackQueryHandler(handle_group_report_reason, pattern="^report_reason_"))

application.add_handler(CallbackQueryHandler(handle_edit_name_button, pattern="^edit_name$"))
application.add_handler(CallbackQueryHandler(edit_level_prompt, pattern="^edit_level$"))
application.add_handler(CallbackQueryHandler(edit_level_save, pattern="^editdiffval_"))

application.add_handler(CallbackQueryHandler(edit_gender_prompt, pattern="^edit_gender$"))
application.add_handler(CallbackQueryHandler(edit_gender_save, pattern="^editgender_"))
application.add_handler(CallbackQueryHandler(edit_climb_type_prompt, pattern="^edit_climb_type$"))
application.add_handler(CallbackQueryHandler(edit_climb_type_save, pattern="^edittype_"))
application.add_handler(CallbackQueryHandler(edit_weight_prompt, pattern="^edit_weight$"))
application.add_handler(CallbackQueryHandler(edit_weight_save, pattern="^editweight_"))
application.add_handler(CallbackQueryHandler(edit_photo_prompt, pattern="^edit_photo$"))
application.add_handler(CallbackQueryHandler(edit_photo_delete, pattern="^editphoto_delete$"))
application.add_handler(CallbackQueryHandler(edit_photo_skip, pattern="^editphoto_skip$"))
application.add_handler(CallbackQueryHandler(edit_bio_prompt, pattern="^edit_about$"))
application.add_handler(CallbackQueryHandler(edit_bio_delete, pattern="^editbio_delete$"))
application.add_handler(CallbackQueryHandler(edit_bio_skip, pattern="^editbio_skip$"))
application.add_handler(CallbackQueryHandler(handle_edit_location, pattern="^edit_location$"))
application.add_handler(CallbackQueryHandler(menu_board, pattern="^menu_board$"))
application.add_handler(CallbackQueryHandler(handle_difficulty_pagination, pattern="^diffval_"))
application.add_handler(CallbackQueryHandler(handle_noop, pattern="^noop$"))

# 🤝 Встречи (Meetups)
application.add_handler(CallbackQueryHandler(handle_meetups_menu, pattern="^meetups_menu$"))
application.add_handler(CallbackQueryHandler(handle_meetup_other_location, pattern="^meetup_gym_other$"))
application.add_handler(CallbackQueryHandler(handle_board_create_start, pattern="^board_create_start$"))
application.add_handler(CallbackQueryHandler(handle_meetup_gym_selection, pattern="^meetup_gym_"))
application.add_handler(CallbackQueryHandler(handle_meetup_nav_prev, pattern="^meetup_nav_prev$"))
application.add_handler(CallbackQueryHandler(handle_meetup_nav_next, pattern="^meetup_nav_next$"))
application.add_handler(CallbackQueryHandler(handle_board_my_nav_prev, pattern="^board_my_nav_prev$"))
application.add_handler(CallbackQueryHandler(handle_board_my_nav_next, pattern="^board_my_nav_next$"))
application.add_handler(CallbackQueryHandler(handle_meetup_join, pattern="^meetup_join_"))
application.add_handler(CallbackQueryHandler(handle_meetup_level_selection, pattern="^meetup_level_"))
application.add_handler(CallbackQueryHandler(handle_meetup_leave, pattern="^meetup_leave_"))
application.add_handler(CallbackQueryHandler(handle_meetup_participants, pattern="^meetup_parts_"))
application.add_handler(CallbackQueryHandler(handle_meetup_back_session, pattern="^meetup_back_session_"))
application.add_handler(CallbackQueryHandler(handle_meetup_chat_open, pattern="^meetup_chat_open_"))
application.add_handler(CallbackQueryHandler(handle_meetup_chat_leave, pattern="^meetup_chat_leave_"))
application.add_handler(CallbackQueryHandler(handle_meetup_chat, pattern="^meetup_chat_\\d+$"))
application.add_handler(CallbackQueryHandler(handle_meetup_feedback, pattern="^meetup_fb_"))

# Board session handlers
application.add_handler(CallbackQueryHandler(handle_board_join, pattern="^board_join_"))
application.add_handler(CallbackQueryHandler(handle_board_leave, pattern="^board_leave_"))
application.add_handler(CallbackQueryHandler(handle_board_participants, pattern="^board_parts_"))
application.add_handler(CallbackQueryHandler(handle_board_chat, pattern="^board_chat_\\d+$"))
application.add_handler(CallbackQueryHandler(handle_board_back_session, pattern="^board_back_session_"))

# 🌍 Глобальный поиск
application.add_handler(CallbackQueryHandler(handle_global_search, pattern="^btn_global_search$"))
application.add_handler(CallbackQueryHandler(handle_global_referral, pattern="^btn_global_referral$"))
application.add_handler(CallbackQueryHandler(handle_go_home, pattern="^go_home$"))
application.add_handler(CallbackQueryHandler(handle_chalk_get_referral, pattern="^handle_chalk_get_referral$"))

application.add_handler(CallbackQueryHandler(handle_unmute, pattern="^unmute_"))
application.add_handler(CallbackQueryHandler(lang_selected, pattern="^lang_"))
application.add_handler(CallbackQueryHandler(handle_write_prompt, pattern="^write_\\d+$"))
application.add_handler(CallbackQueryHandler(handle_write_confirm, pattern="^confirm_write$"))
application.add_handler(CallbackQueryHandler(handle_write_cancel, pattern="^cancel_write$"))

application.add_handler(CallbackQueryHandler(handle_climb_type, pattern="^type_"))
application.add_handler(CallbackQueryHandler(handle_country, pattern="^country_"))
application.add_handler(CallbackQueryHandler(handle_city_geo, pattern="^city_geo_"))
application.add_handler(CallbackQueryHandler(handle_city, pattern="^city_"))
application.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
application.add_handler(CallbackQueryHandler(handle_weight, pattern="^weight_"))
application.add_handler(CallbackQueryHandler(handle_finish_registration, pattern="finish_registration"))
application.add_handler(CallbackQueryHandler(handle_skip_photo, pattern="^skip_photo$"))

application.add_handler(CallbackQueryHandler(handle_weight_pagination, pattern="^weightval_"))
application.add_handler(CallbackQueryHandler(handle_search_weight, pattern=r"^search_weight_"))

application.add_handler(CallbackQueryHandler(handle_search_difficulty, pattern="^search_diff_"))
application.add_handler(CallbackQueryHandler(handle_search_type, pattern="^search_type_"))
application.add_handler(CallbackQueryHandler(handle_search_gender, pattern="^search_gender_"))
application.add_handler(CallbackQueryHandler(handle_search_weight, pattern="^search_weight_"))
application.add_handler(CallbackQueryHandler(confirm_exit, pattern="^confirm_exit$"))
application.add_handler(CallbackQueryHandler(handle_view_profile_from_chat, pattern="^profile_"))
application.add_handler(CallbackQueryHandler(handle_archive_chat, pattern="^archive_chat_"))
application.add_handler(CallbackQueryHandler(handle_hide_user, pattern="^hide_\\d+_[\\d]+[d]$"))
application.add_handler(CallbackQueryHandler(handle_hide_prompt, pattern="^hide_\\d+$"))
application.add_handler(CallbackQueryHandler(handle_go_to_search_menu, pattern="^go_to_search_menu$"))
application.add_handler(CallbackQueryHandler(handle_unhide_user, pattern="^unhide_\\d+$"))
application.add_handler(CallbackQueryHandler(handle_like_callback, pattern="^like_\\d+$"))
application.add_handler(CallbackQueryHandler(handle_view_liked_me_callback, pattern="^view_liked_me$"))
application.add_handler(CallbackQueryHandler(handle_skip_bio, pattern="^skip_bio$"))
application.add_handler(CallbackQueryHandler(handle_skip_photo_registration, pattern="^skip_photo_registration$"))
application.add_handler(CallbackQueryHandler(handle_photo_reminder_update, pattern="^photo_reminder_update$"))
application.add_handler(CallbackQueryHandler(handle_photo_reminder_skip, pattern="^photo_reminder_skip$"))
application.add_handler(CallbackQueryHandler(handle_admin_send_photo_reminders, pattern="^admin_send_reminders$"))
application.add_handler(CallbackQueryHandler(handle_report, pattern="^report_\\d+$"))
application.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.answer(), pattern="^noop$"))
application.add_handler(CallbackQueryHandler(handle_report_reason, pattern="^reason_.*$"))
# Callback handlers для пагинации лайков
application.add_handler(CallbackQueryHandler(handle_sent_likes_page_nav, pattern="^sent_likes_page_nav_\d+$"))
application.add_handler(CallbackQueryHandler(handle_liked_me_page_nav, pattern="^liked_me_page_nav_\d+$"))
application.add_handler(CallbackQueryHandler(handle_mutual_likes_page_nav, pattern="^mutual_likes_page_nav_\d+$"))
application.add_handler(CallbackQueryHandler(handle_hidden_users_page_nav, pattern="^hidden_users_page_nav_\d+$"))
application.add_handler(CallbackQueryHandler(handle_active_chats_page_nav, pattern="^active_chats_page_nav_\d+$"))
application.add_handler(CallbackQueryHandler(handle_muted_chats_page_nav, pattern="^muted_chats_page_nav_\d+$"))

application.add_handler(CallbackQueryHandler(handle_delete_profile_callback, pattern="^(confirm|cancel)_delete_profile$"))
application.add_handler(CallbackQueryHandler(handle_unlock_likes_prompt, pattern="^unlock_likes_referral$"))
application.add_handler(CallbackQueryHandler(handle_consent_agree, pattern="^consent_agree$"))
application.add_handler(CallbackQueryHandler(show_user_agreement, pattern="^show_user_agreement$"))
application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^admin_"))
application.add_handler(CallbackQueryHandler(handle_mute_from_request, pattern="^mute_from_request_"))
application.add_handler(CallbackQueryHandler(handle_consent_decline, pattern="^consent_decline$"))
application.add_handler(CallbackQueryHandler(handle_fill_profile, pattern="^fill_profile$"))
application.add_handler(CallbackQueryHandler(handle_skip_weight, pattern="^skip_weight$"))
application.add_handler(CallbackQueryHandler(handle_admin_location_selection, pattern="^(country_|city_)"))
application.add_handler(CallbackQueryHandler(handle_stats_selection, pattern="^stats_"))
application.add_handler(CallbackQueryHandler(handle_restore_chat, pattern=r"^restore_chat_\d+$"))
application.add_handler(CallbackQueryHandler(handle_confirm_delete_chat, pattern=r"^confirm_delete_chat_"))
application.add_handler(CallbackQueryHandler(handle_delete_chat_yes, pattern=r"^delete_chat_yes_"))
application.add_handler(CallbackQueryHandler(handle_delete_chat_no, pattern=r"^delete_chat_no_"))
application.add_handler(CallbackQueryHandler(handle_board_partner_gender, pattern="^board_gender_"))

# Чаты
application.add_handler(CallbackQueryHandler(handle_open_chat, pattern=r"^open_chat_\d+$"))
application.add_handler(CallbackQueryHandler(handle_chat_page_prev, pattern="^chat_page_prev$"))
application.add_handler(CallbackQueryHandler(handle_chat_page_next, pattern="^chat_page_next$"))
application.add_handler(CallbackQueryHandler(handle_group_chat_open, pattern="^group_chat_open_"))
application.add_handler(CallbackQueryHandler(handle_group_chat_participants, pattern="^group_chat_participants_"))
application.add_handler(CallbackQueryHandler(handle_group_chat_back, pattern="^group_chat_back_"))
application.add_handler(CallbackQueryHandler(handle_group_chat_page_prev, pattern="^group_chat_page_prev$"))
application.add_handler(CallbackQueryHandler(handle_group_chat_page_next, pattern="^group_chat_page_next$"))

# Cragsy Boost
application.add_handler(CallbackQueryHandler(handle_boost_buy_entry, pattern="^boost_buy$"))
application.add_handler(CallbackQueryHandler(handle_boost_buy_confirm_yes, pattern="^boost_confirm_yes$"))
application.add_handler(CallbackQueryHandler(handle_boost_buy_confirm_no, pattern="^boost_confirm_no$"))
application.add_handler(CallbackQueryHandler(handle_boost_status, pattern="^boost_status$"))

# Новые тарифы Boost
application.add_handler(CallbackQueryHandler(handle_boost_buy_14, pattern="^boost_buy_14$"))
application.add_handler(CallbackQueryHandler(handle_boost_buy_182, pattern="^boost_buy_182$"))
application.add_handler(CallbackQueryHandler(handle_boost_buy_365, pattern="^boost_buy_365$"))
application.add_handler(CallbackQueryHandler(handle_boost_confirm_14_yes, pattern="^boost_confirm_14_yes$"))
application.add_handler(CallbackQueryHandler(handle_boost_confirm_182_yes, pattern="^boost_confirm_182_yes$"))
application.add_handler(CallbackQueryHandler(handle_boost_confirm_365_yes, pattern="^boost_confirm_365_yes$"))
application.add_handler(CallbackQueryHandler(handle_boost_confirm_no, pattern="^boost_confirm_14_no$"))
application.add_handler(CallbackQueryHandler(handle_boost_confirm_no, pattern="^boost_confirm_182_no$"))
application.add_handler(CallbackQueryHandler(handle_boost_confirm_no, pattern="^boost_confirm_365_no$"))

# Единое меню фильтров
application.add_handler(CallbackQueryHandler(handle_filters_difficulty, pattern="^filters_difficulty$"))
application.add_handler(CallbackQueryHandler(handle_filters_type, pattern="^filters_type$"))
application.add_handler(CallbackQueryHandler(handle_filters_gender, pattern="^filters_gender$"))
application.add_handler(CallbackQueryHandler(handle_filters_weight, pattern="^filters_weight$"))

# Премиальные 🗯
application.add_handler(CallbackQueryHandler(handle_filters_photo, pattern="^filters_photo$"))
application.add_handler(CallbackQueryHandler(handle_filters_status, pattern="^filters_status$"))
application.add_handler(CallbackQueryHandler(handle_filters_status_set, pattern="^filters_status_set_"))
application.add_handler(CallbackQueryHandler(handle_filters_city, pattern="^filters_city$"))
application.add_handler(CallbackQueryHandler(handle_filters_popular, pattern="^filters_popular$"))
application.add_handler(CallbackQueryHandler(handle_filters_city_country_page, pattern=r"^filters_city_country_page_"))
application.add_handler(CallbackQueryHandler(handle_filters_city_country, pattern=r"^filters_city_country_"))
application.add_handler(CallbackQueryHandler(handle_filters_city_set_page, pattern=r"^filters_city_set_page_"))
application.add_handler(CallbackQueryHandler(handle_filters_city_set, pattern=r"^filters_city_set_"))
application.add_handler(CallbackQueryHandler(handle_filters_city_clear, pattern=r"^filters_city_clear$"))

# Установка значений
application.add_handler(CallbackQueryHandler(handle_photo_set,   pattern=r"^photo_set_(yes|no|any)$"))
application.add_handler(CallbackQueryHandler(handle_popular_set, pattern=r"^popular_set_(yes|no|any)$"))

# noop на лейблы (если ещё не добавлял)
application.add_handler(CallbackQueryHandler(handle_noop, pattern=r"^noop$"))

# ============ TELEGRAM STARS PAYMENT HANDLERS ============
application.add_handler(CallbackQueryHandler(handle_buy_chalk_callback, pattern="^buy_chalk_"))
application.add_handler(CallbackQueryHandler(handle_buy_founder_callback, pattern="^buy_founder$"))
application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

# Callback для быстрого перехода к Встречам из "За объявления"
application.add_handler(CallbackQueryHandler(menu_board, pattern="^menu_board$"))

# Фото
application.add_handler(MessageHandler(filters.PHOTO, unified_photo_handler))

# Остальные текстовые сообщения
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_messages))

def custom_exception_handler(loop, context):
    """Кастомный обработчик исключений asyncio для предотвращения рекурсии"""
    exception = context.get('exception')
    message = context.get('message', 'No message')

    if exception:
        print(f"⚠️ Asyncio exception: {type(exception).__name__}: {exception}")
    else:
        print(f"⚠️ Asyncio error: {message}")

if __name__ == "__main__":
    print("✅ Бот стартует как background worker...")
    prepare_db_init()  # Sync connection для database init
    create_tables()
    run_migrations()  # Применяем schema migrations

    # Закрываем init connection - больше не нужен
    if init_conn:
        init_cursor.close()
        init_conn.close()
        print("✅ Init DB connection closed (sync connection no longer needed)")

    # Устанавливаем кастомный exception handler для предотвращения RecursionError
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_exception_handler(custom_exception_handler)

    try:
        print("🚀 Запуск polling...")
        # drop_pending_updates=True - очищает очередь апдейтов при старте
        # Это предотвращает конфликты при перезапуске бота
        application.run_polling(
            allowed_updates=Update.ALL_TYPES, 
            timeout=10,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        print("\n✅ Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка при запуске бота: {e}")
        sys.exit(1)
