# -*- coding: utf-8 -*-
import telebot
from telebot import types
import random
import time
from collections import deque

TOKEN = '8684574901:AAEIp2yTBytttMoUSyzvlE-k666z9VtiGYg'
bot = telebot.TeleBot(TOKEN)

# ========== ТВОИ ФРАЗЫ (РОССИЙСКИЕ) ==========
RUSSIAN_PHRASES = [
    "Жизнь боль, но ты держись!",
    "Программист — это не профессия, это образ жизни",
    "Сегодня точно повезёт!",
    "Сделай паузу, съешь печеньку",
    "Код не работает? А ты попробуй включить и выключить",
    "Кофе — это святое",
    "Понедельник дело такое...",
    "Лучше день потерять, потом за пять минут долететь",
    "Работа не волк, работа это работа",
    "Счастье есть, его не может не есть"
]

# ========== ТВОИ ИГРУШКИ ==========
TOYS = {
    'bone': {'name': '🦴 Косточка', 'price': 3},
    'jumper': {'name': '🐸 Попрыгунчик', 'price': 5},
    'ball': {'name': '⚽ Мячик', 'price': 7},
    'ring': {'name': '🔘 Кольцо', 'price': 10}
}

# ========== ТВОИ ЦЕНЫ ==========
MOPS_PRICES = {
    15: 10, 30: 20, 50: 35, 70: 60, 100: 70, 200: 150
}

# ========== ФАКТЫ О МОПСАХ ==========
PUG_FACTS = [
    "🐶 Мопсы очень любят спать до 14 часов в день!",
    "🐶 Они храпят как маленькие тракторчики",
    "🐶 У мопсов смешные морщинки",
    "🐶 Мопсы обожают есть и всегда просят еду",
    "🐶 В Древнем Китае мопсы жили во дворцах императоров"
]

# ========== БАЗЫ ДАННЫХ ==========
users = {}
reg_states = {}
chat_words = {}          # слова для каждого чата
chat_counters = {}       # счетчик сообщений
chat_threshold = {}      # через сколько отвечать
waiting_for_question = set()

# ========== ФУНКЦИИ ДЛЯ СЛОВ ==========
def save_word(chat_id, word):
    if chat_id not in chat_words:
        chat_words[chat_id] = []
    if len(word) > 0:
        chat_words[chat_id].append(word.lower())
        # оставляем последние 50 слов
        if len(chat_words[chat_id]) > 50:
            chat_words[chat_id] = chat_words[chat_id][-50:]

def get_random_words(chat_id):
    if chat_id not in chat_words or len(chat_words[chat_id]) < 3:
        return None
    # берем 3 случайных слова
    words = random.sample(chat_words[chat_id], 3)
    return ' '.join(words)

# ========== ФУНКЦИИ ДЛЯ МАГАЗИНА ==========
def check_balance(user_id, cost):
    return user_id in users and users[user_id]['balance'] >= cost

def spend_mops(user_id, cost):
    if check_balance(user_id, cost):
        users[user_id]['balance'] -= cost
        return True
    return False

# ========== КЛАВИАТУРЫ ==========
def get_ls_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📝 Регистрация", callback_data="ls_reg"),
        types.InlineKeyboardButton("📊 Мой профиль", callback_data="ls_profile"),
        types.InlineKeyboardButton("🧸 Магазин игрушек", callback_data="ls_shop"),
        types.InlineKeyboardButton("💰 Купить 🐶", callback_data="ls_buy_mops"),
        types.InlineKeyboardButton("🐶 О мопсах", callback_data="ls_about_pugs"),
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="ls_settings")
    ]
    markup.add(*buttons)
    return markup

