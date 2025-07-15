import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# Состояния пользователей: {chat_id: "waiting_for_..." }
user_states = {}

ADMINS = [821932338, 384949127]  # сюда добавь свои ID для уведомлений

@app.route('/')
def index():
    return "MT-IT Bot is running."

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    # Проверяем, в каком состоянии сейчас пользователь
    state = user_states.get(chat_id)

    if message.lower() in ["/start", "старт", "привет"]:
        user_states.pop(chat_id, None)  # сброс состояния
        keyboard = telegram.ReplyKeyboardMarkup(
            [['📩 Оставить заявку', '📝 Оставить отзыв']], resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text="👋 Добро пожаловать в MT-IT!\nВыберите действие:", reply_markup=keyboard)
        return "ok"

    if state == "waiting_for_request":
        # Получили заявку от пользователя
        for admin_id in ADMINS:
            bot.send_message(chat_id=admin_id,
                             text=f"📬 Новая заявка от @{update.message.from_user.username} ({chat_id}):\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Заявка принята. Спасибо!")
        user_states.pop(chat_id)
        return "ok"

    if state == "waiting_for_review":
        # Получили отзыв от пользователя
        for admin_id in ADMINS:
            bot.send_message(chat_id=admin_id,
                             text=f"📝 Новый отзыв от @{update.message.from_user.username} ({chat_id}):\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Отзыв получен. Спасибо!")
        user_states.pop(chat_id)
        return "ok"

    if message == "📩 Оставить заявку":
        user_states[chat_id] = "waiting_for_request"
        bot.send_message(chat_id=chat_id, text="✍️ Пожалуйста, напишите вашу заявку.")
        return "ok"

    if message == "📝 Оставить отзыв":
        user_states[chat_id] = "waiting_for_review"
        bot.send_message(chat_id=chat_id, text="✍️ Пожалуйста, напишите ваш отзыв.")
        return "ok"

    # Если пользователь пишет что-то непонятное
    bot.send_message(chat_id=chat_id, text="ℹ️ Напишите /start, чтобы начать или выберите действие кнопками.")
    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
