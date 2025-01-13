import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv
import re
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://web:5000")

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
    
def is_valid_time_list(input_text):
    """
    Validate if the input follows the format '9:00,10:00,11:00'.
    """
    pattern = r'^([0-9]{1,2}:[0-5][0-9])(,[0-9]{1,2}:[0-5][0-9])*$'
    return bool(re.match(pattern, input_text))

def create_cancel_markup(target_lang='es'):
    """Create a reply markup with a 'Cancel' button."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton(translate("Cancelar", target_lang))
    markup.row(item1)
    return markup

def cancel_process(bot, message):
    """Handle the cancellation of the process."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("/menu")
    markup.row(item1)
    bot.send_message(cid, translate("Proceso cancelado.", target_lang), reply_markup=markup)

def sanitize_schedule_text(text):
    """
    Sanitize special characters in schedule-related input.
    """
    return re.sub(r'[^a-zA-Z0-9\s:.-]', '', text)

def escape_schedule_markdown(text):
    """
    Escape special characters for Telegram MarkdownV2 for schedule messages.
    """
    # MarkdownV2 special characters that need escaping
    escape_chars = r'[_*\[\]()~`>#+\-=|{}.!]'
    return re.sub(f'({escape_chars})', r'\\\1', text)

def list_schedules(bot, message):
    """
    Fetch and display the list of all available schedules.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/schedules")

    if response.status_code == 200:
        schedules = response.json()

        if schedules:
            # Build a text representation of the schedules
            schedules_text = f"{translate('Horarios disponibles:', target_lang)}\n"
            for sch in schedules:
                schedules_text += f"🔹 *{translate('Ubicación:', target_lang)}* {sch['location_name']}\n*{translate('Días:', target_lang)}* {sch['days']}\n*{translate('Hora de inicio:', target_lang)}* {sch['time_init']}\n\n"

            # Send the list of schedules to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, schedules_text, parse_mode="MarkdownV2", reply_markup=markup)
        else:
            bot.send_message(cid, translate("No hay horarios disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los horarios.", target_lang))

def list_schedules_customer(bot, message):
    """
    Fetch and display the list of all available schedules.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/schedules")

    if response.status_code == 200:
        schedules = response.json()

        if schedules:
            # Build a text representation of the schedules
            schedules_text = f"{translate('Horarios disponibles:', target_lang)}\n\n"
            for sch in schedules:
                schedules_text += f"🔹 *{translate('Ubicación:', target_lang)}*\n\n{sch['location_name']}\n*{translate('Días:', target_lang)}* {sch['days']}\n*{translate('Hora de inicio:', target_lang)}*\n{sch['time_init']}\n\n\n"

            # Send the list of schedules to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, schedules_text, parse_mode="MarkdownV2", reply_markup=markup)
        else:
            bot.send_message(cid, translate("No hay horarios disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los horarios.", target_lang))        

def list_locations(bot, message):
    """
    List all available locations for the user to select.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/locations")  # Assuming the locations endpoint is /locations

    if response.status_code == 200:
        locations = response.json()

        if locations:
            locations_text = translate("Elija una ubicación:\n", target_lang)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for location in locations:
                markup.add(types.KeyboardButton(location['location']))  # Assuming location has 'name' attribute
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, locations_text, reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: handle_location_selection(bot, msg, locations))
        else:
            bot.send_message(cid, translate("No hay ubicaciones disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener las ubicaciones.", target_lang))

def handle_location_selection(bot, message, locations):
    """
    Handle location selection and proceed to days of the week.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    selected_location = message.text.strip()

    if selected_location.lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    # Find the location object based on the selected location name
    location = next((loc for loc in locations if loc['location'] == selected_location), None)

    if location:
        # Proceed to schedule days
        bot.send_message(cid, translate("Por favor, ingrese los días del horario:", target_lang))
        bot.register_next_step_handler(message, lambda msg: add_schedule_days_handler(bot, msg, location))
    else:
        bot.send_message(cid, translate("Error al obtener las ubicaciones.", target_lang))
        list_locations(bot, message)

