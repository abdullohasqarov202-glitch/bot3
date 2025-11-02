import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile

# 🔑 Telegram token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN aniqlanmadi! Render environment variable orqali qo‘shing.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 📢 Kanal username
CHANNEL_USERNAME = "@Asqarov_2007"

# 🍪 Cookie fayl (Instagram uchun)
COOKIE_FILE = "cookies.txt"


# ✅ Obuna tekshirish
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# 🚀 Start komandasi
@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎥 Salom! Men sizga TikTok, Instagram, Facebook yoki Twitter videolarini yuklab beraman!\n\n"
        "Faqat havolani yuboring 👇",
        parse_mode="HTML"
    )


# 🎥 Video yuklab berish
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    user_id = message.chat.id
    url = message.text.strip()

    # 🔒 Avval obuna tekshiramiz
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(
            user_id,
            f"🚫 Avvalo kanalga obuna bo‘ling:\n{CHANNEL_USERNAME}\n\nShundan so‘ng video yuboring 👇",
            reply_markup=markup
        )
        return

    # 🎬 Yuklab olish jarayoni
    bot.reply_to(message, "⏳ Video yuklab olinmoqda...")

    try:
        if not any(d in url for d in ["tiktok.com", "instagram.com", "facebook.com", "x.com", "twitter.com", "fb.watch"]):
            bot.reply_to(message, "⚠️ Faqat TikTok, Instagram, Facebook yoki Twitter havolasi yuboring.")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
                'format': 'mp4',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            caption = "🎬 Yuklab beruvchi bot: @instagram_tiktok_uzbot"
            with open(video_path, 'rb') as v:
                bot.send_video(message.chat.id, v, caption=caption)

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")


# 🔁 Obuna qayta tekshirish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi! Endi video yuboring 👇", chat_id=user_id, message_id=call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")


# 🌍 Flask webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "<h2>✅ Video yuklab beruvchi bot ishlayapti!</h2>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
