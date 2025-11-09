# bot.py
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv


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
    if not TOKEN or TOKEN == "PUT_YOUR_TOKEN_HERE":
        raise RuntimeError("TG_BOT_TOKEN не вказаний!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.bot_data['welcome_text'] = WELCOME_TEXT

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about_cmd))

    menu_register(app)
    admin_register(app)

    # Налаштування webhook
    PORT = int(os.environ.get("PORT", 5000))
    URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render дає цей env

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{URL}/webhook/{TOKEN}"
    )

if __name__ == "__main__":
    main()
