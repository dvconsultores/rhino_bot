import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import re
from datetime import datetime
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

# Helper function to validate date format
def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Helper function to validate email format
def validate_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

def get_user(bot, message):
    """Retrieve user information by ID."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    msg = bot.send_message(cid, translate("Por favor, ingrese el ID del usuario:", target_lang))
    bot.register_next_step_handler(msg, fetch_user_info, bot=bot)

def fetch_user_info(message, bot):
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    user_id = message.text
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            user_info = "\n".join([f"{key}: {value}" for key, value in user_data.items()])
            bot.send_message(message.chat.id, translate(f"Información del usuario:\n{user_info}", target_lang))
        else:
            bot.send_message(message.chat.id, translate("Usuario no encontrado.", target_lang))
    except Exception as e:
        bot.send_message(message.chat.id, translate(f"Ocurrió un error: {str(e)}", target_lang))

# Dictionary to store user data temporarily
user_data = {}

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
    user_data.pop(cid, None)  # Clear user data after cancellation

def create_user(bot, message):
    """Iniciar la creación de usuario solicitando el nombre del usuario."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    user_data[cid] = {}
    markup = create_cancel_markup(target_lang)
    msg = bot.send_message(cid, translate("Por favor, ingrese su nombre:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(msg, process_name, bot=bot)

def process_name(message, bot):
    """Procesar el nombre del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    """Procesar el nombre del usuario y preguntar por el apellido."""
    if not message.text.strip():
        markup = create_cancel_markup(target_lang)
        msg = bot.send_message(message.chat.id, translate("El nombre es obligatorio. Por favor, ingrese su nombre:", target_lang), reply_markup=markup)
        bot.register_next_step_handler(msg, process_name, bot=bot)
        return
    
    user_data[message.chat.id]["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, translate("Por favor, ingrese su apellido:", target_lang))
    bot.register_next_step_handler(msg, process_lastname, bot=bot)

def process_lastname(message, bot):
    """Procesar el apellido del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    """Procesar el apellido del usuario y preguntar por la cédula."""
    if not message.text.strip():
        markup = create_cancel_markup(target_lang)
        msg = bot.send_message(message.chat.id, translate("El apellido es obligatorio. Por favor, ingrese su apellido:", target_lang), reply_markup=markup)
        bot.register_next_step_handler(msg, process_lastname, bot=bot)
        return
    
    user_data[message.chat.id]["lastname"] = message.text.strip()
    msg = bot.send_message(message.chat.id, translate("Por favor, ingrese su cédula:", target_lang))
    bot.register_next_step_handler(msg, process_cedula, bot=bot)

def process_cedula(message, bot):
    """Procesar la cédula del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    """Procesar la cédula y preguntar por el correo electrónico."""
    cedula_input = message.text.strip()

    # Check if cedula is empty or not an integer
    if not cedula_input or not cedula_input.isdigit():
        markup = create_cancel_markup(target_lang)
        msg = bot.send_message(message.chat.id, translate("Formato de cédula incorrecto. Por favor, ingrese solo números.", target_lang), reply_markup=markup)
        bot.register_next_step_handler(msg, process_cedula, bot=bot)
        return

    # Store the valid cedula as an integer
    user_data[message.chat.id]["cedula"] = int(cedula_input)
    msg = bot.send_message(message.chat.id, translate("Por favor, ingrese su correo electrónico:", target_lang))
    bot.register_next_step_handler(msg, process_email, bot=bot)

def process_email(message, bot):
    """Procesar el correo electrónico del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    """Procesar el correo electrónico y validar su formato, luego preguntar por la fecha de nacimiento."""
    email_input = message.text.lower()
    if not validate_email(email_input):
        markup = create_cancel_markup(target_lang)
        msg = bot.send_message(message.chat.id, translate("Correo electrónico inválido. Por favor, ingrese un correo electrónico válido.", target_lang), reply_markup=markup)
        bot.register_next_step_handler(msg, process_email, bot=bot)
        return
    
    user_data[message.chat.id]["email"] = email_input
    msg = bot.send_message(message.chat.id, translate("Por favor, ingrese su fecha de nacimiento (DD/MM/AAAA):", target_lang))
    bot.register_next_step_handler(msg, process_date_of_birth, bot=bot)

def process_date_of_birth(message, bot):
    """Procesar la fecha de nacimiento del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    """Procesar la fecha de nacimiento, validarla y luego preguntar por el número de teléfono."""
    date_input = message.text.strip()

    # Validate and reformat date
    try:
        # Convert from dd/mm/yyyy to yyyy-mm-dd format
        formatted_date = datetime.strptime(date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        # If the date is invalid, ask again
        markup = create_cancel_markup(target_lang)
        msg = bot.send_message(message.chat.id, translate("Formato de fecha incorrecto. Por favor, ingrese la fecha en el formato DD/MM/AAAA.", target_lang), reply_markup=markup)
        bot.register_next_step_handler(msg, process_date_of_birth, bot=bot)
        return
    
    # Save the correctly formatted date to user_data
    user_data[message.chat.id]["date_of_birth"] = formatted_date
    markup = create_cancel_markup(target_lang)
    msg = bot.send_message(message.chat.id, translate("Por favor, ingrese su número de teléfono:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone, bot=bot)

def process_phone(message, bot):
    """Procesar el número de teléfono del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return
        
    """Procesar el número de teléfono y luego preguntar por el handle de Instagram."""
    phone_input = message.text.strip()

    # Check if the phone number is empty or not an integer
    if not phone_input or not phone_input.isdigit():
        markup = create_cancel_markup(target_lang)
        msg = bot.send_message(message.chat.id, translate("Número de teléfono inválido. Por favor, ingrese solo números.", target_lang), reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone, bot=bot)
        return

    # Store the valid phone number as an integer
    user_data[message.chat.id]["phone"] = int(phone_input)

    # Create markup with a 'Skip' button for the next step
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = types.KeyboardButton(translate('Omitir', target_lang))
    markup.row(item1)
    markup.row(types.KeyboardButton(translate("Cancelar", target_lang)))
    msg = bot.send_message(message.chat.id, translate("Por favor, ingrese su handle de Instagram (o 'Omitir'):", target_lang), parse_mode='Markdown', reply_markup=markup)         
    bot.register_next_step_handler(msg, process_instagram, bot=bot)

def process_instagram(message, bot):
    """Procesar el handle de Instagram del usuario y preguntar por la cancelación."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    """Procesar el handle de Instagram y luego confirmar los detalles del usuario antes de la creación."""
    user_data[message.chat.id]["instagram"] = message.text if message.text.lower() != translate("Omitir", target_lang).lower() else None

    # Set default values for type, status, and telegram_id
    user_data[message.chat.id]["type"] = "cliente"
    user_data[message.chat.id]["estatus"] = "activo"
    user_data[message.chat.id]["telegram_id"] = message.chat.id

    # Titles dictionary to map data keys to personalized titles
    titles = {
        "name": translate("Nombre", target_lang),
        "lastname": translate("Apellido", target_lang),
        "cedula": translate("Cédula", target_lang),
        "email": translate("Correo electrónico", target_lang),
        "date_of_birth": translate("Fecha de nacimiento", target_lang),
        "phone": translate("Número de teléfono", target_lang),
        "instagram": translate("Instagram", target_lang),
        "type": translate("Tipo", target_lang),
        "estatus": translate("Estatus", target_lang),
        "telegram_id": translate("ID de Telegram", target_lang)
    }

    # Display collected data for confirmation with personalized titles, limited to 7 fields
    user_info = "\n".join([f"{titles.get(key, key)}: {value}" 
                        for key, value in list(user_data[message.chat.id].items())[:7] if value])
    confirmation_text = translate("Por favor, confirme sus datos:", target_lang) + "\n" + user_info

    # Show confirmation options with Yes, No, and Cancel buttons
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = types.KeyboardButton(translate("Sí", target_lang))
    item2 = types.KeyboardButton(translate("No", target_lang))
    item3 = types.KeyboardButton(translate("Cancelar", target_lang))
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    msg = bot.send_message(message.chat.id, confirmation_text, reply_markup=markup)
    bot.register_next_step_handler(msg, lambda msg: confirmation_handler(msg, bot))

def confirmation_handler(message, bot):
    """Handle the user's confirmation choice."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    # Normalize input to match button text (case insensitive)
    user_input = message.text.strip().lower()
    yes_option = translate("Sí", target_lang).lower()
    no_option = translate("No", target_lang).lower()
    cancel_option = translate("Cancelar", target_lang).lower()

    # Remove the reply keyboard
    markup_remove = types.ReplyKeyboardRemove()

    if user_input == yes_option:
        # Proceed with user creation
        bot.send_message(cid, translate("Procesando...", target_lang), reply_markup=markup_remove)
        response = requests.post(f"{BASE_URL}/users", json=user_data[cid])
        if response.status_code != 201:
            bot.send_message(cid, f"{translate('Error al crear el usuario.', target_lang)} Error: {response.status_code}", reply_markup=markup_remove)
            return
        bot.send_message(cid, translate("Usuario creado con éxito.", target_lang), reply_markup=markup_remove)
    elif user_input == no_option:
        # Restart user creation process
        bot.send_message(cid, translate("Reiniciando el proceso de creación de usuario.", target_lang), reply_markup=markup_remove)
        create_user(bot, message)
    elif user_input == cancel_option:
        # Cancel user creation
        cancel_process(bot, message)
    else:
        # Handle invalid input
        bot.send_message(cid, translate("Entrada no válida. Por favor, seleccione una opción válida.", target_lang), reply_markup=markup_remove)
        process_instagram(message, bot)  # Restart the confirmation step


def process_payment(bot, message):
    """Procesar el pago."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    payment_payload = payment_data.get(cid)

    response = requests.post(f"{BASE_URL}/payments", json=payment_payload)
    
    if response.status_code == 201:
        bot.send_message(cid, translate("Pago realizado con éxito.", target_lang), reply_markup=markup_remove)
    else:
        bot.send_message(cid, f"{translate('Error en el pago.', target_lang)} Error: {response.status_code}", reply_markup=markup_remove)

    # Clear stored data
    payment_data.pop(cid, None)

