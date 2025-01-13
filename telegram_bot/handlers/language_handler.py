import os
import sys
import requests
import gettext
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from deep_translator import GoogleTranslator
from telebot import types
from telebot.types import Message
import requests
# import redis

# Load environment variables
load_dotenv()

# Initialize Redis client
# redis_host = os.getenv('REDIS_HOST', 'localhost')
# redis_port = os.getenv('REDIS_PORT', 6380)

# try:
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
#     redis_client.ping()  # Check if the connection is successful
# except redis.ConnectionError as e:
#     print(f"Redis connection error: {e}")
#     redis_client = None

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://web:5000")


def translate(text, target_lang='es'):
    """Translate text to the target language using GoogleTranslator."""
    if target_lang == 'es':
        return text
    return GoogleTranslator(source='auto', target=target_lang).translate(text)


def get_language_by_telegram_id(cid):
    # """Fetch the user's language preference via an API request."""
    # response = requests.get(f"{BASE_URL}/languages/{cid}")
    # if response.status_code == 200:
    #     return response.json().get('language', 'es')
    return 'es'
    
# Fetch language preference from API
def fetch_language_from_db(telegram_id):
    # """Fetch language preference from API by Telegram ID."""
    # response = requests.get(f"{BASE_URL}/languages/{telegram_id}")
    # if response.status_code == 200:
    #     return response.json().get('Language', 'es')
    return 'es'

def edit_language(bot, message):
    """Handle the language editing process."""
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("English", "Español")
    bot.send_message(cid, translate("Seleccione su idioma:"), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: set_user_language(bot, msg))

def change_language(cid, language_code):
    """Update the user's language preference via an API request and delete the Redis cache."""
    redis_client.delete(f"language:{cid}")
    url = f"{BASE_URL}//languages/{cid}"
    data = {'language': language_code}
    response = requests.put(url, json=data)       
    
    return response

def set_user_language(bot, message):
    """Set the user's language preference."""
    cid = message.chat.id
    language = message.text.strip().lower()
    if language == "english":
        change_language(cid, 'en')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton("/menu")
        markup.row(item1)
        bot.send_message(cid, translate("Idioma cambiado a Inglés.", 'en'), reply_markup=markup)

    elif language == "español":
        change_language(cid, 'es')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton("/menu")
        markup.row(item1)
        bot.send_message(cid, translate("Idioma cambiado a Español.", 'es'), reply_markup=markup)
    else:
        bot.send_message(cid, translate("Idioma no reconocido. Por favor, seleccione 'English' o 'Español'."))
        edit_language(bot, message)
