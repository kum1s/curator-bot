# bot.py - Основной файл бота
import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters, CallbackQueryHandler
import database as db

# Используем токен из database
TOKEN = db.BOT_TOKEN

# Этапы разговора
CITY, PRODUCT, WEIGHT, DELIVERY, DEPOSIT, CONFIRM, CAPTCHA = range(7)

# Данные пользователей
user_data = {}
captcha_data = {}
captcha_timers = {}  # Для хранения времени создания капчи

# Защита от флуда
login_attempts = {}
user_activity = {}

# Настройки логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ========== ОПИСАНИЯ ВАКАНСИЙ ==========
JOB_DESCRIPTIONS = {
    "🚴 Курьер": (
        "🚴 КУРЬЕР\n\n"
        "Суть работы — быстрая и безопасная доставка продукции по указанным адресам.\n\n"
        "📋 Условия работы:\n"
        "• Оплата: от 150.000₽ до 250.000₽ в месяц\n"
        "• График: свободный, 2-4 часа в день\n"
        "• Выплаты: ежедневно на карту/крипту\n"
        "• Бонусы: +15% за работу в выходные\n"
        "• Опыт: не требуется, обучаем за 1 день\n\n"
        "🛡️ Гарантии безопасности:\n"
        "• Полная анонимность\n"
        "• Юридическая защита при любых ситуациях\n"
        "• Все расходы на адвоката — за наш счёт\n"
        "• Страховка на случай форс-мажора\n\n"
        "🔐 Требования для начала:\n"
        "ВЫБЕРИТЕ ОДИН ИЗ ВАРИАНТОВ:\n"
        "1. 📸 Фото-верификация:\n"
        "   • Ваше селфи с паспортом\n"
        "   • Рядом листок с надписью 'Curator's Choice'\n"
        "   • Чётко видно лицо и данные паспорта\n\n"
        "2. 💵 Страховой депозит: 4.500₽\n"
        "   • Возвращается после первого месяца работы\n"
        "   • Гарантия вашей ответственности\n\n"
        "📞 Для старта напишите свой город: @curator_hr"
    ),
    
    "👨‍🎨 Трафаретчик": (
        "👨‍🎨 ТРАФАРЕТЧИК\n\n"
        "Суть работы — нанесение рисунка/наклейки на проходимые места, фотографирование граффити/стикера.\n\n"
        "📋 Условия оплаты:\n"
        "• Граффити: от 110₽ за штуку\n"
        "• Стикер: от 50₽ за штуку\n"
        "• Минимальная выплата: от 20 граффити или 50 стикеров\n"
        "• Выплаты: раз в 3 дня на карту\n"
        "• Опыт: не требуется\n\n"
        "🎨 Что нужно делать:\n"
        "1. Получаете текст/рисунок от оператора\n"
        "2. Наносите в проходимых местах города\n"
        "3. Фотографируете через приложение NoteCam\n"
        "4. Отправляете фото оператору\n"
        "5. Получаете оплату\n\n"
        "💰 Компенсация расходов:\n"
        "• Сохраняйте чеки на краску/стикеры\n"
        "• Все расходы компенсируем при первой выплате\n\n"
        "📞 Для начала работы напишите свой город оператору: @curator_hr"
    ),
    
    "🚗 Водитель": (
        "🚗 ВОДИТЕЛЬ\n\n"
        "Логистика и транспортное обслуживание операций.\n\n"
        "📋 Условия работы:\n"
        "• Оплата: 200.000₽ - 350.000₽ в месяц\n"
        "• График: 3-4 часа в день\n"
        "• Автомобиль: предоставляем (после стажировки)\n"
        "• Топливо: за наш счёт\n"
        "• Выплаты: ежедневно\n\n"
        "🔐 Требования для старта:\n"
        "• Залог 8.000₽ за оборудование (топливная карта + навигатор)\n"
        "• Возвращается через 2 недели работы\n"
        "• Водительские права категории B\n"
        "• Трезвый образ жизни\n\n"
        "🛡️ Гарантии:\n"
        "• Полная анонимность\n"
        "• Страхование\n"
        "• Подмена авто при поломке\n\n"
        "📞 Для трудоустройства: @curator_hr"
    ),
    
    "✅ Верификатор": (
        "✅ ВЕРИФИКАТОР\n\n"
        "Проверка информации, клиентов и транзакций.\n\n"
        "📋 Требования:\n"
        "• Опыт в сфере: от 3 месяцев\n"
        "• Знание основных правил безопасности\n"
        "• Внимательность к деталям\n"
        "• Ответственность\n\n"
        "💰 Условия:\n"
        "• Оплата: 120.000₽ - 180.000₽ в месяц\n"
        "• Удалённая работа\n"
        "• Гибкий график\n"
        "• Выплаты: 2 раза в неделю\n\n"
        "🔐 Для доступа к системе:\n"
        "• Оплата доступа к базе: 3.000₽ (единоразово)\n"
        "• Обучение: бесплатно\n\n"
        "📞 Резюме отправлять: @curator_hr"
    ),
    
    "📞 Оператор": (
        "📞 ОПЕРАТОР\n\n"
        "Работа с клиентами, консультации, обработка заказов.\n\n"
        "📋 Требования:\n"
        "• Опыт в сфере: от 6 месяцев\n"
        "• Грамотная речь и письмо\n"
        "• Стрессоустойчивость\n"
        "• Умение решать конфликты\n\n"
        "💰 Условия:\n"
        "• Оплата: 140.000₽ - 200.000₽ + бонусы\n"
        "• Удалённая работа\n"
        "• Сменный график (4-6 часов в день)\n"
        "• Процент от продаж\n\n"
        "🎓 Обучение:\n"
        "• Платный курс: 5.000₽ (очно или онлайн)\n"
        "• Длительность: 3 дня\n"
        "• Сертификат по окончании\n\n"
        "📞 Запись на обучение: @curator_hr"
    ),
    
    "👨‍💼 Менеджер": (
        "👨‍💼 МЕНЕДЖЕР\n\n"
        "Управление командой, контроль процессов, развитие направления.\n\n"
        "📋 Требования:\n"
        "• Опыт в сфере: от 1 года\n"
        "• Лидерские качества\n"
        "• Организаторские способности\n"
        "• Знание рынка\n\n"
        "💰 Условия:\n"
        "• Оплата: 200.000₽ - 400.000₽ + процент\n"
        "• Карьерный рост до директора филиала\n"
        "• Премии за выполнение плана\n"
        "• Бонусы за развитие команды\n\n"
        "🔐 Для старта:\n"
        "• Вступительный взнос: 10.000₽ (доступ к клиентской базе и инструментам)\n"
        "• Возвращается после 3 месяцев работы\n\n"
        "📞 Обсудить условия: @curator_hr"
    )
}

