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

def add_coach_handler(bot, message):
    """Start the process of creating a new coach."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = create_cancel_markup(target_lang)
    bot.send_message(message.chat.id, translate("Por favor, ingrese la cédula del entrenador:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, handle_cedula_input)

def handle_cedula_input(bot, message):
    """Handle the input of the coach's cedula and ask for the names."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    cedula = message.text.strip()
    bot.send_message(message.chat.id, translate("Por favor, ingrese los nombres del entrenador:", target_lang))
    bot.register_next_step_handler(message, lambda msg: handle_names_input(bot, msg, cedula))

def handle_names_input(bot, message, cedula):
    """Handle the input of the coach's names and ask for the location ID."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    names = message.text.strip()
    bot.send_message(message.chat.id, translate("Por favor, ingrese el ID de la ubicación para el entrenador:", target_lang))
    bot.register_next_step_handler(message, lambda msg: submit_new_coach(bot, msg, cedula, names))

def submit_new_coach(bot, message, cedula, names):
    """Submit the new coach to the backend."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    location_id = message.text.strip()

    if not location_id.isdigit():
        bot.send_message(message.chat.id, translate("ID de ubicación inválido. Por favor, ingrese un número válido.", target_lang))
        bot.register_next_step_handler(message, lambda msg: submit_new_coach(bot, msg, cedula, names))
        return

    data = {"cedula": cedula, "names": names, "location_id": int(location_id)}
    response = requests.post(f"{BASE_URL}/coaches", json=data)
    bot.send_message(cid, translate("Procesando...", target_lang))
    if response.status_code == 201:
        bot.send_message(message.chat.id, translate("¡Entrenador creado con éxito!", target_lang))
        list_coaches(bot, message)
    else:
        bot.send_message(message.chat.id, translate("Error al crear el entrenador. Por favor, inténtelo de nuevo.", target_lang))

def list_coaches(bot, message):
    """Fetch and display the list of all available coaches."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/coaches")

    if response.status_code == 200:
        coaches = response.json()

        if coaches:
            # Build a text representation of the coaches
            coaches_text = translate("Entrenadores disponibles:", target_lang) + "\n"
            for coach in coaches:
                coaches_text += f"🔹 ID: {coach['id']} - Cédula: {coach['cedula']} - Nombres: {coach['names']} - Ubicación: {coach['location_name']}\n"

            # Send the list of coaches to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, coaches_text, parse_mode="MarkdownV2", reply_markup=markup)
        else:
            bot.send_message(cid, translate("No hay entrenadores disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los entrenadores.", target_lang))

def list_coaches_for_selection(bot, message, action):
    """Fetch and display the list of available coaches for selection."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/coaches")

    if response.status_code == 200:
        coaches = response.json()

        if coaches:
            # Display coaches for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for coach in coaches:
                button = types.KeyboardButton(f"{coach['id']}: {coach['names']} ({coach['cedula']})")
                markup.add(button)
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, translate("Por favor, seleccione un entrenador:", target_lang), reply_markup=markup)

            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_coach_selection(bot, msg, coaches))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_coach_selection(bot, msg, coaches))
        else:
            bot.send_message(cid, translate("No hay entrenadores disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los entrenadores.", target_lang))

