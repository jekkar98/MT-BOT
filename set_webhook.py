import os
import telegram

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = telegram.Bot(token=TOKEN)

# URL должен совпадать с адресом твоего Render сервиса + '/' + TOKEN
WEBHOOK_URL = f"https://your-render-service.onrender.com/{TOKEN}"

def main():
    success = bot.set_webhook(WEBHOOK_URL)
    if success:
        print("Webhook установлен успешно")
    else:
        print("Не удалось установить webhook")

if __name__ == "__main__":
    main()
