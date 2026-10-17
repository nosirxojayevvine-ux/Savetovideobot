import os
import threading
from flask import Flask
import telebot
from telebot import types
import yt_dlp

# --- Flask server (Render o'chib qolmasligi uchun) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: Active"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Veb-serverni orqa fonda ishonchli ishga tushirish
t = threading.Thread(target=run_web)
t.daemon = True
t.start()

# --- Telegram Bot ---
TOKEN = "8815596661:AAFj0_tnBVyNesYDzDFyeHoAdsjuAwq0_WI"
bot = telebot.TeleBot(TOKEN)

ADS_TEXT = "\n\n🤖 **Bot:** @SavedToVideoBot"

def get_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    add_btn = types.InlineKeyboardButton(
        text="➕ Guruhga qo'shish",
        url="https://t.me/SavedToVideoBot?startgroup=true"
    )
    keyboard.add(add_btn)
    return keyboard

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Xush kelibsiz! Menga Instagram, TikTok yoki YouTube'dan havola yuborishingizni kutyabman... .",
        reply_markup=get_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "Iltimos, to'g'ri havola yuboring.")
        return

    msg = bot.reply_to(message, "⏳ Video yuklanmoqda, kuting...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open('video.mp4', 'rb') as video:
            bot.send_video(
                message.chat.id,
                video,
                caption=f"Yuklab olindi!{ADS_TEXT}",
                parse_mode="Markdown",
                reply_markup=get_keyboard()
            )

        if os.path.exists('video.mp4'):
            os.remove('video.mp4')

        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"Xatolik yuz berdi: {e}", message.chat.id, msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