# ========== БЕЗОПАСНОСТЬ ==========
def check_user_limit(user_id):
    """Проверяет лимит попыток входа"""
    now = datetime.now()
    if user_id not in login_attempts:
        login_attempts[user_id] = []
    
    # Удаляем старые попытки (старше 1 часа)
    login_attempts[user_id] = [t for t in login_attempts[user_id] if (now - t).seconds < 3600]
    
    # Если больше 5 попыток за час - блокируем на час
    if len(login_attempts[user_id]) >= 5:
        return False
    
    login_attempts[user_id].append(now)
    return True

def check_flood(user_id):
    """Проверяет флуд от пользователя"""
    now = datetime.now()
    if user_id not in user_activity:
        user_activity[user_id] = []
    
    # Удаляем старые сообщения (старше минуты)
    user_activity[user_id] = [t for t in user_activity[user_id] if (now - t).seconds < 60]
    
    # Если больше лимита в минуту - блокируем
    if len(user_activity[user_id]) >= db.SECURITY_SETTINGS["max_messages_per_minute"]:
        return False
    
    user_activity[user_id].append(now)
    return True

async def anti_flood_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE, next_handler):
    """Промежуточный обработчик для проверки флуда"""
    user_id = update.effective_user.id
    
    if not check_flood(user_id):
        if update.message:
            await update.message.reply_text(
                "⚠️ Слишком много запросов. Подождите 1 минуту."
            )
        return
    
    return await next_handler(update, context)

def generate_captcha():
    """Генерирует капчу с таймером"""
    num1 = random.randint(10, 50)
    num2 = random.randint(1, 20)
    operation = random.choice(['+', '-', '*'])
    
    if operation == '+':
        answer = num1 + num2
    elif operation == '-':
        answer = num1 - num2
    else:
        num1 = random.randint(2, 10)
        num2 = random.randint(2, 5)
        answer = num1 * num2
    
    question = f"{num1} {operation} {num2}"
    return question, str(answer)

