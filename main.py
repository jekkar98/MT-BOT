import os
from flask import Flask, request
import telegram

TOKEN = "7054901468:AAFqXIPgsDF_4Axh4Vhc0CH-xTSW6lvokp0"
ADMIN_IDS = [821932338, 384949127]  # Твои Telegram ID для получения заявок/отзывов

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Словарь для хранения состояния пользователя: что он сейчас вводит (заявку или отзыв)
user_states = {}

@app.route('/')
def index():
    return "MT-IT Bot is running."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    # Обработка команд /start, приветствия
    if message.lower() in ["/start", "старт", "привет"]:
        # Сброс состояния
        user_states.pop(chat_id, None)
        keyboard = telegram.ReplyKeyboardMarkup([['📩 Оставить заявку', '📝 Оставить отзыв']], resize_keyboard=True)
        bot.send_message(chat_id=chat_id, 
                         text="👋 Добро пожаловать в MT-IT!\n\nВыберите действие:", 
                         reply_markup=keyboard)
        return "ok"

    # Проверяем, что пользователь выбрал в меню
    if chat_id in user_states:
        state = user_states[chat_id]

        if state == "waiting_for_request":
            # Пользователь пишет текст заявки
            for admin_id in ADMIN_IDS:
                bot.send_message(chat_id=admin_id, 
                                 text=f"📬 Новая заявка от @{update.message.from_user.username} ({chat_id}):\n\n{message}")
            bot.send_message(chat_id=chat_id, text="✅ Ваша заявка принята. Спасибо!")
            user_states.pop(chat_id)
            return "ok"

        elif state == "waiting_for_review":
            # Пользователь пишет отзыв
            for admin_id in ADMIN_IDS:
                bot.send_message(chat_id=admin_id, 
                                 text=f"📝 Новый отзыв от @{update.message.from_user.username} ({chat_id}):\n\n{message}")
            bot.send_message(chat_id=chat_id, text="✅ Ваш отзыв принят. Спасибо!")
            user_states.pop(chat_id)
            return "ok"

    # Если пользователь нажал кнопку «Оставить заявку»
    if message == "📩 Оставить заявку":
        user_states[chat_id] = "waiting_for_request"
        bot.send_message(chat_id=chat_id, text="✍️ Пожалуйста, напишите вашу заявку в сообщении.")
        return "ok"

    # Если пользователь нажал кнопку «Оставить отзыв»
    if message == "📝 Оставить отзыв":
        user_states[chat_id] = "waiting_for_review"
        bot.send_message(chat_id=chat_id, text="✍️ Пожалуйста, напишите ваш отзыв в сообщении.")
        return "ok"

    # Если сообщение не распознано, подсказываем
    bot.send_message(chat_id=chat_id, 
                     text="ℹ️ Пожалуйста, используйте меню для выбора действия.\nНапишите /start для начала.")
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
