import os
import requests
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from dotenv import load_dotenv

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Load environment variables
load_dotenv()


# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
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
    payment_data.pop(cid, None)  # Clear payment data after cancellation

# Step 1: Fetch payment methods and display them as buttons
def start_payment(bot, message):
    cid = message.chat.id

    # Fetch payment methods from the API
    response = requests.get(f"{BASE_URL}/payment_methods")
    if response.status_code != 200:
        bot.send_message(cid, "Failed to fetch payment methods.")
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
    item1 = types.KeyboardButton(_("general_cancel"))
    markup.row(item1)

    bot.send_message(cid, _("get_payment_id"), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: handle_payment_method_selection(bot, msg, payment_methods))

# Step 1b: Handle selected payment method from user’s message text
def handle_payment_method_selection(bot, message, payment_methods):
    """Process the user's selected payment method and ask for the payment amount."""
    if message.text.strip().lower() == _("general_cancel").lower():
        cancel_process(bot, message)
        return

    cid = message.chat.id
    selected_method_name = message.text
    
    # Find the selected method ID and name based on the user's choice
    selected_method = next((method for method in payment_methods if method["method"] == selected_method_name), None)
    
    if selected_method:
        if cid not in payment_data:
            payment_data[cid] = {}
        payment_data[cid]["payment_method_id"] = selected_method["id"]
        payment_data[cid]["payment_method_name"] = selected_method_name  # Store the method name
        markup = create_cancel_markup()
        bot.send_message(cid, _("payment_amount"), reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: handle_payment_amount(bot, msg))
    else:
        bot.send_message(cid, _("payment_invalid"))
        bot.register_next_step_handler(message, lambda msg: handle_payment_method_selection(bot, msg, payment_methods))
        

def handle_payment_amount(bot, message):
    """Process the payment amount and confirm the payment."""
    if message.text.strip().lower() == _("general_cancel").lower():
        cancel_process(bot, message)
        return

    cid = message.chat.id
    amount = message.text.strip()
    if is_float(amount) == False:      
        bot.send_message(cid, _("payment_amount_invalid"))
        bot.register_next_step_handler(message, lambda msg: handle_payment_amount(bot, msg))
        return

    payment_data[cid]["amount"] = float(amount)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Skip")
    bot.send_message(cid, _("payment_reference"), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: process_payment_reference(bot, msg))

# Step 3: Process payment reference
def process_payment_reference(bot, message):
    cid = message.chat.id
    payment_data[cid]["reference"] = message.text if message.text.lower() != "skip" else None
    
    # Ask for payment proof (image or PDF)
    markup = create_cancel_markup()
    bot.send_message(cid, _("payment_image"), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: process_payment_proof(bot, msg))

# Step 4: Process payment proof upload
def process_payment_proof(bot, message):
    cid = message.chat.id
    
    # Handle photo or document upload
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'document' and message.document.mime_type in ["application/pdf"]:
        file_id = message.document.file_id
    else:
        bot.send_message(cid, _("payment_image_invalid"))
        bot.register_next_step_handler(message, lambda msg: process_payment_proof(bot, msg))
        return

    # Download and save the file
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"{cid}_{datetime.now().strftime('%Y%m%d')}_{file_info.file_path.split('/')[-1]}"
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
    data = payment_data[cid]
    confirmation_text = (
        _("payment_confirm1") + "\n\n" +
        _("payment_confirm2") + f" {data['payment_method_name']}\n" +  # Display name instead of ID
        _("payment_confirm3") + f" {data['amount']}\n" +
        _("payment_confirm4") + f" {data['reference'] or 'None'}\n"
    )

    # Show confirmation options with Yes, No, and Cancel buttons
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = types.KeyboardButton(_("general_yes"))
    item2 = types.KeyboardButton(_("general_no"))
    item3 = types.KeyboardButton(_("general_cancel"))
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)

    # Send message with confirmation options
    msg = bot.send_message(cid, confirmation_text, reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda msg: confirmation_handler(bot, msg))  # Correct usage here

# Step 6: Handle confirmation response
def confirmation_handler(bot, message):
    cid = message.chat.id

    if message.text not in [_("general_yes"), _("general_no"), _("general_cancel")]:
        bot.send_message(cid, _("payment_confirm_invalid"))
        bot.register_next_step_handler(message, lambda msg: confirmation_handler(bot, msg))  # Correct usage here
        return
   
    if message.text == _("general_yes"):
        submit_payment(cid)  # Proceed with payment submission
        bot.send_message(cid, _("procesing"))
    elif message.text == _("general_no"):
        bot.send_message(cid, _("payment_restart"))
        start_payment(bot, message)  # Restart the payment process
    elif message.text == _("general_cancel"):
        bot.send_message(cid, _("payment_canceled"))
        payment_data.pop(cid, None)  # Clear stored payment data


# Submit payment to the API
def submit_payment(cid):
    # Step 1: Fetch user ID from the backend using the Telegram user ID (cid)
    user_response = requests.get(f"{BASE_URL}/users/telegram/{cid}")
    
    # Handle cases where the user is not found or there is an error
    if user_response.status_code != 200:
        bot.send_message(cid, _("payment_no_user"))
        return

    # Extract the user ID from the response
    user_data = user_response.json()
    user_id = user_data.get('id')
    
    if not user_id:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton(("/menu"))
        markup.row(item1)
        bot.send_message(cid, _("payment_no_user"), reply_markup=markup)
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
        bot.send_message(cid, _("payment_success"), reply_markup=markup_remove)
    else:
        bot.send_message(cid, ("payment_failed") + {response.status_code}, reply_markup=markup_remove)

    # Step 5: Clear stored data
    payment_data.pop(cid, None)
