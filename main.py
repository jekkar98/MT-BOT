import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = list(map(int, os.getenv("OWNER_IDS", "").split(',')))  # Например: "821932338,384949127"

# Хранение состояния пользователя: ждём заявку или отзыв
user_states = {}  # user_id: 'waiting_for_request' | 'waiting_for_review' | None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оставить заявку", callback_data='request')],
        [InlineKeyboardButton("Оставить отзыв", callback_data='review')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выберите опцию:", reply_markup=reply_markup)
    user_states[update.effective_user.id] = None

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'request':
        await query.message.reply_text("✍️ Пожалуйста, напишите вашу заявку в ответном сообщении.")
        user_states[user_id] = 'waiting_for_request'
    elif query.data == 'review':
        await query.message.reply_text("📝 Пожалуйста, напишите ваш отзыв в ответном сообщении.")
        user_states[user_id] = 'waiting_for_review'

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    state = user_states.get(user_id)

    if state == 'waiting_for_request':
        # Пересылаем заявку владельцам
        for owner_id in OWNER_IDS:
            await context.bot.send_message(chat_id=owner_id, text=f"Заявка от {user_id}:\n{text}")
        await update.message.reply_text("Спасибо! Ваша заявка отправлена.")
        user_states[user_id] = None

    elif state == 'waiting_for_review':
        # Пересылаем отзыв владельцам
        for owner_id in OWNER_IDS:
            await context.bot.send_message(chat_id=owner_id, text=f"Отзыв от {user_id}:\n{text}")
        await update.message.reply_text("Спасибо за ваш отзыв!")
        user_states[user_id] = None

    else:
        await update.message.reply_text("Пожалуйста, нажмите /start и выберите действие.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
