# database.py - База данных товаров с безопасными названиями
BOT_TOKEN = "8526771683:AAHVuIMkyrZ9atsnIMOpOYfeOubLtQQmz-E"

# ========== НАСТРОЙКИ БЕЗОПАСНОСТИ ==========
SECURITY_SETTINGS = {
    "max_messages_per_minute": 10,  # Максимум сообщений в минуту
    "captcha_timeout": 30,  # Время на решение капчи (секунды)
    "auto_cleanup_hours": 24,  # Автоочистка данных (часы)
    "min_order_for_deposit": 10000,  # Минимальная сумма для залога
    "deposit_percentage": 30,  # Процент предоплаты от суммы
    "large_order_threshold": 20000,  # Порог для большого заказа
    "large_deposit_percentage": 50  # Процент предоплаты для больших заказов
}

class NameCrypto:
    """Шифрование названий для безопасности"""
    def __init__(self):
        self.cipher_map = {}
        self.reverse_map = {}
        self._init_maps()
    
    def _init_maps(self):
        # Реальные названия -> Безопасные названия
        encrypted_map = {
            # Мефедрон и аналоги
            "Мефедрон Кристаллы": "🔥 M€f€dr0n Crystal Premium",
            "Розовый Меф": "🌹 Pink M3ph Deluxe",
            "Альфа-PVP Соль": "⚡ Alpha-PVP Salt Pro",
            
            # Кокаин
            "Перуанский Кокс": "💎 Peruvian Premium",
            "Кокаин Bolivia": "❄️ Bolivia Special",
            
            # Героин
            "Белый Героин": "⚪ White Dragon",
            
            # Каннабис
            "Марокканский Гашиш": "🌿 Moroccan Gold 4*",
            "Шишки Gorilla Glue": "🐵 Gorilla Glue OG",
            "Амнезия Haze": "🌀 Amnesia Haze XXL",
            
            # Амфетамины
            "Спид Паста": "⚡ Speed Paste Pro",
            "Амф Кристалл": "💎 Amphetamine Crystal",
            
            # МДМА и экстази
            "МДМА Кристаллы": "💎 MDMA Crystal Pure",
            "Экстази Голубой": "💙 Blue Punisher",
            "Оранжевый МДМА": "🧡 Orange Tesla",
            
            # Психоделики
            "ЛСД-25 250мкг": "🌈 LSD-25 Blotter",
            "2C-B 25мг": "🎭 2C-B Capsule",
            "Грибы Псилоцибин": "🍄 Magic Mushrooms",
            
            # Диссоциативы
            "Кетамин Вет": "💉 Ketamine Vet",
            
            # Фарма
            "Ксанакс 2мг": "💊 Xanax Bar",
            
            # Эксклюзив
            "Золотой Стандарт": "👑 Golden Standard",
            "Чёрный Жемчуг": "⚫ Black Pearl",
            
            # Комбо
            "Трип-комбо 2C-B+K": "🎪 Combo 2C-B+K",
            "Лин Коктейль": "🍹 Purple Drank"
        }
        
        self.cipher_map = encrypted_map
        self.reverse_map = {v: k for k, v in encrypted_map.items()}
    
    def encrypt_name(self, real_name):
        return self.cipher_map.get(real_name, real_name)
    
    def decrypt_name(self, safe_name):
        return self.reverse_map.get(safe_name, safe_name)

# Инициализируем шифровальщик названий
name_crypto = NameCrypto()

# Коэффициенты городов
CITY_COEFFICIENTS = {
    "Москва": 1.0,
    "Санкт-Петербург": 1.1,
    "Екатеринбург": 0.9,
    "Новосибирск": 1.05,
    "Казань": 0.95,
    "Сочи": 1.2,
    "Краснодар": 1.0,
    "Нижний Новгород": 0.95,
    "Ростов-на-Дону": 1.0
}