def handle_edit_coach_selection(bot, message, coaches):
    """Handle the selection of a coach to edit."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        coach_id = int(choice.split(":")[0].strip())
        selected_coach = next((coach for coach in coaches if coach['id'] == coach_id), None)

        if selected_coach:
            bot.send_message(
                cid,
                f"{translate('Nombres actuales:', target_lang)} {selected_coach['names']}. {translate('Por favor, proporcione nuevos nombres o elija Omitir:', target_lang)}",
                reply_markup=create_cancel_markup(target_lang)
            )
            bot.register_next_step_handler(message, lambda msg: handle_names_edit(bot, msg, selected_coach))
        else:
            bot.send_message(cid, translate("Selección inválida. Por favor, inténtelo de nuevo.", target_lang))
            list_coaches_for_selection(bot, message, "edit")
    except ValueError:
        bot.send_message(cid, translate("Entrada inválida. Por favor, inténtelo de nuevo.", target_lang))
        list_coaches_for_selection(bot, message, "edit")

def handle_names_edit(bot, message, coach):
    """Handle editing the `names` field."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_names = message.text.strip()

    if new_names.lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    if new_names.lower() == translate("Omitir", target_lang).lower():
        new_names = coach['names']

    coach['names'] = new_names

    bot.send_message(
        cid,
        f"{translate('ID de ubicación actual:', target_lang)} {coach['location_id']}. {translate('Por favor, proporcione un nuevo ID de ubicación o elija Omitir:', target_lang)}",
        reply_markup=create_cancel_markup(target_lang)
    )
    bot.register_next_step_handler(message, lambda msg: handle_location_edit(bot, msg, coach))

def handle_location_edit(bot, message, coach):
    """Handle editing the `location_id` field."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_location_id = message.text.strip()

    if new_location_id.lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    if new_location_id.lower() == translate("Omitir", target_lang).lower():
        new_location_id = coach['location_id']
    else:
        if not new_location_id.isdigit():
            bot.send_message(message.chat.id, translate("ID de ubicación inválido. Por favor, ingrese un número válido.", target_lang))
            bot.register_next_step_handler(message, lambda msg: handle_location_edit(bot, msg, coach))
            return

    coach['location_id'] = int(new_location_id)

    # Submit the updated coach to the backend
    response = requests.put(f"{BASE_URL}/coaches/{coach['id']}", json=coach)
    bot.send_message(cid, translate("Procesando...", target_lang))

    if response.status_code == 200:
        bot.send_message(cid, translate("¡Entrenador actualizado con éxito!", target_lang))
    else:
        bot.send_message(cid, translate("Error al ✏️ Actualizar el entrenador. Por favor, inténtelo de nuevo.", target_lang))

def handle_delete_coach_selection(bot, message, coaches):
    """Handle the selection of a coach to delete."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        coach_id = int(choice.split(":")[0].strip())
        selected_coach = next((coach for coach in coaches if coach['id'] == coach_id), None)

        if selected_coach:
            confirm_delete_coach(bot, message, selected_coach)
        else:
            bot.send_message(cid, translate("Selección inválida. Por favor, inténtelo de nuevo.", target_lang))
            list_coaches_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, translate("Entrada inválida. Por favor, inténtelo de nuevo.", target_lang))
        list_coaches_for_selection(bot, message, "delete")

def confirm_delete_coach(bot, message, coach):
    """Confirm the deletion of the selected coach."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton(translate("Sí", target_lang)), types.KeyboardButton(translate("Cancelar", target_lang)))

    bot.send_message(cid, f"{translate('¿Está seguro de que desea eliminar al entrenador', target_lang)} '{coach['names']}'?", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: execute_delete_coach(bot, msg, coach['id']))

def execute_delete_coach(bot, message, coach_id):
    """Execute the deletion of the selected coach."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Sí", target_lang).lower():
        response = requests.delete(f"{BASE_URL}/coaches/{coach_id}")
        bot.send_message(cid, translate("Procesando...", target_lang))
        if response.status_code == 200:
            bot.send_message(cid, translate("¡Entrenador eliminado con éxito!", target_lang))
        else:
            bot.send_message(cid, translate("Error al eliminar el entrenador. Por favor, inténtelo de nuevo.", target_lang))
    else:
        bot.send_message(cid, translate("Eliminación cancelada.", target_lang))

    list_coaches(bot, message)

def edit_coach_handler(message):
    list_coaches_for_selection(bot, message, "edit")

def delete_coach_handler(message):
    list_coaches_for_selection(bot, message, "delete")