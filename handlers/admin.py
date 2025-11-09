# handlers/admin.py
"""
Прості адмін-команди: /reload, /admin
ADMINS визначені в config.ADMINS (user_id як рядок або @username)
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ADMINS
from handlers.menu import menu_manager

def _normalize_admins():
    # повертаємо список рядків для порівняння
    return [str(a).strip() for a in ADMINS]

def is_admin(user):
    """Перевірка: чи є user в ADMINS (по id або username)."""
    admins = _normalize_admins()
    if str(user.id) in admins:
        return True
    if user.username and ('@' + user.username) in admins:
        return True
    return False

async def reload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезавантажити menu.json та info.json (тільки для адмінів)."""
    user = update.effective_user
    if not is_admin(user):
        await update.message.reply_text('Немає доступу. Ви не адмін.')
        return
    try:
        menu_manager.load()
        await update.message.reply_text('Конфігурація перезавантажена.')
    except Exception as e:
        await update.message.reply_text(f'Помилка при перезавантаженні: {e}')

async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        await update.message.reply_text('Немає доступу. Ви не адмін.')
        return
    await update.message.reply_text('Ви — адміністратор. Доступні команди: /reload')

def register_handlers(application):
    application.add_handler(CommandHandler('reload', reload_cmd))
    application.add_handler(CommandHandler('admin', admin_info))