def add_schedule_handler(bot, message):
    """
    Start the process of adding a new schedule, first asking for location.
    """
    list_locations(bot, message)  # Now it starts with selecting a location

def add_schedule_days_handler(bot, message, location):
    """
    Handle the days input for the new schedule after the location is selected.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    schedule_days = message.text.strip()

    if not schedule_days:
        bot.send_message(message.chat.id, translate("Los días del horario no pueden estar vacíos.", target_lang))
        add_schedule_days_handler(bot, message, location)
        return

    # Now ask for the start time (time_init)
    bot.send_message(message.chat.id, translate("Por favor, ingrese la hora de inicio del horario:", target_lang))
    bot.register_next_step_handler(message, lambda msg: submit_new_schedule(bot, msg, location, schedule_days))

def submit_new_schedule(bot, message, location, schedule_days):
    """
    Handle the time_init and proceed to time_end.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    time_init = message.text.strip()

    if not is_valid_time_list(time_init):  # Validate format  # Validate time format (e.g., 9, 10:30)
        bot.send_message(cid, translate("Formato de hora incorrecto. Por favor, ingrese la hora en el formato HH:MM.", target_lang))
        bot.register_next_step_handler(message, lambda msg: submit_new_schedule(bot, msg, location, schedule_days))
        return

    # Prepare the data to submit to the backend
    data = {
        "location_id": location['id'],
        "days": schedule_days, 
        "time_init": time_init
    }
    print(data)
    response = requests.post(f"{BASE_URL}/schedules", json=data)

    bot.send_message(cid, translate("Procesando...", target_lang))

    if response.status_code == 201:
        bot.send_message(message.chat.id, translate("Horario creado con éxito.", target_lang))
        list_schedules(bot, message)  # Optionally, show the updated list of schedules
    else:
        bot.send_message(message.chat.id, translate("Error al crear el horario.", target_lang))

def submit_new_schedule_end_time(bot, message, location, schedule_days, time_init):
    """
    Handle time_end input and create the schedule.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    # Prepare the data to submit to the backend
    data = {
        "location_id": location['id'],
        "days": schedule_days, 
        "time_init": time_init
    }
    print(data)
    response = requests.post(f"{BASE_URL}/schedules", json=data)

    bot.send_message(cid, translate("Procesando...", target_lang))

    if response.status_code == 201:
        bot.send_message(message.chat.id, translate("Horario creado con éxito.", target_lang))
        list_schedules(bot, message)  # Optionally, show the updated list of schedules
    else:
        bot.send_message(message.chat.id, translate("Error al crear el horario.", target_lang))

def list_schedules_for_selection(bot, message, action):
    """
    Fetch and display the list of available schedules for selection.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/schedules")

    if response.status_code == 200:
        schedules = response.json()

        if schedules:
            # Display schedules for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for sch in schedules:
                button = types.KeyboardButton(f"{sch['id']}: {sch['location_name']} {sch['days']} ({sch['time_init']})")
                markup.add(button)
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, translate("Seleccione un horario:", target_lang), reply_markup=markup)

            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_schedule_selection(bot, msg, schedules))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_schedule_selection(bot, msg, schedules))
        else:
            bot.send_message(cid, translate("No hay horarios disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los horarios.", target_lang))

