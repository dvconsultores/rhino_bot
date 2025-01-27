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
BASE_URL = os.getenv("API_BASE_URL", "http://web:5000")

# Temporary session storage
user_session_data = {}

def translate(text, target_lang='es'):
    """Translate text to the target language using GoogleTranslator."""
    if target_lang == 'es':
        return text
    return GoogleTranslator(source='auto', target=target_lang).translate(text)

def get_language_by_telegram_id(cid):
    return 'es'

def cancel_process(bot, message):
    """Handle the cancellation of the process."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    user_session_data.pop(cid, None)  # Clear session data
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("/menu"))
    bot.send_message(cid, translate("Proceso cancelado.", target_lang), reply_markup=markup)

def add_attendance_handler(bot, message):
    """Start the process of adding an attendance record."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    bot.send_message(cid, translate("Registro diario de asistencia:", target_lang))
    list_coaches_for_attendance(bot, message)

def list_coaches_for_attendance(bot, message):
    """List all available coaches for attendance."""
    cid = message.chat.idh
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

    # Store coach in session data
    user_session_data[cid] = {'coach_id': selected_coach['id']}
    bot.send_message(cid, translate("Por favor, seleccione un usuario (cliente):", target_lang))
    list_users_for_attendance(bot, message)

def list_users_for_attendance(bot, message):
    """List all available users for attendance."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/users")

    if response.status_code == 200:
        users = response.json()

        if users:
            users_text = translate("Elija un usuario:\n", target_lang)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for user in users:
                markup.add(types.KeyboardButton(f"{user['cedula']}: {user['name']} {user['lastname']}"))
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, users_text, reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: handle_user_selection(bot, msg, users))
        else:
            bot.send_message(cid, translate("No hay usuarios disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los usuarios.", target_lang))

def handle_user_selection(bot, message, users):
    """Handle the selection of a user and proceed to location selection."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    user_input = message.text.strip()

    # Try to find the user based on input
    selected_user = None
    if ":" in user_input:  # Input matches button format "<cedula>: <name> <lastname>"
        input_cedula = user_input.split(":")[0].strip()
        selected_user = next((user for user in users if str(user['cedula']) == input_cedula and f"{user['cedula']}: {user['name']} {user['lastname']}" == user_input), None)
    else:  # Input is just the cedula
        input_cedula = user_input.strip()
        selected_user = next((user for user in users if str(user['cedula']) == input_cedula), None)

    if not selected_user:
        bot.send_message(cid, translate("Usuario inválido. Por favor, seleccione un usuario válido o ingrese el número de cédula.", target_lang))
        bot.register_next_step_handler(message, lambda msg: handle_user_selection(bot, msg, users))
        return

    # Store user in session data
    if cid not in user_session_data:
        user_session_data[cid] = {}
    user_session_data[cid]['user_id'] = selected_user['id']

    # Check if location is already stored
    if 'location' in user_session_data[cid]:
        # If location is stored, skip location selection
        submit_attendance(bot, message, user_session_data[cid]['location'])
    else:
        # If location is not stored, proceed to location selection
        bot.send_message(cid, translate("Por favor, seleccione una ubicación:", target_lang))
        list_locations_for_attendance(bot, message)


def list_locations_for_attendance(bot, message):
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
                markup.add(types.KeyboardButton(f"{location['id']}: {location['location']}"))
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, locations_text, reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: handle_location_selection(bot, msg, locations))
        else:
            bot.send_message(cid, translate("No hay ubicaciones disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener las ubicaciones.", target_lang))

def handle_location_selection(bot, message, locations):
    """Handle the selection of the location."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    user_input = message.text.strip()
    try:
        input_location_id = user_input.split(":")[0].strip()
    except IndexError:
        bot.send_message(cid, translate("Entrada inválida. Por favor, seleccione una ubicación válida.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_locations_for_attendance(bot, msg))
        return

    selected_location = next((loc for loc in locations if str(loc['id']) == input_location_id and f"{loc['id']}: {loc['location']}" == user_input), None)

    if not selected_location:
        bot.send_message(cid, translate("Ubicación inválida. Por favor, seleccione una ubicación válida.", target_lang))
        bot.register_next_step_handler(message, lambda msg: list_locations_for_attendance(bot, msg))
        return

    # Store location in session data
    if cid not in user_session_data:
        user_session_data[cid] = {}
    user_session_data[cid]['location'] = {
        'id': selected_location['id'],
        'name': selected_location['location']
    }

    # Submit attendance data
    submit_attendance(bot, message, user_session_data[cid]['location'])

def submit_attendance(bot, message, location):
    """Submit the attendance data to the backend."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    # Automatically set the date to today's date
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    # Data to be sent
    data = {
        'coach_id': user_session_data[cid]['coach_id'],
        'user_id': user_session_data[cid]['user_id'],
        'location_id': location['id'],
        'date': date
    }
    response = requests.post(f"{BASE_URL}/attendances", json=data)

    if response.status_code == 201:
        offer_add_or_finish(bot, message, target_lang)
    else:
        bot.send_message(cid, translate("Error al registrar la asistencia. Por favor, inténtelo de nuevo.", target_lang))

def offer_add_or_finish(bot, message, target_lang):
    """Offer to add another record or finish the process."""
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton(translate("Agregar Otro", target_lang)))
    markup.add(types.KeyboardButton(translate("Terminar", target_lang)))

    bot.send_message(
        cid,
        translate("¡Asistencia registrada con éxito! ¿Desea agregar otro registro o terminar el proceso?", target_lang),
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, lambda msg: process_add_or_finish(bot, msg))

def process_add_or_finish(bot, message):
    """Handle the choice to add another record or finish."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    user_input = message.text.strip().lower()
    add_another_option = translate("Agregar Otro", target_lang).lower()
    finish_option = translate("Terminar", target_lang).lower()

    if user_input == add_another_option:
        bot.send_message(cid, translate("Por favor, seleccione un usuario (cliente):", target_lang))
        list_users_for_attendance(bot, message)
    elif user_input == finish_option:
        user_session_data.pop(cid, None)  # Clear session data
        bot.send_message(cid, translate("Proceso finalizado. Gracias.", target_lang))
    else:
        bot.send_message(cid, translate("Opción inválida. Por favor, seleccione una opción válida.", target_lang))
        offer_add_or_finish(bot, message)
