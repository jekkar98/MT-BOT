import os
import requests
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")  # Токен из настроек Render / .env
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://yourdomain.com/<токен>

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Установка webhook при старте
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    params = {"url": WEBHOOK_URL}
    resp = requests.get(url, params=params)
    print("Set webhook response:", resp.json())

@app.route("/")
def index():
    return "MT-IT Bot is running."

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message is None:
        return "ok"

    chat_id = update.message.chat.id
    message = update.message.text or ""

    # Обработка команд и сообщений
    if message.lower() in ["/start", "старт", "привет"]:
        keyboard = telegram.ReplyKeyboardMarkup(
            [["📩 Оставить заявку", "📝 Оставить отзыв"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        bot.send_message(chat_id=chat_id,
                         text="👋 Добро пожаловать в MT-IT!\n\nВыберите действие ниже:",
                         reply_markup=keyboard)
        return "ok"

    if message == "📩 Оставить заявку":
        bot.send_message(chat_id=chat_id, text="✍️ Пожалуйста, напишите вашу заявку в ответном сообщении.")
        return "ok"

    if message == "📝 Оставить отзыв":
        bot.send_message(chat_id=chat_id, text="✍️ Пожалуйста, напишите ваш отзыв в ответном сообщении.")
        return "ok"

    # Если сообщение не команда, считаем что это заявка или отзыв в зависимости от последнего действия
    # Для упрощения будем просто пересылать все сообщения, которые не команда

    # Пересылаем сообщение на твои ID
    admins = [821932338, 384949127]
    for admin_id in admins:
        bot.send_message(chat_id=admin_id,
                         text=f"📬 Новое сообщение от @{update.message.from_user.username} (ID: {chat_id}):\n\n{message}")

    bot.send_message(chat_id=chat_id, text="✅ Спасибо! Ваше сообщение получено.")
    return "ok"


if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