def handle_edit_schedule_selection(bot, message, schedules):
    """
    Handle the selection of a schedule to edit.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        schedule_id = int(choice.split(":")[0].strip())
        selected_schedule = next((sch for sch in schedules if sch['id'] == schedule_id), None)

        if selected_schedule:
            start_edit_schedule(bot, message, selected_schedule)
        else:
            bot.send_message(cid, translate("Selección de horario inválida.", target_lang))
            list_schedules_for_selection(bot, message, "edit")
    except ValueError:
        bot.send_message(cid, translate("Selección de horario inválida.", target_lang))
        list_schedules_for_selection(bot, message, "edit")

def start_edit_schedule(bot, message, schedule):
    """
    Start editing the schedule by asking for new `days`.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(translate("Omitir", target_lang))

    bot.send_message(
        cid,
        f"{translate('Días actuales del horario:', target_lang)} {schedule['days']}\n{translate('Por favor, ingrese los nuevos días del horario:', target_lang)}",
        reply_markup=markup,
    )
    bot.register_next_step_handler(
        message, lambda msg: handle_days_edit(bot, msg, schedule)
    )

def handle_days_edit(bot, message, schedule):
    """
    Handle editing the `days` field.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_days = message.text.strip()

    if new_days.lower() == translate("Omitir", target_lang).lower():
        new_days = schedule['days']

    schedule['days'] = new_days

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(translate("Omitir", target_lang))

    bot.send_message(
        cid,
        f"{translate('Hora de inicio actual del horario:', target_lang)} {schedule['time_init']}\n{translate('Por favor, ingrese la nueva hora de inicio del horario:', target_lang)}",
        reply_markup=markup,
    )
    bot.register_next_step_handler(
        message, lambda msg: handle_time_edit(bot, msg, schedule)
    )

def handle_time_edit(bot, message, schedule):
    """
    Handle editing the `time_init` field.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_time = message.text.strip()

    if new_time.lower() == translate("Omitir", target_lang).lower():
        new_time = schedule['time_init']

    schedule['time_init'] = new_time

    # Submit the updated schedule to the backend
    response = requests.put(f"{BASE_URL}/schedules/{schedule['id']}", json=schedule)
    bot.send_message(cid, translate("Procesando...", target_lang))

    if response.status_code == 200:
        bot.send_message(cid, translate("Horario actualizado con éxito.", target_lang))
        list_schedules(bot, message)  # Optionally, show the updated list of schedules
    else:
        bot.send_message(cid, translate("Error al ✏️ Actualizar el horario.", target_lang))

def handle_delete_schedule_selection(bot, message, schedules):
    """
    Handle the selection of a schedule to delete.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        schedule_id = int(choice.split(":")[0].strip())
        selected_schedule = next((sch for sch in schedules if sch['id'] == schedule_id), None)

        if selected_schedule:
            confirm_delete_schedule(bot, message, selected_schedule)
        else:
            bot.send_message(cid, translate("Selección de horario inválida.", target_lang))
            list_schedules_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, translate("Selección de horario inválida.", target_lang))
        list_schedules_for_selection(bot, message, "delete")

def confirm_delete_schedule(bot, message, schedule):
    """
    Confirm the deletion of the selected schedule.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton(translate("Sí", target_lang)), types.KeyboardButton(translate("Cancelar", target_lang)))

    bot.send_message(cid, f"{translate('¿Está seguro de que desea eliminar el horario', target_lang)} '{schedule['id']}'?", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: execute_delete_schedule(bot, msg, schedule['id']))

def execute_delete_schedule(bot, message, schedule_id):
    """
    Execute the deletion of the selected schedule.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text == translate("Sí", target_lang):
        response = requests.delete(f"{BASE_URL}/schedules/{schedule_id}")
        bot.send_message(cid, translate("Procesando...", target_lang))
        if response.status_code == 200:
            bot.send_message(cid, translate("Horario eliminado con éxito.", target_lang))
        else:
            bot.send_message(cid, translate("Error al eliminar el horario.", target_lang))

    list_schedules(bot, message)

def edit_schedule_handler(bot, message):
    """
    Start the process of editing a schedule.
    """
    list_schedules_for_selection(bot, message, "edit")

def delete_schedule_handler(bot, message):
    """
    Start the process of deleting a schedule.
    """
    list_schedules_for_selection(bot, message, "delete")