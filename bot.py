import os
import telebot
from telebot import types
import yt_dlp

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Assalomu alaykum! 👋\n\n"
        "Men Instagram, YouTube va TikTok'dan video hamda musiqalarni yuklab beruvchi botman.\n"
        "Menga shunchaki video havolasini (linkini) yuboring!"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_keyboard())

@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "Iltimos, to'g'ri havola (link) yuboring.")
        return

    msg = bot.reply_to(message, "Yuklanmoqda, iltimos kuting...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        caption_text = (info.get('title', 'Video') or 'Video') + ADS_TEXT

        with open(filename, 'rb') as video_file:
            bot.send_video(
                message.chat.id, 
                video_file, 
                caption=caption_text, 
                parse_mode="Markdown",
                reply_markup=get_keyboard()
            )

        bot.delete_message(message.chat.id, msg.message_id)
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        bot.edit_message_text("Xatolik yuz berdi yoki ushbu havoladan videoni yuklab bo'lmadi.", message.chat.id, msg.message_id)
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    bot.infinity_polling()