def get_chat_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📸 Мемное фото", callback_data="chat_meme"),
        types.InlineKeyboardButton("💬 Фраза", callback_data="chat_phrase"),
        types.InlineKeyboardButton("🌀 Фраза из чата", callback_data="chat_saved"),
        types.InlineKeyboardButton("ℹ️ О боте", callback_data="chat_about")
    ]
    markup.add(*buttons)
    return markup

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    user_id = message.from_user.id
    chat_type = message.chat.type
    
    if chat_type == 'private':
        if user_id in users:
            bot.send_message(
                user_id,
                f"🐕 С возвращением, {users[user_id]['name']}!",
                reply_markup=get_ls_keyboard()
            )
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📝 Зарегистрироваться", callback_data="ls_reg"))
            bot.send_message(
                user_id,
                "👋 Привет! Я МопсБот!\n\nНажми кнопку ниже:",
                reply_markup=markup
            )
    else:
        if message.chat.id not in chat_counters:
            chat_counters[message.chat.id] = 0
            chat_threshold[message.chat.id] = random.randint(3, 6)
        
        bot.send_message(
            message.chat.id,
            "👋 Привет, чат! Я отвечаю каждые 3-6 сообщений.",
            reply_markup=get_chat_keyboard()
        )

@bot.message_handler(commands=['profile'])
def profile(message):
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(user_id, "❌ Сначала зарегистрируйся через /start")
        return
    
    user = users[user_id]
    inv = "\n".join([f"• {i}" for i in user['inventory']]) if user['inventory'] else "Пусто"
    text = f"📊 *Твой профиль*\n\nИмя: {user['name']}\n🐶 Мопсиков: {user.get('pugs_count',0)}\n💰 Баланс: {user['balance']} 🐶\n\n📦 Инвентарь:\n{inv}"
    bot.send_message(user_id, text, parse_mode='Markdown')

@bot.message_handler(commands=['shop'])
def shop(message):
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(user_id, "❌ Сначала зарегистрируйся")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for toy_id, toy in TOYS.items():
        markup.add(types.InlineKeyboardButton(f"{toy['name']} - {toy['price']} 🐶", callback_data=f"ls_buy_{toy_id}"))
    bot.send_message(user_id, f"🧸 Магазин игрушек\n💰 Баланс: {users[user_id]['balance']} 🐶", reply_markup=markup)

@bot.message_handler(commands=['buy'])
def buy(message):
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(user_id, "❌ Сначала зарегистрируйся")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for mops, price in MOPS_PRICES.items():
        markup.add(types.InlineKeyboardButton(f"{mops} 🐶 = {price} грн", callback_data=f"ls_pay_{mops}"))
    bot.send_message(user_id, "💰 Выбери пакет:", reply_markup=markup)

@bot.message_handler(commands=['mops'])
def mops_fact(message):
    bot.send_message(message.chat.id, f"✨ {random.choice(PUG_FACTS)}")

