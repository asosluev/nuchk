# handlers/menu.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
import json
from pathlib import Path
from config import MENU_FILE, INFO_FILE, CB_PREFIX

class MenuManager:
    def __init__(self):
        self.menu = {}
        self.info = {}
        self.load()

    def load(self):
        """(Re)load menu and info from JSON files."""
        if not MENU_FILE.exists():
            raise FileNotFoundError(f"Menu file not found: {MENU_FILE}")
        if not INFO_FILE.exists():
            raise FileNotFoundError(f"Info file not found: {INFO_FILE}")

        with open(MENU_FILE, 'r', encoding='utf-8') as f:
            self.menu = json.load(f)

        with open(INFO_FILE, 'r', encoding='utf-8') as f:
            self.info = json.load(f)

    def get_node_by_path(self, path: list):
        """Повертає вузол меню за шляхом path (list)."""
        node = self.menu
        if not path:
            return node
        items = node.get('items', [])
        for key in path:
            found = None
            for it in items:
                if it.get('key') == key:
                    found = it
                    break
            if not found:
                return None
            node = found
            items = node.get('children', []) or node.get('items', [])
        return node

    def build_markup(self, node: dict, path: list):
        """Створює InlineKeyboardMarkup для вузла."""
        kb = []
        child_list = node.get('items') or node.get('children') or []

        for item in child_list:
            key = item.get('key')
            text = item.get('text', key)
            cb = CB_PREFIX + '/'.join(path + [key]) if (path or key) else CB_PREFIX
            kb.append([InlineKeyboardButton(text, callback_data=cb)])

        if path:
            back_path_cb = CB_PREFIX + '/'.join(path[:-1]) if len(path) > 1 else CB_PREFIX
            kb.append([InlineKeyboardButton('⬅️ Назад', callback_data=back_path_cb)])

        return InlineKeyboardMarkup(kb)

menu_manager = MenuManager()

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = context.bot_data.get('welcome_text') or 'Оберіть пункт меню:'
    markup = menu_manager.build_markup(menu_manager.menu, [])
    if update.message:
        await update.message.reply_text(text, reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=markup)

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ''
    if not data.startswith(CB_PREFIX):
        await query.message.edit_text("Невідома дія.")
        return

    path_raw = data[len(CB_PREFIX):].lstrip('/')
    path = path_raw.split('/') if path_raw else []

    node = menu_manager.get_node_by_path(path)
    if node is None:
        await query.message.edit_text('Пункт не знайдено.')
        return

    node_key = node.get('key')
    content = menu_manager.info.get(node_key) if node_key else None
    markup = menu_manager.build_markup(node, path)

    # --- Видаляємо попередню картинку, якщо вона була ---
    prev_img_id = context.user_data.get('image_message_id')
    prev_chat_id = context.user_data.get('image_chat_id')
    if prev_img_id and prev_chat_id:
        try:
            await context.bot.delete_message(chat_id=prev_chat_id, message_id=prev_img_id)
        except:
            pass
        context.user_data.pop('image_message_id', None)
        context.user_data.pop('image_chat_id', None)

    # --- Спеціальні кейси ---
    if node_key == 'consult':
        consult = menu_manager.info.get('contacts', {}).get('consultant_username')
        if consult:
            await query.message.edit_text(f"Зв'язатися з консультантом: {consult}", reply_markup=markup)
            return
        contacts = menu_manager.info.get('contacts', {})
        text_to_send = 'Контакти:\n'
        if contacts.get('phone'):
            text_to_send += f"Телефон: {contacts.get('phone')}\n"
        if contacts.get('email'):
            text_to_send += f"Email: {contacts.get('email')}\n"
        await query.message.edit_text(text_to_send, reply_markup=markup)
        return

    if node_key == 'faq':
        faqs = menu_manager.info.get('faq', [])
        if not faqs:
            await query.message.edit_text('FAQ порожній.', reply_markup=markup)
            return
        text_to_send = '\n\n'.join([f"Q: {f.get('q')}\nA: {f.get('a')}" for f in faqs])
        await query.message.edit_text(text_to_send, reply_markup=markup)
        return

    if node_key == 'news':
        news = menu_manager.info.get('news', [])
        if not news:
            await query.message.edit_text('Новин немає.', reply_markup=markup)
            return
        text_lines = [f"{n.get('date')} — {n.get('title')}\n{n.get('text')}" for n in news[:3]]
        text_to_send = "\n\n".join(text_lines)
        await query.message.edit_text(text_to_send, reply_markup=markup)
        return

    # --- Контент з картинкою ---
    if content and isinstance(content, dict):
        text = content.get("text", "")
        image = content.get("image")
        images = content.get("images")

        # Надсилаємо картинку/галерею окремо
        if image:
            msg = await query.message.reply_photo(photo=image)
            context.user_data['image_message_id'] = msg.message_id
            context.user_data['image_chat_id'] = msg.chat_id
        elif images:
            for i, img in enumerate(images):
                msg = await query.message.reply_photo(photo=img)
                if i == 0:
                    context.user_data['image_message_id'] = msg.message_id
                    context.user_data['image_chat_id'] = msg.chat_id

        # Редагуємо текстове повідомлення з кнопками (не створюємо нове)
        text_to_send = text or node.get('text') or "Інформація відсутня."
        await query.message.edit_text(text_to_send, reply_markup=markup)
        return

    # --- Дочірні вузли або простий текст без картинки ---
    children = node.get('children') or node.get('items')
    if children:
        text_to_send = node.get('text') or node.get('title') or 'Оберіть пункт меню:'
        await query.message.edit_text(text_to_send, reply_markup=markup)
        return

    if isinstance(content, str):
        await query.message.edit_text(content, reply_markup=markup)
        return

    # fallback
    text_to_send = node.get('text') or "Інформація недоступна."
    await query.message.edit_text(text_to_send, reply_markup=markup)

def register_handlers(application):
    application.add_handler(CallbackQueryHandler(menu_callback, pattern=f'^{CB_PREFIX}'))
