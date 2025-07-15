import os
from flask import Flask, request
import telegram
import asyncio

TOKEN = "7054901468:AAFqXIPgsDF_4Axh4Vhc0CH-xTSW6lvokp0"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/')
def index():
    return "MT-IT Bot is running."

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    asyncio.run(handle_update(update))
    return "ok"

async def handle_update(update):
    chat_id = update.message.chat.id
    message = update.message.text

    if message.lower() in ["/start", "старт", "привет"]:
        keyboard = telegram.ReplyKeyboardMarkup([['📩 Оставить заявку']], resize_keyboard=True)
        await bot.send_message(chat_id=chat_id, text="👋 Добро пожаловать в MT-IT!\n\nНажмите кнопку ниже, чтобы оставить заявку.")
        await bot.send_message(chat_id=chat_id, text="Выберите действие:", reply_markup=keyboard)
        return

    if "заявка" in message.lower():
        admins = ["821932338", "384949127"]
        for admin_id in admins:
            await bot.send_message(
                chat_id=admin_id,
                text=f"📬 Новая заявка от @{update.message.from_user.username}:\n\n{message}"
            )
        await bot.send_message(chat_id=chat_id, text="✅ Заявка принята. Спасибо!")
    else:
        await bot.send_message(chat_id=chat_id, text="ℹ️ Напишите 'заявка', чтобы оставить обращение.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
