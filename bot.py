# bot.py
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from config import TOKEN, WELCOME_TEXT
from handlers.menu import start_menu, register_handlers as menu_register
from handlers.admin import register_handlers as admin_register
from handlers.menu import menu_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команди
async def start_cmd(update, context):
    # Викликаємо функцію, яка посилає головне меню
    await start_menu(update, context)

async def help_cmd(update, context):
    text = (
        "/start — головне меню\n"
        "/help — ця довідка\n"
        "/about — коротко про університет\n"
        "/reload — перезавантажити menu.json (тільки адміни)\n"
    )
    await update.message.reply_text(text)

async def about_cmd(update, context):
    about = menu_manager.info.get('about', 'Інформація про університет відсутня.')
    await update.message.reply_text(about)

def main():
    if TOKEN == 'PUT_YOUR_TOKEN_HERE' or not TOKEN:
        raise RuntimeError("TG_BOT_TOKEN не вказаний в .env або в середовищі")

    application = ApplicationBuilder().token(TOKEN).build()

    # Зберігаємо привітальний текст у bot_data
    application.bot_data['welcome_text'] = WELCOME_TEXT

    # Стандартні команди
    application.add_handler(CommandHandler('start', start_cmd))
    application.add_handler(CommandHandler('help', help_cmd))
    application.add_handler(CommandHandler('about', about_cmd))

    # Реєстрація хендлерів меню та адмін-панелі
    menu_register(application)
    admin_register(application)


# --- Запуск ---
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN не знайдено у .env")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    WEBHOOK_URL = f"https://{HOSTNAME}/webhook"

    print(f"✅ Webhook URL: {WEBHOOK_URL}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

  #  logger.info("Bot started (polling).")
  #  application.run_polling()

#if __name__ == '__main__':#
#    main()
