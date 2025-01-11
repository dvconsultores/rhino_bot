import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()

# Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

def translate(text, target_lang='es'):
    """Translate text to the target language using GoogleTranslator."""
    if target_lang == 'es':
        return text
    return GoogleTranslator(source='auto', target=target_lang).translate(text)


def get_language_by_telegram_id(cid):
    """Fetch the user's language preference via an API request."""
    response = requests.get(f"{BASE_URL}/languages/{cid}")
    if response.status_code == 200:
        return response.json().get('language', 'es')
    return 'es'
    
def add_attendance_handler(bot, message):
    """Start the process of adding an attendance record with coach, location, user, and date."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    bot.send_message(cid, translate("Por favor, seleccione un entrenador:", target_lang))
    list_coaches_for_attendance(bot, message)


def list_coaches_for_attendance(bot, message):
    """List all available coaches for attendance."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/coaches")

    if response.status_code == 200:
        coaches = response.json()

        if coaches:
            coaches_text = translate("Elija un entrenador:\n", target_lang)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for coach in coaches:
                button = types.KeyboardButton(f"{coach['id']}: {coach['names']}")
                markup.add(button)
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, coaches_text, reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: handle_coach_selection(bot, msg, coaches))
        else:
            bot.send_message(cid, translate("No hay entrenadores disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los entrenadores.", target_lang))


def handle_coach_selection(bot, message, coaches):
    """Handle the selection of a coach and ask for the user ID."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    selected_coach = next((coach for coach in coaches if f"{coach['id']}: {coach['names']}" == message.text.strip()), None)

    if not selected_coach:
        bot.send_message(cid, translate("Entrenador inválido. Por favor, seleccione un entrenador válido.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_coaches_for_attendance(bot, msg))
        return

    bot.send_message(cid, translate("Por favor, ingrese el ID del usuario (cliente):", target_lang))
    bot.register_next_step_handler(message, lambda msg: handle_user_id_input(bot, msg, selected_coach['id']))


def handle_user_id_input(bot, message, coach_id):
    """Handle the input for the user ID and ask for the location."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    user_id = message.text.strip()
    if not user_id.isdigit():
        bot.send_message(cid, translate("ID del usuario inválido. Por favor, ingrese un número válido:", target_lang))
        bot.register_next_step_handler(message, lambda msg: handle_user_id_input(bot, msg, coach_id))
        return

    bot.send_message(cid, translate("Por favor, seleccione una ubicación:", target_lang))
    bot.register_next_step_handler(message, lambda msg: list_locations_for_attendance(bot, msg, coach_id, int(user_id)))


def list_locations_for_attendance(bot, message, coach_id, user_id):
    """List all available locations for attendance."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/locations")

    if response.status_code == 200:
        locations = response.json()

        if locations:
            locations_text = translate("Elija una ubicación:\n", target_lang)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for location in locations:
                markup.add(types.KeyboardButton(location['location']))
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, locations_text, reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: handle_location_selection(bot, msg, coach_id, user_id, locations))
        else:
            bot.send_message(cid, translate("No hay ubicaciones disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener las ubicaciones.", target_lang))


def handle_location_selection(bot, message, coach_id, user_id, locations):
    """Handle the selection of the location."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    selected_location = next((loc for loc in locations if loc['location'] == message.text.strip()), None)

    if not selected_location:
        bot.send_message(cid, translate("Ubicación inválida. Por favor, seleccione una ubicación válida.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_locations_for_attendance(bot, msg, coach_id, user_id))
        return

    bot.send_message(cid, translate("Por favor, ingrese la fecha (formato YYYY-MM-DD):", target_lang))
    bot.register_next_step_handler(message, lambda msg: handle_date_input(bot, msg, coach_id, user_id, selected_location))


def handle_date_input(bot, message, coach_id, user_id, location):
    """Handle the input for the date and submit the data."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    date = message.text.strip()
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        bot.send_message(cid, translate("Fecha inválida. Por favor, ingrese una fecha en el formato YYYY-MM-DD:", target_lang))
        bot.register_next_step_handler(message, lambda msg: handle_date_input(bot, msg, coach_id, user_id, location))
        return

    # Submit the data to the backend
    data = {
        'coach_id': coach_id,
        'user_id': user_id,
        'location_id': location['id'],
        'date': date
    }
    response = requests.post(f"{BASE_URL}/attendances", json=data)

    if response.status_code == 201:
        bot.send_message(cid, translate("¡Asistencia registrada con éxito!", target_lang))
    else:
        bot.send_message(cid, translate("Error al registrar la asistencia. Por favor, inténtelo de nuevo.", target_lang))
