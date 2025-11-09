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


# 🚀 Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎥 Salom! Men sizga TikTok, Instagram, Facebook yoki Twitter videolarini yuklab beraman!\n\n"
        "Faqat havolani yuboring 👇",
        parse_mode="HTML"
    )


# 🎞 Yuklash funksiyasi (fon jarayoni)
def process_video(message, url):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
                'quiet': True,
                'retries': 2,
                'noplaylist': True
            }

            # 🔽 Video yuklash
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            # 🎬 Caption
            caption = "🎬 Yuklab beruvchi bot: @instagram_tiktok_uzbot"

            # 🎥 Video yuborish
            with open(file_path, 'rb') as v:
                bot.send_video(message.chat.id, v, caption=caption)

            # 🎧 Audio yuklashga urinish (agar topilmasa xato chiqmasin)
            try:
                audio_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'
                    }],
                    'quiet': True
                }

                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    info_audio = ydl.extract_info(url, download=True)
                    audio_path = ydl.prepare_filename(info_audio).rsplit('.', 1)[0] + ".mp3"

                # 🎵 Audio faylni yuborish
                with open(audio_path, 'rb') as a:
                    bot.send_audio(message.chat.id, a, caption="🎧 Qo‘shiq")

            except Exception:
                # ❌ Audio topilmasa, hech narsa yozmaydi
                pass

    except Exception as e:
        # Foydalanuvchiga xato yuborilmaydi, lekin server logida ko‘rinadi
        print(f"[Xatolik] {e}")


# 🎥 Link yuborilganda
@bot.message_handler(func=lambda msg: msg.text.startswith("http"))
def handle_link(message):
    url = message.text.strip()

    # 🔒 Obuna tekshirish
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

    bot.reply_to(message, "⚡️ Yuklab olinmoqda... Iltimos kuting!")

    # ⏩ Yuklashni alohida oqimda ishlatish
    thread = threading.Thread(target=process_video, args=(message, url))
    thread.start()


# 🔁 Obuna qayta tekshirish
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi! Endi video yoki qo‘shiq yuboring 👇",
                              chat_id=user_id, message_id=call.message.message_id)
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
