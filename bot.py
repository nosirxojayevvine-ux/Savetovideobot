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
  return 'Bot status: Active'


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

ADS_TEXT = '\n\n🤖 **Bot:** @SavedToVideoBot'


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
  add_btn = types.InlineKeyboardButton(
      text="➕ Guruhga qo'shing",
      url='https://t.me/SavedToVideoBot?startgroup=true',
  )
  keyboard.add(add_btn)
  return keyboard


# --- 3. Command Handlers ---


@bot.message_handler(commands=['start'])
def start_message(message):
  save_user(message.chat.id)
  bot.send_message(
      message.chat.id,
      'Xush kelibsiz! Menga Instagram, TikTok yoki YouTube\'dan havola'
      ' yuborishingizni kutyabman...',
      reply_markup=get_keyboard(),
  )


# --- 4. Hammaga xabar va rasm tarqatish (Rassilka / Broadcast) ---
@bot.message_handler(commands=['send', 'broadcast'])
def broadcast_message(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, 'Kechirasiz, bu buyruq faqat admin uchun!')
    return

  if not os.path.exists('users.txt'):
    bot.reply_to(message, 'Hozircha bazada foydalanuvchilar yo\'q.')
    return

  with open('users.txt', 'r') as f:
    users = f.read().splitlines()

  if not users:
    bot.reply_to(message, 'Baza bo\'sh.')
    return

  success = 0
  failed = 0

  # A) Agar Rasm bilan yuborilgan bo'lsa
  if message.caption:
    caption_text = (
        message.caption.replace('/send', '').replace('/broadcast', '').strip()
    )
    file_id = message.photo[-1].file_id if message.photo else None

    for uid in users:
      try:
        if file_id:
          bot.send_photo(
              uid, file_id, caption=caption_text, parse_mode='Markdown'
          )
        else:
          bot.send_message(uid, caption_text, parse_mode='Markdown')
        success += 1
      except Exception:
        failed += 1

  # B) Agar faqat Matn yuborilgan bo'lsa
  else:
    text = message.text.replace('/send', '').replace('/broadcast', '').strip()
    if not text:
      bot.reply_to(
          message,
          '⚠️ **Qanday ishlatiladi?**\n\n'
          '1. **Faqat matn:** `/send Assalomu alaykum`\n'
          '2. **Rasm bilan:** Rasmni tanlab, ostidagi matnga `/send Bu rasm'
          ' izohi` deb yozasiz.',
          parse_mode='Markdown',
      )
      return

    for uid in users:
      try:
        bot.send_message(uid, text, parse_mode='Markdown')
        success += 1
      except Exception:
        failed += 1

  bot.reply_to(
      message,
      f'Xabar tarqatildi! ✅\n\nYetib bordi: {success} ta\nYetib bormadi (bloklagan):'
      f' {failed} ta',
  )


# --- 5. Video Yuklovchi Handler ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  save_user(message.chat.id)
  url = message.text.strip()

  if not (url.startswith('http://') or url.startswith('https://')):
    bot.reply_to(message, "Iltimos, to'g'ri havola yuboring.")
    return

  msg = bot.reply_to(message, '⏳ Havolangiz Yuklab olinmoqda, kuting...')

  ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    with open('video.mp4', 'rb') as video:
      bot.send_video(
          message.chat.id,
          video,
          caption=Videoingiz yuklab olindi ✅ 
(Tashlagan havolangiz uchun raxmat)!{ADS_TEXT}',
          parse_mode='Markdown',
          reply_markup=get_keyboard(),
      )

    if os.path.exists('video.mp4'):
      os.remove('video.mp4')

    bot.delete_message(message.chat.id, msg.message_id)

  except Exception as e:
    bot.edit_message_text(
        f'Xatolik yuz berdi: {e}', message.chat.id, msg.message_id
    )


# --- 6. Botni ishga tushirish ---
if __name__ == '__main__':
  bot.infinity_polling(timeout=10, long_polling_timeout=5)




