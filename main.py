import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/')
def index():
    return "MT-IT Bot is running."

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message.lower() in ["/start", "старт", "привет"]:
        bot.send_message(chat_id=chat_id, text="👋 Добро пожаловать в MT-IT!\n\nНажмите кнопку ниже, чтобы оставить заявку.")
        keyboard = telegram.ReplyKeyboardMarkup([['📩 Оставить заявку']], resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text="Выберите действие:", reply_markup=keyboard)
        return "ok"

    if "заявка" in message.lower():
        bot.send_message(chat_id="821932338", text=f"📬 Новая заявка от @{update.message.from_user.username}:\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Заявка принята. Спасибо!")
    else:
        bot.send_message(chat_id=chat_id, text="ℹ️ Напишите 'заявка', чтобы оставить обращение.")

    return "ok"

if __name__ == "__main__":
    app.run(port=10000)
