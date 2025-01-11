import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from datetime import datetime

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


def cancel_process(bot, message):
    """Handle the cancellation of the process."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("/menu"))
    bot.send_message(cid, translate("Proceso cancelado.", target_lang), reply_markup=markup)


def add_attendance_handler(bot, message):
    """Start the process of adding an attendance record with coach, location, user, and date."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    bot.send_message(cid, translate("Registro diario de coach:", target_lang))
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
    """Handle the selection of a coach and proceed to user selection."""
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

    bot.send_message(cid, translate("Por favor, seleccione un usuario (cliente):", target_lang))
    list_users_for_attendance(bot, message, selected_coach['id'])


def list_users_for_attendance(bot, message, coach_id):
    """List all available users for attendance."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/users")  # Assuming the endpoint to fetch users

    if response.status_code == 200:
        users = response.json()

        if users:
            users_text = translate("Elija un usuario:\n", target_lang)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for user in users:
                markup.add(types.KeyboardButton(f"{user['cedula']}: {user['name']} {user['lastname']}"))
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, users_text, reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: handle_user_selection(bot, msg, coach_id, users))
        else:
            bot.send_message(cid, translate("No hay usuarios disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los usuarios.", target_lang))


def handle_user_selection(bot, message, coach_id, users):
    """Handle the selection of a user and proceed to location selection."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    # Extract the input text and split it by ":"
    user_input = message.text.strip()
    try:
        input_cedula = user_input.split(":")[0].strip()
    except IndexError:
        bot.send_message(cid, translate("Entrada inválida. Por favor, seleccione un usuario válido con el formato proporcionado.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_users_for_attendance(bot, msg, coach_id))
        return

    # Validate both the cedula and the full string
    selected_user = next((user for user in users if str(user['cedula']) == input_cedula and f"{user['cedula']}: {user['name']} {user['lastname']}" == user_input), None)

    if not selected_user:
        bot.send_message(cid, translate("Usuario inválido. Por favor, seleccione un usuario válido.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_users_for_attendance(bot, msg, coach_id))
        return

    # Proceed to location selection
    bot.send_message(cid, translate("Por favor, seleccione una ubicación:", target_lang))
    list_locations_for_attendance(bot, message, coach_id, selected_user['id'])



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
                # Show location ID and name for better validation
                markup.add(types.KeyboardButton(f"{location['id']}: {location['location']}"))
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

    # Extract location ID from user input
    user_input = message.text.strip()
    try:
        input_location_id = user_input.split(":")[0].strip()
    except IndexError:
        bot.send_message(cid, translate("Entrada inválida. Por favor, seleccione una ubicación válida.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_locations_for_attendance(bot, msg, coach_id, user_id))
        return

    # Validate both the location ID and full string
    selected_location = next((loc for loc in locations if str(loc['id']) == input_location_id and f"{loc['id']}: {loc['location']}" == user_input), None)

    if not selected_location:
        bot.send_message(cid, translate("Ubicación inválida. Por favor, seleccione una ubicación válida.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_locations_for_attendance(bot, msg, coach_id, user_id))
        return

    # Automatically set the date to today's date
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    # Submit the data to the backend
    data = {
        'coach_id': coach_id,
        'user_id': user_id,
        'location_id': selected_location['id'],
        'date': date
    }
    response = requests.post(f"{BASE_URL}/attendances", json=data)

    if response.status_code == 201:
        # Set up buttons with translated text
        buttons = [
            [InlineKeyboardButton(translate("🏅 Nuevo registro", target_lang), callback_data="add_attendance_handler")],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.send_message(cid, translate("¡Asistencia registrada con éxito!", target_lang), reply_markup=reply_markup)
    else:
        bot.send_message(cid, translate("Error al registrar la asistencia. Por favor, inténtelo de nuevo.", target_lang))

