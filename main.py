import os
from flask import Flask, request
import telegram

# Просто токен напрямую
bot = telegram.Bot(token="7054901468:AAFqXIPgsDF_4Axh4Vhc0CH-xTSW6lvokp0")

app = Flask(__name__)

@app.route('/')
def index():
    return "MT-IT Bot is running."

# Вебхук на правильный путь
@app.route("/webhook", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message.lower() in ["/start", "старт", "привет"]:
        keyboard = telegram.ReplyKeyboardMarkup([['📩 Оставить заявку']], resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text="👋 Добро пожаловать в MT-IT!\n\nНажмите кнопку ниже, чтобы оставить заявку.", reply_markup=keyboard)
        return "ok"

    if "заявка" in message.lower():
        bot.send_message(chat_id="821932338", text=f"📬 Новая заявка от @{update.message.from_user.username}:\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Заявка принята. Спасибо!")
    else:
        bot.send_message(chat_id=chat_id, text="ℹ️ Напишите 'заявка', чтобы оставить обращение.")

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