# ========== /ДАНЕТ ТОЛЬКО В ЛИЧКЕ ==========
@bot.message_handler(commands=['данет'])
def yes_no_command(message):
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, "❌ Команда /данет работает только в личных сообщениях!")
        return
    user_id = message.from_user.id
    waiting_for_question.add(user_id)
    bot.send_message(user_id, "❓ Напиши свой вопрос, а я отвечу честно 50/50", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    text = (
        "📋 *Список команд:*\n\n"
        "/start - Запустить бота\n"
        "/menu - Открыть меню\n"
        "/profile - Мой профиль\n"
        "/shop - Магазин игрушек\n"
        "/buy - Купить мопсокрипты\n"
        "/mops - Факты о мопсах\n"
        "/данет - Честный ответ 50/50 (только в ЛС)\n"
        "/help - Это меню\n\n"
        "В чате: каждые 3-6 сообщений бот отвечает случайными словами из чата"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# ========== РЕГИСТРАЦИЯ ==========
@bot.callback_query_handler(func=lambda call: call.data == "ls_reg")
def ls_registration_start(call):
    user_id = call.message.chat.id
    reg_states[user_id] = 'waiting_name'
    bot.edit_message_text("1️⃣ Как тебя зовут?", user_id, call.message.message_id)

@bot.message_handler(func=lambda message: message.chat.type == 'private' and message.from_user.id in reg_states)
def ls_handle_registration(message):
    user_id = message.from_user.id
    state = reg_states[user_id]
    
    if state == 'waiting_name':
        users[user_id] = {'name': message.text, 'balance': 0, 'inventory': []}
        reg_states[user_id] = 'waiting_pugs'
        bot.send_message(user_id, "2️⃣ Сколько мопсиков у тебя дома?")
    
    elif state == 'waiting_pugs':
        try:
            users[user_id]['pugs_count'] = int(message.text)
            reg_states[user_id] = 'waiting_toy'
            bot.send_message(user_id, "3️⃣ Любимая игрушка твоего мопса?")
        except:
            bot.send_message(user_id, "❌ Напиши число")
    
    elif state == 'waiting_toy':
        users[user_id]['favorite_toy'] = message.text
        del reg_states[user_id]
        bot.send_message(user_id, f"✅ Регистрация завершена, {users[user_id]['name']}!", reply_markup=get_ls_keyboard())

# ========== ДАНЕТ (ОБРАБОТКА ВОПРОСОВ) ==========
@bot.message_handler(func=lambda message: message.from_user.id in waiting_for_question and message.chat.type == 'private')
def handle_yes_no_question(message):
    user_id = message.from_user.id
    waiting_for_question.remove(user_id)
    
    answers = [
        "✅ Да", "👍 Конечно", "⭐ Безусловно", "🌟 Совершенно точно",
        "❌ Нет", "👎 Скорее всего нет", "🌧️ Маловероятно", "😕 Без сомнений, нет"
    ]
    
    bot.send_message(user_id, random.choice(answers))

# ========== КНОПКИ В ЛС ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('ls_'))
def ls_callback_handler(call):
    user_id = call.message.chat.id
    data = call.data
    
    if data == "ls_profile":
        user = users[user_id]
        inv = "\n".join([f"• {i}" for i in user['inventory']]) if user['inventory'] else "Пусто"
        text = f"📊 *Профиль*\n\nИмя: {user['name']}\n🐶 Мопсиков: {user.get('pugs_count',0)}\n💰 Баланс: {user['balance']} 🐶\n\n📦 Инвентарь:\n{inv}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Назад", callback_data="ls_back"))
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    
    elif data == "ls_shop":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for toy_id, toy in TOYS.items():
            markup.add(types.InlineKeyboardButton(f"{toy['name']} - {toy['price']} 🐶", callback_data=f"ls_buy_{toy_id}"))
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="ls_back"))
        bot.edit_message_text(f"🧸 Магазин\n💰 Баланс: {users[user_id]['balance']} 🐶", user_id, call.message.message_id, reply_markup=markup)
    
    elif data.startswith("ls_buy_"):
        toy_id = data.replace("ls_buy_", "")
        if toy_id in TOYS and spend_mops(user_id, TOYS[toy_id]['price']):
            users[user_id]['inventory'].append(TOYS[toy_id]['name'])
            bot.answer_callback_query(call.id, f"✅ Куплено!")
        else:
            bot.answer_callback_query(call.id, f"❌ Не хватает 🐶")
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for t_id, t in TOYS.items():
            markup.add(types.InlineKeyboardButton(f"{t['name']} - {t['price']} 🐶", callback_data=f"ls_buy_{t_id}"))
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="ls_back"))
        bot.edit_message_text(f"🧸 Магазин\n💰 Баланс: {users[user_id]['balance']} 🐶", user_id, call.message.message_id, reply_markup=markup)
    
    elif data == "ls_buy_mops":
        markup = types.InlineKeyboardMarkup(row_width=2)
        for mops, price in MOPS_PRICES.items():
            markup.add(types.InlineKeyboardButton(f"{mops} 🐶 = {price} грн", callback_data=f"ls_pay_{mops}"))
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="ls_back"))
        bot.edit_message_text("💰 Выбери пакет:", user_id, call.message.message_id, reply_markup=markup)
    
    elif data.startswith("ls_pay_"):
        mops = int(data.split("_")[2])
        users[user_id]['balance'] += mops
        bot.answer_callback_query(call.id, f"✅ +{mops} 🐶")
        bot.edit_message_text(f"🐕 {users[user_id]['name']}", user_id, call.message.message_id, reply_markup=get_ls_keyboard())
    
    elif data == "ls_about_pugs":
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🔄 Ещё", callback_data="ls_about_pugs"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="ls_back"))
        bot.edit_message_text(f"✨ {random.choice(PUG_FACTS)}", user_id, call.message.message_id, reply_markup=markup)
    
    elif data == "ls_settings":
        bot.edit_message_text(
            "⚙️ *Настройки*\n\n(тут будут настройки позже)",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Назад", callback_data="ls_back"))
        )
    
    elif data == "ls_back":
        bot.edit_message_text(f"🐕 {users[user_id]['name']}", user_id, call.message.message_id, reply_markup=get_ls_keyboard())

