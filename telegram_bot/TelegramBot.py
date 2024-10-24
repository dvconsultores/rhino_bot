import os
from dotenv import load_dotenv
import telebot
import gettext
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load .env file
load_dotenv()

# Configure gettext
def set_language(language):
    locale_path = os.path.join(os.path.dirname(__file__), 'locales')
    lang = gettext.translation('messages', localedir=locale_path, languages=[language])
    lang.install()
    return lang.gettext

# Default language
_ = set_language('es')

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

user_languages = {}

def language_middleware(func):
    def wrapper(message):
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'es')  # Default to Spanish
        global _
        _ = set_language(language)
        return func(message)
    return wrapper

@bot.message_handler(commands=['set_language'])
def set_language_command(message):
    cid = message.chat.id
    user_id = message.from_user.id
    language = message.text.split()[1] if len(message.text.split()) > 1 else 'es'
    user_languages[user_id] = language
    bot.send_message(cid, f"Language set to {language}")

@bot.message_handler(commands=['start'])
@language_middleware
def command_start(message):
    cid = message.chat.id
    nom = message.chat.first_name
    bot.send_message(cid, f"Bienvenido al Rhino Bot {nom} - {cid}, podrás registrar tus pagos, ver sedes, precios y mucho más {nom}")
    command_list(message)

def clear_message_text(message):
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='')

@bot.message_handler(commands=['list'])
@language_middleware
def command_list(message):
    cid = message.chat.id
    help_text = _("available")

    # Use gettext translations
    button1 = InlineKeyboardButton(_("register"), callback_data="listLongTrade")
    button2 = InlineKeyboardButton(_("plans"), callback_data="listSwing")
    button3 = InlineKeyboardButton(_("locations"), callback_data="SetSignalStatus")
    button4 = InlineKeyboardButton(_("schedule"), callback_data="BinanceGainers")
    button5 = InlineKeyboardButton(_("payment"), callback_data="BinanceGainersAutoList")
    button6 = InlineKeyboardButton(_("administrator"), callback_data="TechnicalAnalisys")
    button7 = InlineKeyboardButton(_("language"), callback_data="TechnicalAnalisys")
    
    buttons = [[button1], [button2], [button3], [button4], [button5], [button6], [button7]]
    buttons[1].sort(key=lambda btn: btn.text)

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(cid, help_text, reply_markup=reply_markup)

bot.polling()