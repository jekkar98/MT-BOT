import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из переменной окружения
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

user_states = {}  # для отслеживания в каком режиме пользователь: 'waiting_for_request' или 'waiting_for_feedback'

@app.route('/')
def index():
    return "MT-IT Bot is running."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    state = user_states.get(chat_id)

    if message.lower() in ['/start', 'старт', 'привет']:
        keyboard = telegram.ReplyKeyboardMarkup([['📩 Оставить заявку', '📝 Оставить отзыв']], resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text="👋 Добро пожаловать в MT-IT!\n\nВыберите действие:", reply_markup=keyboard)
        user_states[chat_id] = None
        return "ok"

    if state == 'waiting_for_request':
        # Отправляем заявку на оба ID
        for admin_id in [821932338, 384949127]:
            bot.send_message(chat_id=admin_id,
                             text=f"📬 Новая заявка от @{update.message.from_user.username} ({chat_id}):\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Ваша заявка принята. Спасибо!")
        user_states[chat_id] = None
        return "ok"

    if state == 'waiting_for_feedback':
        # Отправляем отзыв на оба ID
        for admin_id in [821932338, 384949127]:
            bot.send_message(chat_id=admin_id,
                             text=f"📝 Новый отзыв от @{update.message.from_user.username} ({chat_id}):\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Ваш отзыв принят. Спасибо!")
        user_states[chat_id] = None
        return "ok"

    if message == '📩 Оставить заявку':
        bot.send_message(chat_id=chat_id, text="Пожалуйста, напишите вашу заявку.")
        user_states[chat_id] = 'waiting_for_request'
        return "ok"

    if message == '📝 Оставить отзыв':
        bot.send_message(chat_id=chat_id, text="Пожалуйста, напишите ваш отзыв.")
        user_states[chat_id] = 'waiting_for_feedback'
        return "ok"

    # Если пришло что-то непонятное
    bot.send_message(chat_id=chat_id, text="ℹ️ Используйте кнопки меню или напишите /start для начала.")
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