# ========== КНОПКИ В ЧАТЕ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_'))
def chat_callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if data == "chat_meme":
        bot.answer_callback_query(call.id, "📸 Мем")
        bot.send_message(chat_id, "📸 Вот мем (позже добавлю ссылки)")
    
    elif data == "chat_phrase":
        bot.answer_callback_query(call.id, "💬 Фраза")
        bot.send_message(chat_id, f"💬 {random.choice(RUSSIAN_PHRASES)}")
    
    elif data == "chat_saved":
        bot.answer_callback_query(call.id, "🌀 Из чата")
        words = get_random_words(chat_id)
        if words:
            bot.send_message(chat_id, f"🌀 {words}")
        else:
            bot.send_message(chat_id, "❌ Мало слов в чате (нужно минимум 3)")
    
    elif data == "chat_about":
        word_count = len(chat_words.get(chat_id, []))
        msg_count = chat_counters.get(chat_id, 0)
        threshold = chat_threshold.get(chat_id, 3)
        bot.send_message(chat_id, f"ℹ️ Слов сохранено: {word_count}\nСообщений: {msg_count}/{threshold}")

# ========== СООБЩЕНИЯ В ЧАТЕ (АВТООТВЕТЫ) ==========
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_chat_messages(message):
    chat_id = message.chat.id
    
    # Инициализация для нового чата
    if chat_id not in chat_counters:
        chat_counters[chat_id] = 0
        chat_threshold[chat_id] = random.randint(3, 6)
    
    if message.text and not message.text.startswith('/'):
        # Сохраняем все слова
        words = message.text.split()
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha())
            if len(clean_word) > 0:
                save_word(chat_id, clean_word)
        
        # Увеличиваем счетчик
        chat_counters[chat_id] += 1
        
        # Проверяем, пора ли отвечать
        if chat_counters[chat_id] >= chat_threshold[chat_id]:
            # Пытаемся получить слова из чата
            words = get_random_words(chat_id)
            if words:
                bot.send_message(chat_id, f"🌀 {words}")
            else:
                bot.send_message(chat_id, f"💬 {random.choice(RUSSIAN_PHRASES)}")
            
            # Сбрасываем счетчики
            chat_counters[chat_id] = 0
            chat_threshold[chat_id] = random.randint(3, 6)

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🐶" + "="*50)
    print("🐶 МОПСБОТ ЗАПУЩЕН НА RENDER!")
    print("🐶" + "="*50)
    print("✅ Доступные команды:")
    print("   /start, /menu, /profile, /shop")
    print("   /buy, /mops, /данет (только в ЛС), /help")
    print("✅ В чате: собирает слова, отвечает 3-6 сообщений")
    print("✅ Всё на русском языке")
    print("🐶" + "="*50)
    
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
