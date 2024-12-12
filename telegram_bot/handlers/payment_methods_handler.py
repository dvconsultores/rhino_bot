import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv
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

def show_payment_method_list(bot, message):
    """
    Fetch and display the list of available payment methods to the admin user.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    # Fetch payment methods from the API
    response = requests.get(f"{BASE_URL}/payment_methods")
    
    if response.status_code != 200:
        bot.send_message(message.chat.id, translate("Error al obtener los métodos de pago.", target_lang))
        return
    
    payment_methods = response.json()
    
    # Check if there are any payment methods available
    if not payment_methods:
        bot.send_message(message.chat.id, translate("No hay métodos de pago disponibles.", target_lang))
        return

    # Build a list of payment methods to display
    payment_methods_text = "*" + translate("Métodos de pago disponibles:", target_lang) + "*" + "\n"
    for method in payment_methods:
        method_name = method.get("method")
        method_id = method.get("id")
        payment_methods_text += f"🔹 *{translate('ID del método:', target_lang)}*: {method_id} - *{translate('Nombre del método:', target_lang)}*: {method_name}\n"

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("/menu")
    markup.row(item1)

    # Send the list to the admin user
    bot.send_message(message.chat.id, payment_methods_text, parse_mode="Markdown", reply_markup=markup)

def add_payment_method_handler(bot, message):
    """
    Ask the admin for the new payment method name.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = create_cancel_markup(target_lang)
    bot.send_message(message.chat.id, translate("Por favor, ingrese el nombre del nuevo método de pago:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: submit_new_payment_method(bot, msg))

def submit_new_payment_method(bot, message):
    """
    Process the payment amount and confirm the payment.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    new_method_name = message.text.strip()
    
    if new_method_name:
        bot.send_message(cid, translate("Procesando...", target_lang))
        response = requests.post(f"{BASE_URL}/payment_methods", json={"method": new_method_name})
        
        if response.status_code == 201:
            bot.send_message(cid, translate("Método de pago creado con éxito.", target_lang))
            show_payment_method_list(bot, message)
        else:
            bot.send_message(cid, translate("Error al crear el método de pago.", target_lang))
    else:
        bot.send_message(cid, translate("El nombre del método de pago no puede estar vacío.", target_lang))
        add_payment_method_handler(bot, message)  # Retry adding if input was empty

def list_payment_methods_for_selection(bot, message, action):
    """
    Fetch and display the list of available payment methods for selection.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/payment_methods")
    
    if response.status_code == 200:
        payment_methods = response.json()
        
        if payment_methods:
            # Display payment methods for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for method in payment_methods:
                button = types.KeyboardButton(f"{method['id']}: {method['method']}")
                markup.add(button)
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, translate("Seleccione un método de pago:", target_lang), reply_markup=markup)
            
            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_selection(bot, msg, payment_methods))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_selection(bot, msg, payment_methods))
        else:
            bot.send_message(cid, translate("No hay métodos de pago disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los métodos de pago.", target_lang))

def handle_delete_selection(bot, message, payment_methods):
    """
    Handle the selection of a payment method to delete.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text
    
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        # Extract method ID from the selected option
        method_id = int(choice.split(":")[0].strip())
        selected_method = next((m for m in payment_methods if m['id'] == method_id), None)
        
        if selected_method:
            confirm_delete_method(bot, message, selected_method)
        else:
            bot.send_message(cid, translate("Selección de método de pago inválida.", target_lang))
            list_payment_methods_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, translate("Selección de método de pago inválida.", target_lang))
        list_payment_methods_for_selection(bot, message, "delete")

def confirm_delete_method(bot, message, selected_method):
    """
    Confirm the deletion of the selected payment method.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton(translate("Sí", target_lang)), types.KeyboardButton(translate("Cancelar", target_lang)))
    
    # Send the confirmation message
    bot.send_message(cid, f"{translate('¿Está seguro de que desea eliminar el método de pago', target_lang)} '{selected_method['method']}'?", reply_markup=markup)
    
    # Register the next step handler to capture the confirmation response
    bot.register_next_step_handler(message, lambda msg: handle_delete_confirmation(bot, msg, selected_method['id']))

def handle_delete_confirmation(bot, message, payment_method_id):
    """
    Handle delete confirmation and direct to deletion.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text == translate("Sí", target_lang):
        delete_payment_method(bot, message, payment_method_id)
    else:
        bot.send_message(cid, translate("Proceso cancelado.", target_lang))

def delete_payment_method(bot, message, payment_method_id):
    """
    Perform deletion.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    bot.send_message(cid, translate("Procesando...", target_lang))
    
    response = requests.delete(f"{BASE_URL}/payment_methods/{payment_method_id}")
    
    if response.status_code == 204:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton("/menu")
        markup.row(item1)
        bot.send_message(cid, translate("Método de pago eliminado con éxito.", target_lang), reply_markup=markup)
    else:
        bot.send_message(cid, translate("Error al eliminar el método de pago.", target_lang))
    
    # Return to the list of payment methods
    show_payment_method_list(bot, message)

def handle_edit_selection(bot, message, payment_methods):
    """
    Handle the selection of a payment method to edit.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        # Extract method ID from the selected option
        method_id = int(choice.split(":")[0].strip())
        selected_method = next((m for m in payment_methods if m['id'] == method_id), None)
        
        if selected_method:
            bot.send_message(cid, f"{translate('Por favor, ingrese el nuevo nombre para el método de pago', target_lang)} {selected_method['method']}:")
            bot.register_next_step_handler(message, lambda msg: edit_payment_method(bot, msg, selected_method['id']))
        else:
            bot.send_message(cid, translate("Selección de método de pago inválida.", target_lang))
            list_payment_methods_for_selection(bot, message, "edit")
    except ValueError:
        bot.send_message(cid, translate("Selección de método de pago inválida.", target_lang))
        list_payment_methods_for_selection(bot, message, "edit")

def edit_payment_method(bot, message, payment_method_id):
    """
    Perform update.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_name = message.text.strip()
    
    if new_name:
        bot.send_message(cid, translate("Procesando...", target_lang))
        response = requests.put(f"{BASE_URL}/payment_methods/{payment_method_id}", json={"method": new_name})
        if response.status_code == 200:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            item1 = types.KeyboardButton("/menu")
            markup.row(item1)
            bot.send_message(cid, translate("Método de pago actualizado con éxito.", target_lang), reply_markup=markup)
        else:
            bot.send_message(cid, translate("Error al actualizar el método de pago.", target_lang))
    else:
        bot.send_message(cid, translate("El nombre del método de pago no puede estar vacío.", target_lang))
    
    # Return to main payment methods list after action
    show_payment_method_list(bot, message)

def delete_payment_method_handler(bot, message):
    """
    Entry point for delete action.
    """
    list_payment_methods_for_selection(bot, message, "delete")

def edit_payment_method_handler(bot, message):
    """
    Entry point for edit action.
    """
    list_payment_methods_for_selection(bot, message, "edit")
