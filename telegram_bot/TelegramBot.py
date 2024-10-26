import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.language_handler import edit_language, language_middleware
from handlers.user_handler import get_user, create_user, update_user

# Load .env file
load_dotenv()

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
@language_middleware
def command_start(message):
    cid = message.chat.id
    nom = message.chat.first_name
    bot.send_message(cid, f"Bienvenido al Rhino Bot {nom} - {cid}, podrás registrar tus pagos, ver sedes, precios y mucho más {nom}")
    command_list(message)

@bot.message_handler(commands=['list'])
@language_middleware
def command_list(message):
    cid = message.chat.id
    help_text = _("available")

    # Set up buttons with translated text
    buttons = [
        [InlineKeyboardButton(_("register"), callback_data="create_user")],
        [InlineKeyboardButton(_("plans"), callback_data="listSwing")],
        [InlineKeyboardButton(_("locations"), callback_data="SetSignalStatus")],
        [InlineKeyboardButton(_("schedule"), callback_data="BinanceGainers")],
        [InlineKeyboardButton(_("payment"), callback_data="BinanceGainersAutoList")],
        [InlineKeyboardButton(_("administrator"), callback_data="TechnicalAnalisys")],
        [InlineKeyboardButton(_("language"), callback_data="edit_language")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(cid, help_text, reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    options = {
        'List': command_list,
        'edit_language': lambda msg: edit_language(bot, msg),
        'create_user': lambda msg: create_user(bot, msg),
    }
    func = options.get(call.data)
    if func:
        func(call.message)

bot.polling()
