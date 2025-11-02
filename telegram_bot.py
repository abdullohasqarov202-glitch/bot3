import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile
import threading

# 🔑 Token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN topilmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)
app = Flask(__name__)

CHANNEL_USERNAME = "@Asqarov_2007"
COOKIE_FILE = "cookies.txt"


# ✅ Obuna tekshirish
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# 🚀 Start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎥 Salom! Men sizga TikTok, Instagram, Facebook yoki Twitter videolarini yuklab beraman!\n\n"
        "Faqat havolani yuboring 👇",
        parse_mode="HTML"
    )


# 🎞 Asosiy yuklash funksiyasi (fon jarayoni)
def process_video(message, url):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
                'format': 'mp4',
                'quiet': True,
                'retries': 2,  # qayta urinadi
                'noplaylist': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            caption = "🎬 Yuklab beruvchi bot: @instagram_tiktok_uzbot"
            with open(video_path, 'rb') as v:
                bot.send_video(message.chat.id, v, caption=caption)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik: {e}")


# 🎥 Havola kelganda
@bot.message_handler(func=lambda msg: msg.text.startswith("http"))
def handle_link(message):
    url = message.text.strip()

    # 🔒 Avval obuna tekshirish
    if not is_subscribed(message.chat.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(
            message.chat.id,
            f"🚫 Avvalo kanalga obuna bo‘ling:\n{CHANNEL_USERNAME}\n\nSo‘ngra havolani yuboring 👇",
            reply_markup=markup
        )
        return

    # 🎬 Tezkor javob
    bot.reply_to(message, "⚡️ Yuklab olinmoqda... Iltimos kuting!")

    # ⏩ Yangi oqimda yuklash
    thread = threading.Thread(target=process_video, args=(message, url))
    thread.start()


# 🔁 Obuna qayta tekshirish
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi! Endi video yuboring 👇", chat_id=user_id, message_id=call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")


# 🌐 Flask webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "<h3>✅ Bot ishlayapti — instagram_tiktok_uzbot</h3>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
