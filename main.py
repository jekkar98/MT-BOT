import os
from flask import Flask, request
import asyncio
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Чтение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://yourbot.onrender.com/
OWNER_IDS = [int(x.strip()) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()]

# Flask
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Хранилище состояний пользователей
user_states = {}

# Состояния
STATE_WAITING_FOR_APPLICATION = "waiting_for_application"
STATE_WAITING_FOR_REVIEW = "waiting_for_review"

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✍️ Оставить заявку", "💬 Оставить отзыв"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Выберите действие ниже 👇",
        reply_markup=reply_markup
    )
    user_states[update.effective_chat.id] = None

# Обработка текстов
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    state = user_states.get(chat_id)

    if text == "✍️ Оставить заявку":
        await update.message.reply_text("✍️ Пожалуйста, напишите вашу заявку:")
        user_states[chat_id] = STATE_WAITING_FOR_APPLICATION
        return

    if text == "💬 Оставить отзыв":
        await update.message.reply_text("💬 Пожалуйста, напишите ваш отзыв:")
        user_states[chat_id] = STATE_WAITING_FOR_REVIEW
        return

    # Обработка заявки
    if state == STATE_WAITING_FOR_APPLICATION:
        for owner_id in OWNER_IDS:
            await bot.send_message(chat_id=owner_id, text=f"📩 Новая заявка от {chat_id}:\n\n{text}")
        await update.message.reply_text("✅ Ваша заявка отправлена. Спасибо!")
        user_states[chat_id] = None
        return

    # Обработка отзыва
    if state == STATE_WAITING_FOR_REVIEW:
        for owner_id in OWNER_IDS:
            await bot.send_message(chat_id=owner_id, text=f"⭐ Отзыв от {chat_id}:\n\n{text}")
        await update.message.reply_text("✅ Спасибо за ваш отзыв!")
        user_states[chat_id] = None
        return

    # Если нет состояния
    await update.message.reply_text("Нажмите одну из кнопок ниже, чтобы продолжить.")

# Вебхук
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def home():
    return "Бот работает."

# Хендлеры
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
