import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
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
        keyboard = telegram.ReplyKeyboardMarkup([['📩 Оставить заявку', '📝 Оставить отзыв']], resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text="👋 Добро пожаловать в MT-IT!\n\nВыберите действие:", reply_markup=keyboard)
        return "ok"

    if message == '📩 Оставить заявку':
        bot.send_message(chat_id=chat_id, text="Пожалуйста, напишите свою заявку.")
        return "ok"
    elif message == '📝 Оставить отзыв':
        bot.send_message(chat_id=chat_id, text="Пожалуйста, напишите свой отзыв.")
        return "ok"

    if "заявка" in message.lower():
        bot.send_message(chat_id="821932338", text=f"📬 Новая заявка от @{update.message.from_user.username}:\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Заявка принята. Спасибо!")
        return "ok"
    elif "отзыв" in message.lower():
        bot.send_message(chat_id="821932338", text=f"📝 Новый отзыв от @{update.message.from_user.username}:\n\n{message}")
        bot.send_message(chat_id=chat_id, text="✅ Отзыв принят. Спасибо!")
        return "ok"

    bot.send_message(chat_id=chat_id, text="ℹ️ Напишите 'заявка' или 'отзыв', чтобы оставить обращение.")
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
