import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request, Response

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()]

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# Клавиатура с кнопкой заявки
keyboard = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text="📩 Оставить заявку", callback_data="leave_request")
)

# Стейт для хранения заявок (простой словарь в памяти)
user_requests = {}

# Хэндлер на команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы оставить заявку.",
        reply_markup=keyboard
    )

# Обработка нажатия кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "leave_request":
        user_requests[query.from_user.id] = True
        await query.message.reply_text("✍️ Пожалуйста, напишите вашу заявку в ответном сообщении.")

# Обработка текстовых сообщений (заявок)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_requests.get(user_id):
        # Пересылаем заявку всем владельцам
        text = f"📨 Заявка от @{update.message.from_user.username or update.message.from_user.first_name}:\n\n{update.message.text}"
        for owner_id in OWNER_IDS:
            try:
                await context.bot.send_message(chat_id=owner_id, text=text)
            except Exception as e:
                print(f"Ошибка при отправке владельцу {owner_id}: {e}")
        await update.message.reply_text("Спасибо! Ваша заявка отправлена.")
        user_requests.pop(user_id)
    else:
        await update.message.reply_text("Пожалуйста, нажмите кнопку, чтобы оставить заявку.", reply_markup=keyboard)

# Регистрируем хэндлеры
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# --- Flask endpoint для webhook ---

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put(update)
    return Response("ok", status=200)

# Запуск приложения через webhook с портом Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
