import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Включение логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
APPLY, FEEDBACK = range(2)

# Чтение конфиденциальных данных из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_IDS = os.environ.get("OWNER_IDS", "")

if not BOT_TOKEN:
    logger.error("Не задан BOT_TOKEN в переменных окружения")
    exit("Error: BOT_TOKEN not set")

# Парсим строку OWNER_IDS в список целых ID владельцев
owners = []
if OWNER_IDS:
    owners = [int(x) for x in OWNER_IDS.split(",") if x.strip().isdigit()]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start: показывает приветствие с двумя кнопками."""
    keyboard = [
        ["📩 Оставить заявку", "⭐ Оставить отзыв"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(
        "Здравствуйте! Вы можете оставить заявку или отзыв. Пожалуйста, выберите действие:",
        reply_markup=reply_markup,
    )

async def apply_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пользователь выбрал «Оставить заявку»: просим ввести текст заявки."""
    await update.message.reply_text("Пожалуйста, введите текст вашей заявки:")
    return APPLY

async def feedback_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пользователь выбрал «Оставить отзыв»: просим ввести текст отзыва."""
    await update.message.reply_text("Пожалуйста, введите текст вашего отзыва:")
    return FEEDBACK

async def receive_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем текст заявки и отправляем его владельцам."""
    user = update.message.from_user
    text = update.message.text
    message = f"📩 *Новая заявка*\nОт: {user.full_name} (id={user.id})\n\n{text}"
    # Отправляем сообщение каждому владельцу
    for owner_id in owners:
        try:
            await context.bot.send_message(chat_id=owner_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка отправки заявки владельцу {owner_id}: {e}")
    await update.message.reply_text(
        "✅ Спасибо! Ваше сообщение отправлено.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем текст отзыва и отправляем его владельцам."""
    user = update.message.from_user
    text = update.message.text
    message = f"⭐ *Новый отзыв*\nОт: {user.full_name} (id={user.id})\n\n{text}"
    for owner_id in owners:
        try:
            await context.bot.send_message(chat_id=owner_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка отправки отзыва владельцу {owner_id}: {e}")
    await update.message.reply_text(
        "✅ Спасибо! Ваше сообщение отправлено.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Позволяет пользователю отменить текущий ввод."""
    await update.message.reply_text(
        "Действие отменено.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # ConversationHandler для обработки заявок и отзывов
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r"^📩 Оставить заявку$"), apply_request),
            MessageHandler(filters.Regex(r"^⭐ Оставить отзыв$"), feedback_request)
        ],
        states={
            APPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_application)],
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Определяем режим работы: webhook (на Render) или polling (локально)
    PORT = int(os.environ.get("PORT", 5000))
    render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_hostname:
        # Запуск в режиме webhook для Render
        webhook_url = f"https://{render_hostname}/{BOT_TOKEN}"
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Локальный запуск с Long Polling
        application.run_polling()

if __name__ == "__main__":
    main()