# База товаров
PRODUCTS = {
    # Мефедрон
    "Мефедрон Кристаллы": {
        "safe_name": name_crypto.encrypt_name("Мефедрон Кристаллы"),
        "base_price": 3800,
        "desc": "Кристаллы высшей очистки 98%",
        "full_description": "Премиум кристаллы европейского производства. Чистота 98%. Эффект: мощная эйфория, прилив энергии.",
        "effects": "Эйфория, энергия, общительность",
        "duration": "4-6 часов",
        "purity": "98%",
        "category": "стимуляторы",
        "is_hot": True,
        "emoji": "🔥",
        "dosage": "Начальная: 10-30мг"
    },
    
    "Розовый Меф": {
        "safe_name": name_crypto.encrypt_name("Розовый Меф"),
        "base_price": 3500,
        "desc": "Розовые кристаллы премиум качества",
        "full_description": "Специальная розовая рецептура для мягкого эффекта и усиления тактильных ощущений.",
        "effects": "Тактильность, эйфория, желание",
        "duration": "3-5 часов",
        "purity": "96%",
        "category": "стимуляторы",
        "is_hot": True,
        "emoji": "🌹",
        "dosage": "Начальная: 15-40мг"
    },
    
    # Кокаин
    "Перуанский Кокс": {
        "safe_name": name_crypto.encrypt_name("Перуанский Кокс"),
        "base_price": 8200,
        "desc": "Кокаин высшей пробы 90%+",
        "full_description": "Эксклюзивный перуанский кокаин. Максимальная чистота, проверенное качество.",
        "effects": "Уверенность, ясность, анестезия",
        "duration": "40-60 минут",
        "purity": "90%+",
        "category": "премиум",
        "is_hot": True,
        "emoji": "💎",
        "dosage": "Дорожка: 20-50мг"
    },
    
    # Каннабис
    "Марокканский Гашиш": {
        "safe_name": name_crypto.encrypt_name("Марокканский Гашиш"),
        "base_price": 1800,
        "desc": "Пресованный гашиш 4* качества",
        "full_description": "Традиционный марроканский гашиш ручной прессовки. Натуральный продукт.",
        "effects": "Расслабление, креативность, аппетит",
        "duration": "2-4 часа",
        "purity": "4 звезды",
        "category": "каннабис",
        "is_hot": False,
        "emoji": "🌿",
        "dosage": "На человека: 0.2-0.5г"
    },
    
    "Шишки Gorilla Glue": {
        "safe_name": name_crypto.encrypt_name("Шишки Gorilla Glue"),
        "base_price": 2200,
        "desc": "Индика с THC 24-28%",
        "full_description": "Гибридный сорт Gorilla Glue #4. Мощный расслабляющий эффект.",
        "effects": "Расслабление, седация, сонливость",
        "duration": "2-5 часов",
        "purity": "THC 24-28%",
        "category": "каннабис",
        "is_hot": False,
        "emoji": "🐵",
        "dosage": "На человека: 0.1-0.3г"
    },
    
    # Амфетамины
    "Спид Паста": {
        "safe_name": name_crypto.encrypt_name("Спид Паста"),
        "base_price": 1600,
        "desc": "Амфетамин паста для концентрации",
        "full_description": "Классический амфетамин для работы и учебы. Улучшает концентрацию.",
        "effects": "Концентрация, бодрость, многословие",
        "duration": "4-8 часов",
        "purity": "Чистая",
        "category": "стимуляторы",
        "is_hot": False,
        "emoji": "⚡",
        "dosage": "20-60мг"
    },
    
    # МДМА
    "МДМА Кристаллы": {
        "safe_name": name_crypto.encrypt_name("МДМА Кристаллы"),
        "base_price": 5200,
        "desc": "Кристаллический МДМА 84%+",
        "full_description": "Высокоочищенный МДМА в кристаллической форме. Чистый эмпатогенный эффект.",
        "effects": "Эмпатия, любовь, тактильность",
        "duration": "4-6 часов",
        "purity": "84%+",
        "category": "энтактогены",
        "is_hot": True,
        "emoji": "💎",
        "dosage": "80-150мг"
    },
    
    # Психоделики
    "ЛСД-25 250мкг": {
        "safe_name": name_crypto.encrypt_name("ЛСД-25 250мкг"),
        "base_price": 2800,
        "desc": "Промокашки с точной дозировкой",
        "full_description": "ЛСД-25 на промокашках, 250мкг. Для психоделических путешествий.",
        "effects": "Визуалы, изменение мышления, синестезия",
        "duration": "8-12 часов",
        "purity": "250мкг",
        "category": "психоделики",
        "is_hot": False,
        "emoji": "🌈",
        "dosage": "1/4-1/2 промокашки"
    },
    
    # Фарма
    "Ксанакс 2мг": {
        "safe_name": name_crypto.encrypt_name("Ксанакс 2мг"),
        "base_price": 1200,
        "desc": "Алпразолам для снятия тревоги",
        "full_description": "Фармацевтический алпразолам 2мг. Только по необходимости.",
        "effects": "Снятие тревоги, релаксация, сон",
        "duration": "6-8 часов",
        "purity": "2мг",
        "category": "фарма",
        "is_hot": False,
        "emoji": "💊",
        "dosage": "0.5-2мг"
    },
    
    # Эксклюзив
    "Золотой Стандарт": {
        "safe_name": name_crypto.encrypt_name("Золотой Стандарт"),
        "base_price": 9500,
        "desc": "Мефедрон 99.9% очистки",
        "full_description": "Эксклюзивная партия максимальной очистки. Минимум побочных эффектов.",
        "effects": "Чистая эйфория, плавный отход",
        "duration": "3-4 часа",
        "purity": "99.9%",
        "category": "эксклюзив",
        "is_hot": False,
        "emoji": "👑",
        "dosage": "20-80мг"
    }
}

# Функции для работы с товарами
def get_safe_product_name(product_key):
    """Получить безопасное название продукта"""
    if product_key in PRODUCTS:
        return PRODUCTS[product_key].get("safe_name", product_key)
    return product_key

def get_real_product_name(safe_name):
    """Получить настоящее название по безопасному"""
    for product_key, data in PRODUCTS.items():
        if data.get("safe_name") == safe_name:
            return product_key
    return safe_name

def get_product_by_safe_name(safe_name):
    """Получить данные продукта по безопасному названию"""
    for product_key, data in PRODUCTS.items():
        if data.get("safe_name") == safe_name:
            return data
    return None

def get_product_by_real_name(real_name):
    """Получить данные продукта по настоящему названию"""
    return PRODUCTS.get(real_name)

# Крипто-кошельки
CRYPTO_WALLETS = {
    "BTC": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "ETH": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "USDT": "TQt6Ffn9hxKFuzgVGtGv8H1k9BHFj7JqjS",
    "TON": "UQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqEBI"
}