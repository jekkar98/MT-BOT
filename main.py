import os
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = list(map(int, os.getenv("OWNER_IDS", "").split(",")))  # Например: "12345,67890"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton("Отзывы", callback_data="reviews")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "leave_request":
        await query.message.reply_text("✍️ Пожалуйста, напишите вашу заявку в ответном сообщении.")
        context.user_data["awaiting_request"] = True

    elif data == "reviews":
        reviews_text = (
            "Отзывы наших клиентов:\n\n"
            "1. Отличный сервис! Рекомендую.\n"
            "2. Быстро и профессионально.\n"
            "3. Очень доволен работой бота."
        )
        await query.message.reply_text(reviews_text)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_request"):
        text = update.message.text
        # Переслать владельцам
        for owner_id in OWNER_IDS:
            try:
                await context.bot.send_message(chat_id=owner_id, text=f"Новая заявка от @{update.message.from_user.username or update.message.from_user.id}:\n\n{text}")
            except Exception as e:
                logger.error(f"Ошибка при отправке заявки владельцу {owner_id}: {e}")

        await update.message.reply_text("Спасибо за заявку! Мы свяжемся с вами.")
        context.user_data["awaiting_request"] = False
    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню командой /start")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(MessageHandler(filters.CallbackQueryHandler(button_handler)))

    # Запуск приложения с webhook или polling
    # Для локальной разработки можно заменить webhook на polling:
    # application.run_polling()
    # Но для Render нужно запускать с webhook. Ты сам указывал url webhook.

    # В Render обычно запускаем вот так:
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "8443")),
        url_path=BOT_TOKEN,
        webhook_url=f"https://<твое_доменное_имя>/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
