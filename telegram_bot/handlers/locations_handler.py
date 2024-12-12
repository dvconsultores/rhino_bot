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

def sanitize_text(text):
    """
    Remove all special characters that might interfere with Telegram MarkdownV2.
    """
    # Allow only alphanumeric characters and spaces
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def escape_markdown(text):
    """
    Escape special characters for Telegram MarkdownV2.
    """
    # MarkdownV2 special characters that need escaping
    escape_chars = r'[_*\[\]()~`>#+\-=|{}.!]'
    return re.sub(f'({escape_chars})', r'\\\1', text)

# List all locations
def list_locations(bot, message):
    """
    Fetch and display the list of all available locations.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/locations")

    if response.status_code == 200:
        locations = response.json()

        if locations:
            # Build a text representation of the locations
            locations_text = f"{escape_markdown(translate('Ubicaciones disponibles:', target_lang))}\n"
            for loc in locations:
                locations_text += (
                    f"🔹 *{escape_markdown(translate('ID:', target_lang))}*: {loc['id']} "
                    f"*{escape_markdown(translate('Ubicación:', target_lang))}*: {escape_markdown(loc['location'])} "
                    f"*{escape_markdown(translate('Dirección:', target_lang))}*: {escape_markdown(loc['address'])}\n"
                )

            # Send the list of locations to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, locations_text, parse_mode="MarkdownV2", reply_markup=markup)
        else:
            bot.send_message(cid, escape_markdown(translate("No hay ubicaciones disponibles.", target_lang)), parse_mode="MarkdownV2")
    else:
        bot.send_message(cid, escape_markdown(translate("Error al obtener las ubicaciones.", target_lang)), parse_mode="MarkdownV2")

# Add a new location
def add_location_handler(bot, message):
    """
    Start the process of adding a new location.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = create_cancel_markup(target_lang)
    bot.send_message(message.chat.id, translate('Por favor, ingrese el nombre de la ubicación:', target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: add_location_name_handler(bot, msg))

def add_location_name_handler(bot, message):
    """
    Handle the name input for the new location and ask for the address.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    location_name = message.text.strip()

    if not location_name:
        bot.send_message(message.chat.id, translate("El nombre de la ubicación no puede estar vacío.", target_lang))
        add_location_handler(bot, message)
        return

    bot.send_message(message.chat.id, translate("Por favor, ingrese la dirección de la ubicación:", target_lang))
    bot.register_next_step_handler(message, lambda msg: submit_new_location(bot, msg, location_name))

def submit_new_location(bot, message, location_name):
    """
    Submit the new location to the backend.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    location_address = message.text.strip()

    if not location_address:
        bot.send_message(message.chat.id, translate("La dirección de la ubicación no puede estar vacía.", target_lang))
        bot.register_next_step_handler(message, lambda msg: submit_new_location(bot, msg, location_name))
        return

    data = {"location": location_name, "address": location_address}
    response = requests.post(f"{BASE_URL}/locations", json=data)
    bot.send_message(cid, translate("Procesando...", target_lang))
    if response.status_code == 201:
        bot.send_message(message.chat.id, translate("Ubicación creada con éxito.", target_lang))
        list_locations(bot, message)
    else:
        bot.send_message(message.chat.id, translate("Error al crear la ubicación.", target_lang))

# List all locations for selection
def list_locations_for_selection(bot, message, action):
    """
    Fetch and display the list of available locations for selection.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/locations")

    if response.status_code == 200:
        locations = response.json()

        if locations:
            # Display locations for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for loc in locations:
                button = types.KeyboardButton(f"{loc['id']}: {loc['location']} ({loc['address']})")
                markup.add(button)
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, translate("Seleccione una ubicación:", target_lang), reply_markup=markup)

            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_location_selection(bot, msg, locations))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_location_selection(bot, msg, locations))
        else:
            bot.send_message(cid, translate("No hay ubicaciones disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener las ubicaciones.", target_lang))

# Handle selecting a location to edit
def handle_edit_location_selection(bot, message, locations):
    """
    Handle the selection of a location to edit.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        location_id = int(choice.split(":")[0].strip())
        selected_location = next((loc for loc in locations if loc['id'] == location_id), None)

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton(translate("Omitir", target_lang)))

        if selected_location:
            bot.send_message(
                cid,
                f"{translate('Ubicación actual:', target_lang)} '{selected_location['location']}'. {translate('Por favor, ingrese la nueva dirección de la ubicación (o Omitir):', target_lang)}",
                reply_markup=markup
            )
            bot.register_next_step_handler(message, lambda msg: handle_edit_location_name(bot, msg, selected_location))
        else:
            bot.send_message(cid, translate("Selección de ubicación inválida.", target_lang))
            list_locations_for_selection(bot, message, "edit")
    except ValueError:
        bot.send_message(cid, translate('Selección de ubicación inválida.', target_lang))
        list_locations_for_selection(bot, message, "edit")

