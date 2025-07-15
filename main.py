import asyncio
from flask import Flask, request, abort
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

import os

TOKEN = os.getenv("BOT_TOKEN")  # передавай токен в переменной окружения в Render
ADMIN_CHAT_IDS = [821932338, 384949127]  # твои айди для получения заявок

app = Flask(__name__)

# Создаём Application - новый бот с поддержкой async
application = Application.builder().token(TOKEN).build()

# Главное меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Оставить заявку", callback_data="request")],
        [InlineKeyboardButton("Оставить отзыв", callback_data="review")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать в MT-IT!\n\nВыберите действие:",
        reply_markup=main_menu_keyboard()
    )

# Обработка кнопок меню
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "request":
        await query.edit_message_text("✍️ Пожалуйста, напишите вашу заявку в ответном сообщении.")
        context.user_data["expecting"] = "request"

    elif query.data == "review":
        await query.edit_message_text("📝 Пожалуйста, напишите ваш отзыв в ответном сообщении.")
        context.user_data["expecting"] = "review"

# Обработка сообщений (заявки и отзывы)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    expecting = context.user_data.get("expecting")

    if expecting == "request":
        # Отправляем заявку администраторам
        for admin_id in ADMIN_CHAT_IDS:
            await application.bot.send_message(
                chat_id=admin_id,
                text=f"📩 *Заявка* от [{user.first_name}](tg://user?id={user.id}):\n\n{text}",
                parse_mode=ParseMode.MARKDOWN
            )
        await update.message.reply_text("Спасибо! Ваша заявка отправлена.")
        context.user_data["expecting"] = None

    elif expecting == "review":
        # Отправляем отзыв администраторам
        for admin_id in ADMIN_CHAT_IDS:
            await application.bot.send_message(
                chat_id=admin_id,
                text=f"⭐ *Отзыв* от [{user.first_name}](tg://user?id={user.id}):\n\n{text}",
                parse_mode=ParseMode.MARKDOWN
            )
        await update.message.reply_text("Спасибо за ваш отзыв!")
        context.user_data["expecting"] = None

    else:
        # Если сообщение вне диалога с меню
        await update.message.reply_text("Пожалуйста, воспользуйтесь /start и выберите действие.")

# Регистрируем хэндлеры
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(application.message_handler(message_handler))

# Flask webhook route — сюда Телега шлёт обновления
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.update_queue.put(update))
    return "OK"

# Просто проверка доступности
@app.route("/")
def index():
    return "MT-IT Telegram Bot is running!"

# Запуск Flask
if __name__ == "__main__":
    # В Render будет использоваться gunicorn, а локально - просто python main.py
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
