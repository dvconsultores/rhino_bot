import os
from dotenv import load_dotenv
import telebot
from telebot import types
import gettext
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Load .env file
load_dotenv()

# Configure gettext
def set_language(language):
    locale_path = os.path.join(os.path.dirname(__file__), 'locales')
    lang = gettext.translation('messages', localedir=locale_path, languages=[language])
    lang.install()
    return lang.gettext

    print(f"Error: {response.status_code}")

# Default language
_ = set_language('es')

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

user_languages = {}

# Fetch language data from the API
def fetch_language_from_db(telegram_id):
    response = requests.get(f'http://127.0.0.1:5000/languages/{telegram_id}')
    if response.status_code == 200:
        language_data = response.json()
        return language_data['Language']
    else:
        print(f"Error: {response.status_code}")
        return 'es'  # Default to Spanish if there's an error

def language_middleware(func):
    def wrapper(message):
        if not isinstance(message, Message):
            raise AttributeError("The message object is not of type 'Message'")
        telegram_id = message.chat.id
        language = fetch_language_from_db(telegram_id)
        global _
        _ = set_language(language)
        return func(message)
    return wrapper

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

    # Use gettext translations
    button1 = InlineKeyboardButton(_("register"), callback_data="listLongTrade")
    button2 = InlineKeyboardButton(_("plans"), callback_data="listSwing")
    button3 = InlineKeyboardButton(_("locations"), callback_data="SetSignalStatus")
    button4 = InlineKeyboardButton(_("schedule"), callback_data="BinanceGainers")
    button5 = InlineKeyboardButton(_("payment"), callback_data="BinanceGainersAutoList")
    button6 = InlineKeyboardButton(_("administrator"), callback_data="TechnicalAnalisys")
    button7 = InlineKeyboardButton(_("language"), callback_data="edit_language")
    
    buttons = [[button1], [button2], [button3], [button4], [button5], [button6], [button7]]
    buttons[1].sort(key=lambda btn: btn.text)

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(cid, help_text, reply_markup=reply_markup)

# Callback_Handler
# This code creates a dictionary called options that maps the call.data to the corresponding function. 
# The get() method is used to retrieve the function based on the call.data. If the function exists
# , it is called passing the call.message as argument. 
# This approach avoids the need to use if statements to check the value of call.data for each possible option.
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    # Define the mapping between call.data and functions
    options = {
        'List' : command_list,
        'edit_language' : edit_language
    }
    # Get the function based on the call.data
    func = options.get(call.data)

    # Call the function if it exists
    if func:
        func(call.message) 

@bot.message_handler(func=lambda message: True)
@language_middleware
def edit_language(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item_es = types.KeyboardButton('ES')
    item_en = types.KeyboardButton('EN') 
    item_cancel = types.KeyboardButton(_("cancel"))
    markup.row(item_es)
    markup.row(item_en)
    markup.row(item_cancel)
    bot.send_message(cid, _("language_text"), parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, language_handler)  # Registers the next handler to capture language choice

@bot.message_handler(func=lambda message: True)
@language_middleware
def language_handler(m):
    cid = m.chat.id
    global _
    text = m.text.upper()  # Normalize to uppercase to avoid case issues
    
    if text ==  _("cancel"):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item = types.KeyboardButton('/list')
        markup.row(item)
        bot.send_message(cid, _("options"), parse_mode='Markdown', reply_markup=markup)
        return

    if text not in ['ES', 'EN']:
        # Invalid input: prompt user again
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item_es = types.KeyboardButton('ES')
        item_en = types.KeyboardButton('EN')
        item_cancel = types.KeyboardButton(_("cancel"))
        markup.row(item_es)
        markup.row(item_en)
        markup.row(item_cancel)
        bot.send_message(cid, _("language_error"), parse_mode='Markdown', reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(cid, language)  # Re-register to handle invalid input
        return  

    # Valid input: update language setting
    bot.send_message(cid, _("procesing"))
    language_code = 'es' if text == 'ES' else 'en'
    data = {'id_telegram': cid, 'Language': language_code}
    response = requests.put(f'http://localhost:5000/languages/{cid}', json=data)
    if response.status_code == 200:
        _ = set_language(language_code)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item = types.KeyboardButton('/list')
    markup.row(item)
    bot.send_message(cid, _("language_set"), parse_mode='Markdown', reply_markup=markup)


bot.polling()