# ========== КЛАВИАТУРЫ ==========
def get_main_menu():
    keyboard = [
        ["🏙️ Выбрать город", "📦 Каталог товаров"],
        ["💰 Прайс-лист", "⭐ Отзывы клиентов"],
        ["👥 Вакансии", "❓ Частые вопросы"],
        ["👨‍💼 Консультация", "🎁 Акции и бонусы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_cities_keyboard():
    keyboard = [
        ["🏙️ Москва", "🏙️ Санкт-Петербург", "🏙️ Екатеринбург"],
        ["🏙️ Новосибирск", "🏙️ Казань", "🏙️ Сочи"],
        ["🏙️ Краснодар", "🏙️ Нижний Новгород", "🏙️ Ростов-на-Дону"],
        ["⬅️ Главное меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_products_keyboard(city="Москва"):
    keyboard = []
    
    # Группируем товары по категориям
    categories = {}
    for name, info in db.PRODUCTS.items():
        category = info["category"]
        if category not in categories:
            categories[category] = []
        
        price = int(info["base_price"] * db.CITY_COEFFICIENTS.get(city, 1.0))
        display = f"{info.get('emoji', '📦')} {name}"
        categories[category].append((display, price))
    
    # Добавляем по 2-3 товара из каждой категории
    for category, products in categories.items():
        keyboard.append([f"📁 {category}"])
        for i in range(0, min(3, len(products))):
            display, price = products[i]
            keyboard.append([f"{display} - {price}₽/г"])
        keyboard.append(["─" * 20])
    
    keyboard.append(["⬅️ Главное меню"])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_jobs_keyboard():
    keyboard = [
        ["🚴 Курьер", "👨‍🎨 Трафаретчик", "🚗 Водитель"],
        ["✅ Верификатор", "📞 Оператор", "👨‍💼 Менеджер"],
        ["⬅️ Главное меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_weight_keyboard():
    keyboard = [
        ["0.5г", "1г", "2г"],
        ["3г", "5г", "10г"],
        ["Другое количество"],
        ["⬅️ Назад к товарам"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_delivery_keyboard():
    keyboard = [
        ["🚀 Срочная доставка (+1000₽)", "📦 Обычная доставка (бесплатно)"],
        ["⬅️ Назад к весу"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_deposit_keyboard():
    keyboard = [
        ["✅ Да, перейти к оплате предоплаты", "✏️ Изменить заказ"],
        ["❌ Отменить заказ", "⬅️ Главное меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_confirm_keyboard():
    keyboard = [
        ["✅ Подтвердить заказ", "✏️ Изменить данные"],
        ["❌ Отменить", "⬅️ Главное меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем лимит попыток
    if not check_user_limit(user_id):
        await update.message.reply_text(
            "⚠️ Слишком много попыток входа. Попробуйте через 1 час."
        )
        return ConversationHandler.END
    
    # Генерируем капчу с таймером
    question, answer = generate_captcha()
    captcha_data[user_id] = answer
    captcha_timers[user_id] = datetime.now()
    
    await update.message.reply_text(
        "🛡️ Curator's Choice — платформа премиум-качества\n\n"
        "🔐 Для продолжения решите пример для проверки (у вас 30 секунд):\n"
        f"❓ {question} = ?\n\n"
        "✏️ Отправьте ответ цифрами:"
    )
    return CAPTCHA

async def verify_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_answer = update.message.text.strip()
    
    if user_id not in captcha_data:
        await update.message.reply_text("❌ Ошибка проверки. Начните заново с /start")
        return ConversationHandler.END
    
    # Проверяем время
    if user_id in captcha_timers:
        time_passed = (datetime.now() - captcha_timers[user_id]).seconds
        if time_passed > db.SECURITY_SETTINGS["captcha_timeout"]:
            del captcha_data[user_id]
            del captcha_timers[user_id]
            await update.message.reply_text(
                "⏱️ Время вышло! Капча действует 30 секунд.\n"
                "Для нового примера отправьте /start"
            )
            return ConversationHandler.END
    
    correct_answer = captcha_data[user_id]
    
    if user_answer == correct_answer:
        del captcha_data[user_id]
        if user_id in captcha_timers:
            del captcha_timers[user_id]
        
        await update.message.reply_text(
            "✅ Проверка пройдена успешно!\n\n"
            "🌟 Curator's Choice — эксклюзивная платформа с индивидуальным подходом\n\n"
            "🎯 Основные направления:\n"
            "• Премиум сегмент\n" 
            "• Специальные предложения\n"
            "• Гарантия качества\n"
            "• Конфиденциальность\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Неверный ответ. Попробуйте еще раз.\n"
            "Для нового примера отправьте /start"
        )
        return ConversationHandler.END

# ========== ПРОЦЕСС ЗАКАЗА ==========
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📍 Выберите ваш город:\n\n"
        "• Москва — от 2 часов\n"
        "• Санкт-Петербург — от 2.5 часов\n"
        "• Екатеринбург — от 2 часов\n"
        "• Новосибирск — от 3 часов\n"
        "• Казань — от 1.5 часа\n"
        "• Сочи — 2-3 часа\n"
        "• Краснодар — от 2 часов\n"
        "• Нижний Новгород — от 2 часов\n"
        "• Ростов-на-Дону — от 2.5 часов\n\n"
        "⏱️ Время доставки указано ориентировочно",
        reply_markup=get_cities_keyboard()
    )
    return CITY

async def choose_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "⬅️ Главное меню":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    
    if "🏙️" in text:
        city = text.replace("🏙️ ", "")
        user_id = update.effective_user.id
        
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["city"] = city
        
        await update.message.reply_text(
            f"📍 Выбран город: {city}\n\n"
            "🎯 Выберите категорию товара:\n\n"
            "💎 — Премиум сегмент\n"
            "✨ — Эксклюзивные позиции\n"
            "🔥 — Специальные предложения\n"
            "🏷️ — Основной ассортимент",
            reply_markup=get_products_keyboard(city)
        )
        return PRODUCT
    
    await update.message.reply_text("Пожалуйста, выберите город из списка:")
    return CITY

async def choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "⬅️ Главное меню":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    
    if text == "⬅️ Назад к товарам":
        city = user_data.get(user_id, {}).get("city", "Москва")
        await update.message.reply_text(
            f"📍 Город: {city}\n\nВыберите товар:",
            reply_markup=get_products_keyboard(city)
        )
        return PRODUCT
    
    # Убираем эмодзи и цену для поиска
    product_name = text.split(" - ")[0] if " - " in text else text
    if "📁" not in product_name:  # Если это не заголовок категории
        product_name = product_name.split(" ", 1)[1] if " " in product_name else product_name
    else:
        await update.message.reply_text(
            "Выберите конкретный товар из списка:",
            reply_markup=get_products_keyboard(user_data.get(user_id, {}).get("city", "Москва"))
        )
        return PRODUCT
    
    city = user_data.get(user_id, {}).get("city", "Москва")
    
    product_info = None
    product_display_name = None
    
    for name, info in db.PRODUCTS.items():
        if name.lower() in product_name.lower() or product_name.lower() in name.lower():
            product_info = info
            product_display_name = name
            break
    
    if not product_info:
        await update.message.reply_text(
            "Товар не найден. Выберите из списка:",
            reply_markup=get_products_keyboard(city)
        )
        return PRODUCT
    
    user_data[user_id]["product"] = product_display_name
    user_data[user_id]["product_info"] = product_info
    
    base_price = product_info["base_price"]
    price = int(base_price * db.CITY_COEFFICIENTS.get(city, 1.0))
    user_data[user_id]["price_per_gram"] = price
    
    # Формируем подробное описание
    description = product_info.get('description', product_info['desc'])
    effects = product_info.get('effects', 'Индивидуально')
    duration = product_info.get('duration', 'Не указано')
    purity = product_info.get('purity', 'Высокая')
    
    await update.message.reply_text(
        f"🎯 {product_display_name}\n\n"
        f"📝 Описание:\n{description}\n\n"
        f"💫 Эффект: {effects}\n"
        f"⏱️ Длительность: {duration}\n"
        f"🧪 Чистота: {purity}\n"
        f"💰 Цена: {price}₽/г\n\n"
        "⚖️ Выберите количество:",
        reply_markup=get_weight_keyboard()
    )
    return WEIGHT

async def choose_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "⬅️ Назад к товарам":
        city = user_data.get(user_id, {}).get("city", "Москва")
        await update.message.reply_text(
            f"📍 Город: {city}\n\nВыберите товар:",
            reply_markup=get_products_keyboard(city)
        )
        return PRODUCT
    
    if text == "Другое количество":
        await update.message.reply_text("✏️ Введите количество грамм цифрами (например: 1.5 или 2):")
        return WEIGHT
    
    try:
        if text.endswith("г"):
            grams = float(text[:-1].replace(",", "."))
        else:
            grams = float(text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("❌ Некорректный формат. Введите число (например: 1.5 или 2):")
        return WEIGHT
    
    if grams <= 0:
        await update.message.reply_text("❌ Количество должно быть больше 0.")
        return WEIGHT
    
    if grams > 100:
        await update.message.reply_text("❌ Максимальный заказ — 100г. Для опта свяжитесь с менеджером.")
        return WEIGHT
    
    user_data[user_id]["grams"] = grams
    price = user_data[user_id]["price_per_gram"]
    subtotal = price * grams
    
    await update.message.reply_text(
        f"⚖️ Количество: {grams}г\n"
        f"💰 Сумма: {int(subtotal)}₽\n\n"
        "🚚 Выберите тип доставки:\n"
        "• 🚀 Срочная — +1000₽, в течение часа\n"
        "• 📦 Обычная — бесплатно, по графику\n\n"
        "Срочная доставка доступна не во всех районах.",
        reply_markup=get_delivery_keyboard()
    )
    return DELIVERY

async def choose_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "⬅️ Назад к весу":
        await update.message.reply_text(
            "⚖️ Выберите количество:",
            reply_markup=get_weight_keyboard()
        )
        return WEIGHT
    
    if "Срочная" in text:
        delivery_type = "Срочная"
        delivery_cost = 1000
    else:
        delivery_type = "Обычная"
        delivery_cost = 0
    
    user_data[user_id]["delivery"] = delivery_type
    user_data[user_id]["delivery_cost"] = delivery_cost
    
    data = user_data[user_id]
    price = data["price_per_gram"]
    grams = data["grams"]
    subtotal = price * grams
    total = int(subtotal + delivery_cost)
    user_data[user_id]["total"] = total
    user_data[user_id]["subtotal"] = subtotal
    
    # Проверяем, нужен ли залог
    if total >= db.SECURITY_SETTINGS["min_order_for_deposit"]:
        if total >= db.SECURITY_SETTINGS["large_order_threshold"]:
            percentage = db.SECURITY_SETTINGS["large_deposit_percentage"]
        else:
            percentage = db.SECURITY_SETTINGS["deposit_percentage"]
        
        deposit_amount = int(total * percentage / 100)
        user_data[user_id]["deposit_required"] = True
        user_data[user_id]["deposit_amount"] = deposit_amount
        user_data[user_id]["deposit_percentage"] = percentage
        
        await update.message.reply_text(
            f"📋 СВОДКА ЗАКАЗА\n\n"
            f"📍 Город: {data['city']}\n"
            f"🎯 Товар: {data['product']}\n"
            f"⚖️ Вес: {grams}г\n"
            f"💰 Цена за грамм: {price}₽\n"
            f"📦 Доставка: {delivery_type} ({delivery_cost}₽)\n"
            f"💵 ИТОГО: {total}₽\n\n"
            f"⚠️ ТРЕБУЕТСЯ ПРЕДОПЛАТА\n"
            f"• Сумма заказа: {total}₽\n"
            f"• Предоплата: {percentage}% ({deposit_amount}₽)\n"
            f"• К оплате сейчас: {deposit_amount}₽\n"
            f"• Остаток курьеру: {total - deposit_amount}₽\n\n"
            f"📝 Причина: безопасность при заказах от {db.SECURITY_SETTINGS['min_order_for_deposit']}₽\n\n"
            f"Продолжить с предоплатой?",
            reply_markup=get_deposit_keyboard()
        )
        return DEPOSIT
    else:
        user_data[user_id]["deposit_required"] = False
        user_data[user_id]["deposit_amount"] = 0
        
        await update.message.reply_text(
            f"📋 СВОДКА ЗАКАЗА\n\n"
            f"📍 Город: {data['city']}\n"
            f"🎯 Товар: {data['product']}\n"
            f"⚖️ Вес: {grams}г\n"
            f"💰 Цена за грамм: {price}₽\n"
            f"📦 Доставка: {delivery_type} ({delivery_cost}₽)\n"
            f"💵 ИТОГО: {total}₽\n\n"
            "Подтвердите заказ:",
            reply_markup=get_confirm_keyboard()
        )
        return CONFIRM

async def handle_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if "✏️ Изменить" in text:
        city = user_data.get(user_id, {}).get("city", "Москва")
        await update.message.reply_text(
            f"📍 Город: {city}\n\nВыберите товар:",
            reply_markup=get_products_keyboard(city)
        )
        return PRODUCT
    
    if "❌ Отменить" in text:
        await update.message.reply_text(
            "❌ Заказ отменен.\nВозвращаю в главное меню:",
            reply_markup=get_main_menu()
        )
        if user_id in user_data:
            del user_data[user_id]
        return ConversationHandler.END
    
    if "⬅️ Главное меню" in text:
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
        if user_id in user_data:
            del user_data[user_id]
        return ConversationHandler.END
    
    if "✅ Да" in text:
        data = user_data[user_id]
        
        order_id = f"CC-{user_id % 10000:04d}-{datetime.now().strftime('%H%M')}"
        deposit = data["deposit_amount"]
        remaining = data["total"] - deposit
        
        order_text = (
            f"✅ ТРЕБУЕТСЯ ПРЕДОПЛАТА\n\n"
            f"📋 Заказ №{order_id}\n"
            f"📍 Город: {data['city']}\n"
            f"🎯 Товар: {data['product']}\n"
            f"⚖️ Вес: {data['grams']}г\n"
            f"📦 Доставка: {data['delivery']}\n"
            f"💰 Общая сумма: {data['total']}₽\n\n"
            f"💳 ДЛЯ ОПЛАТЫ ПРЕДОПЛАТЫ:\n"
            f"• BTC: {db.CRYPTO_WALLETS['BTC']}\n"
            f"• ETH: {db.CRYPTO_WALLETS['ETH']}\n"
            f"• USDT (TRC20): {db.CRYPTO_WALLETS['USDT']}\n"
            f"• TON: {db.CRYPTO_WALLETS['TON']}\n\n"
            f"⚠️ ВАЖНО:\n"
            f"1. Оплатите ТОЛЬКО предоплату: {deposit}₽\n"
            f"2. Остаток ({remaining}₽) — курьеру при получении\n"
            f"3. Отправьте чек менеджеру @curator_support\n"
            f"4. Укажите номер заказа: {order_id}\n\n"
            f"⏱️ Резерв: 30 минут\n"
            f"📞 Поддержка: @curator_support\n\n"
            f"После оплаты с вами свяжется курьер для уточнения деталей."
        )
        
        await update.message.reply_text(
            order_text,
            reply_markup=get_main_menu()
        )
        
        if user_id in user_data:
            del user_data[user_id]
        
        return ConversationHandler.END
    
    return DEPOSIT

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if "⬅️ Главное меню" in text:
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
        if user_id in user_data:
            del user_data[user_id]
        return ConversationHandler.END
    
    if "✏️ Изменить" in text:
        city = user_data.get(user_id, {}).get("city", "Москва")
        await update.message.reply_text(
            f"📍 Город: {city}\n\nВыберите товар:",
            reply_markup=get_products_keyboard(city)
        )
        return PRODUCT
    
    if "❌ Отменить" in text:
        await update.message.reply_text(
            "❌ Заказ отменен.\nВозвращаю в главное меню:",
            reply_markup=get_main_menu()
        )
        if user_id in user_data:
            del user_data[user_id]
        return ConversationHandler.END
    
    if "✅ Подтвердить" in text:
        data = user_data.get(user_id, {})
        
        if not data:
            await update.message.reply_text("❌ Ошибка данных. Начните заново.", reply_markup=get_main_menu())
            return ConversationHandler.END
        
        # Формируем номер заказа
        order_id = f"CC-{user_id % 10000:04d}-{datetime.now().strftime('%H%M')}"
        
        order_text = (
            f"✅ ЗАКАЗ №{order_id} ПОДТВЕРЖДЕН!\n\n"
            f"📋 Детали заказа:\n"
            f"📍 Город: {data['city']}\n"
            f"🎯 Товар: {data['product']}\n"
            f"⚖️ Вес: {data['grams']}г\n"
            f"📦 Доставка: {data['delivery']}\n"
            f"💵 К ОПЛАТЕ: {data['total']}₽\n\n"
            f"💳 ДЛЯ ОПЛАТЫ:\n"
            f"• BTC: {db.CRYPTO_WALLETS['BTC']}\n"
            f"• ETH: {db.CRYPTO_WALLETS['ETH']}\n"
            f"• USDT (TRC20): {db.CRYPTO_WALLETS['USDT']}\n"
            f"• TON: {db.CRYPTO_WALLETS['TON']}\n\n"
            f"⚠️ ВАЖНО:\n"
            f"1. Оплатите сумму {data['total']}₽\n"
            f"2. Отправьте чек менеджеру\n"
            f"3. Укажите номер заказа: {order_id}\n"
            f"4. После оплаты свяжется курьер\n\n"
            f"⏱️ Резерв: 30 минут\n"
            f"📞 Для связи: @curator_support\n\n"
            f"Благодарим за выбор Curator's Choice! 🌟"
        )
        
        await update.message.reply_text(
            order_text,
            reply_markup=get_main_menu()
        )
        
        if user_id in user_data:
            del user_data[user_id]
        
        return ConversationHandler.END
    
    return CONFIRM

# ========== ВАКАНСИИ ==========
async def show_jobs_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👥 СВОБОДНЫЕ ВАКАНСИИ\n\n"
        "Мы предлагаем стабильную работу с гарантированными выплатами и полной безопасностью.\n\n"
        "💼 Доступные позиции:\n"
        "• 🚴 Курьер — от 150.000₽/мес\n"
        "• 👨‍🎨 Трафаретчик — от 110₽ за граффити\n"
        "• 🚗 Водитель — от 200.000₽/мес\n"
        "• ✅ Верификатор — от 120.000₽/мес\n"
        "• 📞 Оператор — от 140.000₽/мес\n"
        "• 👨‍💼 Менеджер — от 200.000₽/мес\n\n"
        "Выберите вакансию для подробностей:",
        reply_markup=get_jobs_keyboard()
    )

async def show_job_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job = update.message.text
    user_id = update.effective_user.id
    
    if job in JOB_DESCRIPTIONS:
        await update.message.reply_text(
            JOB_DESCRIPTIONS[job],
            reply_markup=get_jobs_keyboard(),
            parse_mode='HTML'
        )
    elif job == "⬅️ Главное меню":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )

# ========== ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ==========
async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    city = user_data.get(user_id, {}).get("city", "Москва")
    
    await update.message.reply_text(
        f"📦 КАТАЛОГ ТОВАРОВ ({city})\n\n"
        "Выберите категорию для просмотра:\n\n"
        "💎 Премиум сегмент — эксклюзивные позиции\n"
        "✨ Эксклюзив — редкие предложения\n"
        "🔥 Акции — специальные условия\n"
        "🏷️ Основное — постоянный ассортимент\n\n"
        "Для оформления заказа нажмите 'Выбрать город'",
        reply_markup=get_products_keyboard(city)
    )

async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💰 ПРАЙС-ЛИСТ (средние цены за грамм)\n\n"
    
    popular_products = [
        "Перуанский Кокс",
        "Мефедрон Кристаллы",
        "Марокканский Гашиш",
        "Спид Паста",
        "ЛСД-25 250мкг"
    ]
    
    for product_name in popular_products:
        if product_name in db.PRODUCTS:
            base_price = db.PRODUCTS[product_name]["base_price"]
            
            text += f"📦 {product_name[:20]}\n"
            
            for city in ["Москва", "Санкт-Петербург", "Екатеринбург", "Новосибирск"]:
                price = int(base_price * db.CITY_COEFFICIENTS.get(city, 1.0))
                text += f"• {city}: {price}₽ "
            
            text += "\n\n"
    
    text += "📌 Примечание:\n"
    text += "• Цены зависят от города доставки\n"
    text += "• Точная стоимость при оформлении заказа\n"
    text += "• Действуют акции и скидки"
    
    await update.message.reply_text(
        text,
        reply_markup=get_main_menu()
    )

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reviews = (
        "⭐ ОТЗЫВЫ КЛИЕНТОВ\n\n"
        
        "🔸 О КАЧЕСТВЕ:\n"
        "«Постоянно заказываю, всегда стабильное качество» — 05.10\n"
        "«Лучшее соотношение цена/качество» — 03.10\n"
        "«Отличный сервис и продукт» — 01.10\n\n"
        
        "🔸 О ДОСТАВКЕ:\n"
        "«Всегда вовремя, курьер вежливый» — 28.09\n"
        "«Быстрая доставка, все четко» — 26.09\n"
        "«Работают в любую погоду» — 22.09\n\n"
        
        "🔸 О СЕРВИСЕ:\n"
        "«Менеджер всегда на связи, помогают» — 12.10\n"
        "«Решают любые вопросы быстро» — 08.10\n"
        "«Профессиональный подход» — 30.09\n\n"
        
        "📊 ПОКАЗАТЕЛИ:\n"
        "• 97% довольных клиентов\n"
        "• 2.1 часа — среднее время\n"
        "• 24/7 — работа поддержки\n\n"
        
        "Мы ценим конфиденциальность наших клиентов."
    )
    await update.message.reply_text(
        reviews,
        reply_markup=get_main_menu()
    )

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faq = (
        "❓ ЧАСТЫЕ ВОПРОСЫ\n\n"
        
        "⚡ О ЗАКАЗАХ:\n"
        "• Как сделать заказ?\n"
        "Выберите город → товар → количество → доставку → подтвердите → оплатите → отправьте чек\n\n"
        
        "• Есть ли минимальный заказ?\n"
        "Минимальный заказ — 0.5г для большинства позиций\n\n"
        
        "🚚 О ДОСТАВКЕ:\n"
        "• Какие районы обслуживаете?\n"
        "Все основные районы города. Уточняйте у менеджера\n\n"
        
        "• Что делать если проблема с доставкой?\n"
        "Сразу свяжитесь с поддержкой, решим вопрос\n\n"
        
        "💰 ОПЛАТА:\n"
        "• Какие способы оплаты?\n"
        "Криптовалюта: BTC, ETH, USDT, TON\n\n"
        
        "🔒 БЕЗОПАСНОСТЬ:\n"
        "• Гарантии конфиденциальности?\n"
        "Полная анонимность, не храним данные\n\n"
        
        "🎁 БОНУСЫ:\n"
        "• Есть ли скидки?\n"
        "Да, для постоянных клиентов и при объемных заказах\n"
    )
    await update.message.reply_text(
        faq,
        reply_markup=get_main_menu()
    )

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support = (
        "👨‍💼 КОНСУЛЬТАЦИЯ\n\n"
        "По вопросам заказов, оплаты, доставки:\n"
        "➡️ @curator_support\n\n"
        "⏰ Режим работы: круглосуточно\n"
        "⏱️ Время ответа: до 5 минут\n\n"
        "📞 Только Telegram\n"
        "💬 Конфиденциально"
    )
    await update.message.reply_text(
        support,
        reply_markup=get_main_menu()
    )

async def show_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bonus = (
        "🎁 АКЦИИ И БОНУСЫ\n\n"
        "• Приведи друга — +10% к заказу\n"
        "• Каждый 5-й заказ — скидка 15%\n"
        "• Заказы от 20г — VIP статус\n"
        "• В VIP клубе:\n"
        "  — Эксклюзивные предложения\n"
        "  — Персональный менеджер\n"
        "  — Приоритетная доставка\n\n"
        "Условия уточняйте у поддержки."
    )
    await update.message.reply_text(
        bonus,
        reply_markup=get_main_menu()
    )

# ========== КОМАНДА PANIC ==========
async def panic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экстренное отключение бота"""
    user_id = update.effective_user.id
    
    # ID администратора (замени на свой)
    ADMIN_IDS = [8250943565]  # Замени на свой Telegram ID
    
    if user_id in ADMIN_IDS:
        try:
            # Пытаемся удалить команду
            await update.message.delete()
            
            # Пытаемся удалить несколько последних сообщений
            for i in range(5):
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=update.message.message_id - i - 1
                    )
                except:
                    continue
        except:
            pass
        
        # Очищаем данные
        user_data.clear()
        captcha_data.clear()
        captcha_timers.clear()
        login_attempts.clear()
        user_activity.clear()
        
        await update.message.reply_text(
            "🛡️ Режим паники активирован.\n"
            "• Данные очищены\n"
            "• История удалена\n"
            "• Бот продолжает работу\n\n"
            "Для восстановления полного функционала перезапустите бота."
        )
        return
    
    await update.message.reply_text("⛔ Команда недоступна.")

# ========== ФИКТИВНОЕ МЕНЮ ПРИ ПРОВЕРКАХ ==========
async def fake_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фиктивное меню для проверок"""
    keyboard = [
        ["📚 Каталог книг", "🎁 Сувениры"],
        ["🖼️ Картины", "📿 Украшения"],
        ["ℹ️ О нас", "📞 Контакты"]
    ]
    
    await update.message.reply_text(
        "📚 Добро пожаловать в магазин книг и сувениров!\n\n"
        "Мы предлагаем:\n"
        "• Художественная литература\n"
        "• Научные издания\n"
        "• Сувениры ручной работы\n"
        "• Картины местных художников\n\n"
        "Выберите раздел:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    )

# ========== ОБРАБОТКА КНОПОК ==========
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📦 Каталог товаров":
        await show_products_menu(update, context)
    elif text == "💰 Прайс-лист":
        await show_prices(update, context)
    elif text == "⭐ Отзывы клиентов":
        await show_reviews(update, context)
    elif text == "👥 Вакансии":
        await show_jobs_menu(update, context)
    elif text == "❓ Частые вопросы":
        await show_faq(update, context)
    elif text == "👨‍💼 Консультация":
        await show_support(update, context)
    elif text == "🎁 Акции и бонусы":
        await show_bonus(update, context)
    elif text == "⬅️ Главное меню":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
    else:
        await update.message.reply_text("Используйте кнопки меню для навигации.")

# ========== ОЧИСТКА ДАННЫХ ПО ТАЙМЕРУ ==========
async def cleanup_old_data():
    """Очистка старых данных"""
    while True:
        await asyncio.sleep(3600)  # Каждый час
        
        now = datetime.now()
        hours_to_keep = db.SECURITY_SETTINGS["auto_cleanup_hours"]
        
        # Очищаем старые данные пользователей
        users_to_delete = []
        for user_id, data_time in list(user_data.items()):
            # Проверяем время последней активности
            if "last_activity" in user_data[user_id]:
                last_active = user_data[user_id]["last_activity"]
                if isinstance(last_active, datetime):
                    if (now - last_active).hours > hours_to_keep:
                        users_to_delete.append(user_id)
        
        for user_id in users_to_delete:
            if user_id in user_data:
                del user_data[user_id]
        
        # Очищаем старые капчи
        captchas_to_delete = []
        for user_id, captcha_time in list(captcha_timers.items()):
            if (now - captcha_time).seconds > 3600:  # Старые капчи (1 час)
                captchas_to_delete.append(user_id)
        
        for user_id in captchas_to_delete:
            if user_id in captcha_timers:
                del captcha_timers[user_id]
            if user_id in captcha_data:
                del captcha_data[user_id]
        
        logging.info(f"Очистка данных: удалено {len(users_to_delete)} пользователей, {len(captchas_to_delete)} капч")

# ========== ЗАПУСК ==========
def main():
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик капчи
    captcha_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CAPTCHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_captcha)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    # Обработчик заказа
    order_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🏙️ Выбрать город)$"), start_order)
        ],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_city)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_product)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_weight)],
            DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_delivery)],
            DEPOSIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(⬅️ Главное меню)$"), start)
        ],
        allow_reentry=True
    )
    
    # Добавляем обработчики
    application.add_handler(captcha_handler)
    application.add_handler(order_handler)
    
    # Команды
    application.add_handler(CommandHandler("panic", panic_command))
    application.add_handler(CommandHandler("help", fake_menu_command))  # Фиктивное меню на /help
    
    # Обработчик вакансий
    application.add_handler(MessageHandler(
        filters.Regex("^(🚴 Курьер|👨‍🎨 Трафаретчик|🚗 Водитель|✅ Верификатор|📞 Оператор|👨‍💼 Менеджер)$"),
        show_job_details
    ))
    
    # Обработчик главного меню
    application.add_handler(MessageHandler(
        filters.Regex("^(📦 Каталог товаров|💰 Прайс-лист|⭐ Отзывы клиентов|👥 Вакансии|❓ Частые вопросы|👨‍💼 Консультация|🎁 Акции и бонусы|⬅️ Главное меню)$"),
        handle_main_menu
    ))
    
    # Фолбэк на любые другие сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))
    
    # Запускаем очистку данных в фоне
    asyncio.get_event_loop().create_task(cleanup_old_data())
    
    print("🚀 Curator's Choice бот запускается...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔐 Безопасность: активна")
    print(f"💰 Залог при заказах от: {db.SECURITY_SETTINGS['min_order_for_deposit']}₽")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logging.error(f"Ошибка запуска: {e}")

if __name__ == "__main__":
    main()