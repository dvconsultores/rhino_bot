import os
import gettext
import requests
from telebot import types
from telebot.types import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

# Configure gettext
def set_language(language):
    """Set the language for translations using gettext."""
    locale_path = os.path.join(os.path.dirname(__file__), '..', 'locales')
    lang = gettext.translation('messages', localedir=locale_path, languages=[language])
    lang.install()
    return lang.gettext

# Initialize default language to Spanish
_ = set_language('es')

# Fetch language preference from API
def fetch_language_from_db(telegram_id):
    """Fetch language preference from API by Telegram ID."""
    response = requests.get(f"{BASE_URL}/languages/{telegram_id}")
    if response.status_code == 200:
        language_data = response.json()
        return language_data['Language']
    else:
        print(f"Error fetching language: {response.status_code}")
        return 'es'  # Default to Spanish if there's an error

# Middleware for handling language based on user preference
def language_middleware(func):
    """Middleware to set language for each user."""
    def wrapper(message):
        if not isinstance(message, Message):
            raise AttributeError("The message object is not of type 'Message'")
        telegram_id = message.chat.id
        language = fetch_language_from_db(telegram_id)
        global _
        _ = set_language(language)
        return func(message)
    return wrapper

# Function to handle language selection
def edit_language(bot, message):
    """Prompt user to select a language."""
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton('ES'), types.KeyboardButton('EN'))
    markup.row(types.KeyboardButton(_("cancel")))
    bot.send_message(cid, _("language_text"), reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, language_handler, bot=bot)

def language_handler(message, bot):
    """Handle user's selected language and update it."""
    cid = message.chat.id
    global _
    text = message.text.upper()  # Normalize to uppercase to avoid case issues

    if text == _("cancel"):
        bot.send_message(cid, _("options"), reply_markup=types.ReplyKeyboardMarkup().add('/list'))
        return

    if text not in ['ES', 'EN']:
        bot.send_message(cid, _("language_error"))
        bot.register_next_step_handler_by_chat_id(cid, language_handler, bot=bot)
        return  

    # Update language setting in the database
    bot.send_message(cid, _("procesing"))
    language_code = 'es' if text == 'ES' else 'en'
    data = {'id_telegram': cid, 'Language': language_code}
    response = requests.put(f"{BASE_URL}/languages/{cid}", json=data)
    if response.status_code == 200:
        _ = set_language(language_code)
    bot.send_message(cid, _("language_set"), reply_markup=types.ReplyKeyboardMarkup().add('/list'))
