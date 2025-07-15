import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# Получение переменных среды
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Например: 821932338
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}{TOKEN}"

# Flask-приложение
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Нажми кнопку 'Оставить заявку'.")

# Обработка обычных сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.from_user.id == (await bot.get_me()).id:
        text = update.message.text
        user = update.message.from_user
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"📨 Новая заявка от @{user.username or user.first_name} ({user.id}):\n\n{text}"
        )
        await update.message.reply_text("✅ Заявка отправлена!")
    else:
        await update.message.reply_text("✍️ Пожалуйста, напишите вашу заявку в ответном сообщении.")

# Обработка вебхука
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

# Главная страница для Render
@app.route("/", methods=["GET"])
def index():
    return "MT-IT Bot is running."

# Основной запуск
if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Установка вебхука
    async def set_webhook():
        await application.bot.set_webhook(WEBHOOK_URL)

    asyncio.get_event_loop().run_until_complete(set_webhook())

    # Запуск Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
