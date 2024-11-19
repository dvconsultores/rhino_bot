import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

def create_cancel_markup():
    """Create a reply markup with a 'Cancel' button."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton(_("general_cancel"))
    markup.row(item1)
    return markup

def cancel_process(bot, message):
    """Handle the cancellation of the process."""
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton(("/menu"))
    markup.row(item1)
    bot.send_message(cid, _("process_canceled"), reply_markup=markup)
    # user_data.pop(cid, None)  # Clear user data after cancellation

def show_payment_method_list(bot, message):
    """
    Fetch and display the list of available payment methods to the admin user.
    """
    # Fetch payment methods from the API
    response = requests.get(f"{BASE_URL}/payment_methods")
    
    if response.status_code != 200:
        bot.send_message(message.chat.id, _("payment_fetch_fail"))
        return
    
    payment_methods = response.json()
    
    # Check if there are any payment methods available
    if not payment_methods:
        bot.send_message(message.chat.id, _("payment_fetch_not_available"))
        return

    # Build a list of payment methods to display
    payment_methods_text = "*" + _("payment_fetch_available") + "*" + "\n"
    for method in payment_methods:
        method_name = method.get("method")
        method_id = method.get("id")
        payment_methods_text += f"🔹 *{_('payment_id')}*: {method_id} - *{_('payment_name')}*: {method_name}\n"


    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton(("/menu"))
    markup.row(item1)

    # Send the list to the admin user
    bot.send_message(message.chat.id, payment_methods_text, parse_mode="Markdown", reply_markup=markup)

# Function to prompt admin to add a new payment method
def add_payment_method_handler(bot, message):
    markup = create_cancel_markup()
    """Ask the admin for the new payment method name."""
    bot.send_message(message.chat.id, _("payment_add_ask_name"), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: submit_new_payment_method(bot, msg))

# Function to handle the submission of the new payment method
def submit_new_payment_method(bot, message):
    """Process the payment amount and confirm the payment."""
    if message.text.strip().lower() == _("general_cancel").lower():
        cancel_process(bot, message)
        return

    cid = message.chat.id
    new_method_name = message.text.strip()
    
    if new_method_name:
        bot.send_message(cid, _("procesing"))
        response = requests.post(f"{BASE_URL}/payment_methods", json={"method": new_method_name})
        
        if response.status_code == 201:
            bot.send_message(cid, _("payment_method_success"))
            show_payment_method_list(bot, message)
        else:
            bot.send_message(cid, _("payment_method_error"))
    else:
        bot.send_message(cid, _("payment_validate_error"))
        add_payment_method_handler(bot, message)  # Retry adding if input was empty

# List all payment methods for selection
def list_payment_methods_for_selection(bot, message, action):
    cid = message.chat.id
    response = requests.get(f"{BASE_URL}/payment_methods")
    
    if response.status_code == 200:
        payment_methods = response.json()
        
        if payment_methods:
            # Display payment methods for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for method in payment_methods:
                button = types.KeyboardButton(f"{method['id']}: {method['method']}")
                markup.add(button)
            markup.add(types.KeyboardButton(_("general_cancel")))
            bot.send_message(cid, f"{_('payment_fetch_available')}", reply_markup=markup)
            
            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_selection(bot, msg, payment_methods))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_selection(bot, msg, payment_methods))
        else:
            bot.send_message(cid, _("payment_fetch_not_available"))
    else:
        bot.send_message(cid, _("payment_fetch_fail"))

# Handler for selecting a payment method to delete
def handle_delete_selection(bot, message, payment_methods):
    cid = message.chat.id
    choice = message.text
    
    if message.text.strip().lower() == _("general_cancel").lower():
        cancel_process(bot, message)
        return

    try:
        # Extract method ID from the selected option
        method_id = int(choice.split(":")[0].strip())
        selected_method = next((m for m in payment_methods if m['id'] == method_id), None)
        
        if selected_method:
            confirm_delete_method(bot, message, selected_method)
        else:
            bot.send_message(cid, _("payment_delete_action_invalid"))
            list_payment_methods_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, _("payment_delete_action_invalid_input"))
        list_payment_methods_for_selection(bot, message, "delete")

# Confirmation for deletion
def confirm_delete_method(bot, message, selected_method):
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton(_("payment_delete_yes")), types.KeyboardButton(_("general_cancel")))
    
    # Send the confirmation message
    bot.send_message(cid, _("payment_delete_yes") + "'{selected_method['method']}'" + "?", reply_markup=markup)
    
    # Register the next step handler to capture the confirmation response
    bot.register_next_step_handler(message, lambda msg: handle_delete_confirmation(bot, msg, selected_method['id']))

# Handle delete confirmation and direct to deletion
def handle_delete_confirmation(bot, message, payment_method_id):
    cid = message.chat.id
    
    if message.text == _("payment_delete_yes"):
        delete_payment_method(bot, message, payment_method_id)
    else:
        bot.send_message(cid, _("payment_delete_canceled"))

# Perform deletion
def delete_payment_method(bot, message, payment_method_id):
    cid = message.chat.id
    bot.send_message(cid, _("procesing"))
    
    response = requests.delete(f"{BASE_URL}/payment_methods/{payment_method_id}")
    
    if response.status_code == 204:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton(("/menu"))
        markup.row(item1)
        bot.send_message(cid, _("payment_delete_deleted"), reply_markup=markup)
    else:
        bot.send_message(cid, _("payment_delete_in_use"))
    
    # Return to the list of payment methods
    show_payment_method_list(bot, message)

# Handler for selecting a payment method to edit
def handle_edit_selection(bot, message, payment_methods):
    cid = message.chat.id
    choice = message.text

    if message.text.strip().lower() == _("general_cancel").lower():
        cancel_process(bot, message)
        return

    try:
        # Extract method ID from the selected option
        method_id = int(choice.split(":")[0].strip())
        selected_method = next((m for m in payment_methods if m['id'] == method_id), None)
        
        if selected_method:
            bot.send_message(cid,f"{_('payment_update_ask')} {selected_method['method']}:")
            bot.register_next_step_handler(message, lambda msg: edit_payment_method(bot, msg, selected_method['id']))
        else:
            bot.send_message(cid, _("payment_update_invalid"))
            list_payment_methods_for_selection(bot, message, "edit")
    except ValueError:
        bot.send_message(cid, _("payment_update_invalid"))
        list_payment_methods_for_selection(bot, message, "edit")

# Perform update
def edit_payment_method(bot, message, payment_method_id):
    cid = message.chat.id
    new_name = message.text.strip()
    
    if new_name:
        bot.send_message(cid, _("procesing"))
        response = requests.put(f"{BASE_URL}/payment_methods/{payment_method_id}", json={"method": new_name})
        if response.status_code == 200:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            item1 = types.KeyboardButton(("/menu"))
            markup.row(item1)
            bot.send_message(cid, _("payment_update_success"), reply_markup=markup)
        else:
            bot.send_message(cid, _("payment_update_error"))
    else:
        bot.send_message(cid, _("payment_update_error_empty"))
    
    # Return to main payment methods list after action
    show_payment_method_list(bot, message)

# Entry points for delete and edit actions
def delete_payment_method_handler(bot, message):
    list_payment_methods_for_selection(bot, message, "delete")

def edit_payment_method_handler(bot, message):
    list_payment_methods_for_selection(bot, message, "edit")