# Handle editing the location name
def handle_edit_location_name(bot, message, location):
    """
    Handle editing the location name and proceed to address editing.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_location_name = message.text.strip()

    if new_location_name.lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(translate("Omitir", target_lang))

    if new_location_name.lower() == translate("Omitir", target_lang).lower():
        new_location_name = location['location']

    bot.send_message(
        cid,
        f"{translate('Dirección actual:', target_lang)} '{location['address']}'. {translate('Por favor, ingrese la nueva dirección de la ubicación (o Omitir):', target_lang)}",
        reply_markup=markup
    )
    bot.register_next_step_handler(
        message, lambda msg: submit_edited_location(bot, msg, location['id'], new_location_name)
    )

# Submit the updated location
def submit_edited_location(bot, message, location_id, new_location_name):
    """
    Submit the edited location to the backend.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_address = message.text.strip()

    if new_address.lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    if new_address.lower() == translate("Omitir", target_lang).lower():
        # Keep the address unchanged
        response = requests.get(f"{BASE_URL}/locations/{location_id}")
        if response.status_code == 200:
            location = response.json()
            new_address = location['address']
        else:
            bot.send_message(cid, translate("Error al obtener las ubicaciones.", target_lang))
            return

    data = {"location": new_location_name, "address": new_address}
    response = requests.put(f"{BASE_URL}/locations/{location_id}", json=data)
    bot.send_message(cid, translate("Procesando...", target_lang))

    if response.status_code == 200:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton("/menu"))
        bot.send_message(cid, translate("Ubicación actualizada con éxito.", target_lang), reply_markup=markup)
        list_locations(bot, message)
    else:
        bot.send_message(cid, translate("Error al ✏️ Actualizar la ubicación.", target_lang))

# Delete location handler
def handle_delete_location_selection(bot, message, locations):
    """
    Handle the selection of a location to delete.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        location_id = int(choice.split(":")[0].strip())
        selected_location = next((loc for loc in locations if loc['id'] == location_id), None)

        if selected_location:
            confirm_delete_location(bot, message, selected_location)
        else:
            bot.send_message(cid, translate("Selección de ubicación inválida.", target_lang))
            list_locations_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, translate("Selección de ubicación inválida.", target_lang))
        list_locations_for_selection(bot, message, "delete")

# Confirm delete location
def confirm_delete_location(bot, message, location):
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton(translate("Sí", target_lang)), types.KeyboardButton(translate("Cancelar", target_lang)))

    bot.send_message(cid, f"{translate('¿Está seguro de que desea eliminar la ubicación', target_lang)} '{location['location']}'?", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: execute_delete_location(bot, msg, location['id']))

def execute_delete_location(bot, message, location_id):
    """
    Execute the deletion of the selected location.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text == translate("Sí", target_lang):
        response = requests.delete(f"{BASE_URL}/locations/{location_id}")
        bot.send_message(cid, translate("Procesando...", target_lang))
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton("/menu"))
        if response.status_code == 200:
            bot.send_message(cid, translate("Ubicación eliminada con éxito.", target_lang), reply_markup=markup)
        else:
            bot.send_message(cid, translate("Error al eliminar la ubicación.", target_lang), reply_markup=markup)
    else:
        bot.send_message(cid, translate("Proceso cancelado.", target_lang))

    list_locations(bot, message)

def handle_edit_location(bot, message):
    list_locations_for_selection(bot, message, "edit")

def handle_delete_location(bot, message):
    list_locations_for_selection(bot, message, "delete")
