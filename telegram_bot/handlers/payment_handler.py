import os
import requests
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import mimetypes

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Load environment variables
load_dotenv()

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://web:5000")
UPLOAD_DIR = "uploads"  # Directory for uploaded payment proofs

# Dictionary to temporarily store payment data
payment_data = {}

# Define the is_float function
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

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
    payment_data.pop(cid, None)  # Clear payment data after cancellation

# Step 1: Fetch payment methods and display them as buttons
def start_payment(bot, message):
    """Start the payment process after validating user existence."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    # Validate if the user exists
    user_validation_response = requests.get(f"{BASE_URL}/users/telegram/{cid}")
    if user_validation_response.status_code == 404:
        # User does not exist
        bot.send_message(
            cid,
            translate("Para ingresar pago debe registrarse en la plataforma.", target_lang),
        )
        return
    elif user_validation_response.status_code != 200:
        # Handle unexpected errors from the server
        bot.send_message(
            cid,
            translate("Error al verificar el usuario. Por favor, inténtelo de nuevo más tarde.", target_lang),
        )
        return

    # Fetch payment methods from the API
    response = requests.get(f"{BASE_URL}/payment_methods")
    if response.status_code != 200:
        bot.send_message(cid, translate("Error al obtener los métodos de pago.", target_lang))
        return

    # Display payment methods as buttons
    payment_methods = response.json()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for method in payment_methods:
        method_name = method.get("method")  # Ensure the correct field name
        method_id = method.get("id")
        if method_name and method_id:
            button = types.KeyboardButton(method_name)  # Only display the method name to the user
            markup.add(button)
    item1 = types.KeyboardButton(translate("Cancelar", target_lang))
    markup.row(item1)

    bot.send_message(cid, translate("Seleccione un método de pago:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: handle_payment_method_selection(bot, msg, payment_methods))


# Step 1b: Handle selected payment method from user’s message text
def handle_payment_method_selection(bot, message, payment_methods):
    """Process the user's selected payment method and ask for the payment amount."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    selected_method_name = message.text
    
    # Find the selected method ID and name based on the user's choice
    selected_method = next((method for method in payment_methods if method["method"] == selected_method_name), None)
    
    if selected_method:
        if cid not in payment_data:
            payment_data[cid] = {}
        payment_data[cid]["payment_method_id"] = selected_method["id"]
        payment_data[cid]["payment_method_name"] = selected_method_name  # Store the method name
        markup = create_cancel_markup(target_lang)
        bot.send_message(cid, translate("Por favor, ingrese el monto del pago:", target_lang), reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: handle_payment_amount(bot, msg))
    else:
        bot.send_message(cid, translate("Método de pago inválido.", target_lang))
        bot.register_next_step_handler(message, lambda msg: handle_payment_method_selection(bot, msg, payment_methods))

