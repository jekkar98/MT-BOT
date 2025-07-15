import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из переменной окружения
ADMIN_IDS = [821932338, 384949127]  # Список ID админов, которым будут приходить заявки и отзывы

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "MT-IT Bot is running."

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    if update.message is None:
        return "ok"

    chat_id = update.message.chat.id
    message = update.message.text

    if message is None:
        return "ok"

    # Обработка команд /start и вариаций
    if message.lower() in ["/start", "старт", "привет"]:
        keyboard = telegram.ReplyKeyboardMarkup(
            [['📩 Оставить заявку', '✍️ Оставить отзыв']],
            resize_keyboard=True
        )
        bot.send_message(chat_id=chat_id, 
                         text="👋 Добро пожаловать в MT-IT!\n\nВыберите действие:", 
                         reply_markup=keyboard)
        return "ok"

    # Обработка заявки
    if message.lower().startswith("заявка") or message == '📩 Оставить заявку':
        bot.send_message(chat_id=chat_id, text="Пожалуйста, напишите вашу заявку.")
        return "ok"

    # Обработка отзыва
    if message.lower().startswith("отзыв") or message == '✍️ Оставить отзыв':
        bot.send_message(chat_id=chat_id, text="Пожалуйста, напишите ваш отзыв.")
        return "ok"

    # Если пользователь написал текст — пересылаем админам с пометкой кто и что написал
    forward_text = f"📬 Сообщение от @{update.message.from_user.username or update.message.from_user.full_name} (id {chat_id}):\n\n{message}"
    for admin_id in ADMIN_IDS:
        bot.send_message(chat_id=admin_id, text=forward_text)
    
    # Подтверждение пользователю
    bot.send_message(chat_id=chat_id, text="✅ Спасибо! Ваше сообщение получено.")

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
