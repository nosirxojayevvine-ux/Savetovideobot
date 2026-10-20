import os
import threading
from flask import Flask
import telebot
from telebot import types
import yt_dlp

# --- 1. Flask veb-server (Render va Cron-job uchun 24/7 ishchi holat) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: Active"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_web)
t.daemon = True
t.start()

# --- 2. Telegram Bot va Sozlamalar ---
TOKEN = '8815596661:AAGIEtg_BA-PUmmBqd48GU8qMFB5SnvBWec'
bot = telebot.TeleBot(TOKEN)

# Sizning Admin ID raqamingiz
ADMIN_ID = 8019481444

ADS_TEXT = "\n\n🤖 **Bot:** @SavedToVideoBot"

# Foydalanuvchini bazaga (users.txt) saqlash funksiyasi
def save_user(user_id):
    if not os.path.exists('users.txt'):
        with open('users.txt', 'w') as f:
            pass
    with open('users.txt', 'r') as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open('users.txt', 'a') as f:
            f.write(str(user_id) + '\n')

# Inline tugma (Guruhga qo'shish)
def get_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    add_btn = types.InlineKeyboardButton(text="➕ Guruhga qo'shish", url="https://t.me/SavedToVideoBot?startgroup=true")
    keyboard.add(add_btn)
    return keyboard

# --- 3. Buyruqlar (Command Handlers) ---

@bot.message_handler(commands=['start'])
def start_message(message):
    save_user(message.chat.id)
    bot.send_message(
        message.chat.id, 
        "Xush kelibsiz! Menga Instagram, TikTok yoki YouTube'dan havola yuboring.",
        reply_markup=get_keyboard()
    )

# --- STATISTIKA BUYRUG'I (/stats) ---
@bot.message_handler(commands=['stats'])
def stats_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Kechirasiz, bu buyruq faqat admin uchun!")
        return
    
    if not os.path.exists('users.txt'):
        bot.reply_to(message, "📊 **Statistika:**\n\nJami foydalanuvchilar: 0 ta")
        return
        
    with open('users.txt', 'r') as f:
        users = f.read().splitlines()
        
    bot.reply_to(
        message, 
        f"📊 **Bot statistikasi:**\n\nJami foydalanuvchilar: {len(users)} ta",
        parse_mode='Markdown'
    )

# --- XABAR TARQATISH BUYRUG'I (/send) ---
@bot.message_handler(commands=['send', 'broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Kechirasiz, bu buyruq faqat admin uchun!")
        return

    if not os.path.exists('users.txt'):
        bot.reply_to(message, "Hozircha bazada foydalanuvchilar yo'q.")
        return

    with open('users.txt', 'r') as f:
        users = f.read().splitlines()

    if not users:
        bot.reply_to(message, "Baza bo'sh.")