def handle_payment_amount(bot, message):
    """Process the payment amount and confirm the payment."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    amount = message.text.strip()
    if not is_float(amount):
        bot.send_message(cid, translate("Monto de pago inválido.", target_lang))
        bot.register_next_step_handler(message, lambda msg: handle_payment_amount(bot, msg))
        return

    payment_data[cid]["amount"] = float(amount)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(translate("Omitir", target_lang))
    bot.send_message(cid, translate("Por favor, ingrese la referencia del pago (o 'Omitir'):", target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: process_payment_reference(bot, msg))

# Step 3: Process payment reference
def process_payment_reference(bot, message):
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    payment_data[cid]["reference"] = message.text if message.text.lower() != translate("Omitir", target_lang).lower() else None
    
    # Ask for payment proof (image or PDF)
    markup = create_cancel_markup(target_lang)
    bot.send_message(cid, translate("Por favor, suba una imagen o PDF del comprobante de pago:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: process_payment_proof(bot, msg))

# Step 4: Process payment proof upload
def process_payment_proof(bot, message):
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    # Check if the message contains a document
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file_mime_type, _ = mimetypes.guess_type(file_info.file_path)

        # Check if the file is an image
        if file_mime_type and file_mime_type.startswith('image/'):
            # Process the image file
            file = bot.download_file(file_info.file_path)
            file_path = f"payment_proofs/{message.document.file_name}"
            with open(file_path, 'wb') as f:
                f.write(file)
            bot.send_message(cid, translate("Imagen recibida y procesada.", target_lang))
        else:
            bot.send_message(cid, translate("Por favor, envía solo archivos de imagen.", target_lang))
    else:
        bot.send_message(cid, translate("No se encontró ningún archivo adjunto.", target_lang))

    # Handle photo or document upload
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'document' and message.document.mime_type in ["application/pdf"]:
        file_id = message.document.file_id
    else:
        bot.send_message(cid, translate("Formato de archivo inválido. Por favor, suba una imagen o PDF.", target_lang))
        bot.register_next_step_handler(message, lambda msg: process_payment_proof(bot, msg))
        return

    # Download and save the file
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"{cid}_{datetime.now().strftime('%Y%m%d')}.jpg" if message.content_type == 'photo' else f"{cid}_{datetime.now().strftime('%Y%m%d')}.pdf"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Store file path in payment data
    payment_data[cid]["proof"] = file_path

    # Display payment summary for confirmation
    show_confirmation(cid, bot)

# Step 5: Show confirmation with collected data
def show_confirmation(cid, bot):
    """Display payment confirmation with collected data."""
    target_lang = get_language_by_telegram_id(cid)
    data = payment_data[cid]
    confirmation_text = (
        translate("Por favor, confirme la información del pago:", target_lang) + "\n\n" +
        translate("Método de pago:", target_lang) + f" {data['payment_method_name']}\n" +  # Display name instead of ID
        translate("Monto:", target_lang) + f" {data['amount']}\n" +
        translate("Referencia:", target_lang) + f" {data['reference'] or 'None'}\n"
    )

    # Show confirmation options with Yes, No, and Cancel buttons
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = types.KeyboardButton(translate("Sí", target_lang))
    item2 = types.KeyboardButton(translate("No", target_lang))
    item3 = types.KeyboardButton(translate("Cancelar", target_lang))
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)

    # Send message with confirmation options
    msg = bot.send_message(cid, confirmation_text, reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda msg: confirmation_handler(bot, msg))


# Step 6: Handle confirmation response
def confirmation_handler(bot, message):
    """Handle the user's confirmation response."""
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)

    # Normalize input to handle both text and button clicks
    user_input = message.text.strip().lower()
    yes_option = translate("Sí", target_lang).lower()
    no_option = translate("No", target_lang).lower()
    cancel_option = translate("Cancelar", target_lang).lower()

    if user_input not in [yes_option, no_option, cancel_option]:
        bot.send_message(cid, translate("Opción inválida. Por favor, seleccione 'Sí', 'No' o 'Cancelar'.", target_lang))
        bot.register_next_step_handler(message, lambda msg: confirmation_handler(bot, msg))
        return

    if user_input == yes_option:
        # Proceed with payment submission
        bot.send_message(cid, translate("Procesando...", target_lang))
        submit_payment(cid)
    elif user_input == no_option:
        # Restart payment process
        bot.send_message(cid, translate("Reiniciando el proceso de pago.", target_lang))
        start_payment(bot, message)
    elif user_input == cancel_option:
        # Cancel payment process
        bot.send_message(cid, translate("Proceso de pago cancelado.", target_lang))
        payment_data.pop(cid, None)  # Clear stored payment data


# Submit payment to the API
def submit_payment(cid):
    target_lang = get_language_by_telegram_id(cid)
    # Step 1: Fetch user ID from the backend using the Telegram user ID (cid)
    user_response = requests.get(f"{BASE_URL}/users/telegram/{cid}")
    
    # Handle cases where the user is not found or there is an error
    if user_response.status_code != 200:
        bot.send_message(cid, translate("Usuario no encontrado.", target_lang))
        return

    # Extract the user ID from the response
    user_data = user_response.json()
    user_id = user_data.get('id')
    
    if not user_id:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton("/menu")
        markup.row(item1)
        bot.send_message(cid, translate("Usuario no encontrado.", target_lang), reply_markup=markup)
        return
    
    # Step 2: Prepare payment data with the retrieved user ID
    data = payment_data[cid]
    payment_payload = {
        'user_id': user_id,  # Use the fetched user_id here
        'date': datetime.now().strftime('%Y-%m-%d'),
        'amount': data['amount'],
        'reference': data['reference'],
        'payment_method_id': data['payment_method_id'],
        'year': datetime.now().year,
        'month': datetime.now().month
    }

    # Step 3: Make API call to submit the payment data
    response = requests.post(f"{BASE_URL}/payments", json=payment_payload)
    markup_remove = types.ReplyKeyboardRemove()
    
    # Step 4: Send confirmation to user based on API response
    if response.status_code == 201:
        bot.send_message(cid, translate("Pago realizado con éxito.", target_lang), reply_markup=markup_remove)
    else:
        bot.send_message(cid, f"{translate('Error en el pago.', target_lang)} Error: {response.status_code}", reply_markup=markup_remove)

    # Step 5: Clear stored data
    payment_data.pop(cid, None)
