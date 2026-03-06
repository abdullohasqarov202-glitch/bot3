import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [["🏋️ Vazn olish", "🔥 Vazn yo‘qotish"]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    await update.message.reply_text(
        "Salom 👋\nMaqsadingizni tanlang:",
        reply_markup=keyboard
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🏋️ Vazn olish":
        await update.message.reply_text("Vazningiz nechchi kg?")

    elif text == "🔥 Vazn yo‘qotish":
        await update.message.reply_text("Hozir vazningiz nechchi kg?")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, message))

app.run_polling()
