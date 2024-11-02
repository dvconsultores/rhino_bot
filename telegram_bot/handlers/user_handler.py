import requests
import telebot
from telebot import types
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import re
from datetime import datetime

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Load environment variables
load_dotenv()

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

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
    msg = bot.send_message(cid, _("get_user_id"))
    bot.register_next_step_handler(msg, fetch_user_info, bot=bot)

def fetch_user_info(message, bot):
    user_id = message.text
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            user_info = "\n".join([f"{key}: {value}" for key, value in user_data.items()])
            bot.send_message(message.chat.id, f"User Info:\n{user_info}")
        else:
            bot.send_message(message.chat.id, "User not found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Dictionary to store user data temporarily
user_data = {}

# Simplified create_user function to only take message
def create_user(bot, message):
    """Start user creation by asking for the user's name."""
    user_data[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, _("create_user_name"))
    bot.register_next_step_handler(msg, process_name, bot=bot)


def process_name(message, bot):
    """Process the user's name and ask for the last name."""
    if not message.text.strip():
        msg = bot.send_message(message.chat.id, _("create_user_name_required"))
        bot.register_next_step_handler(msg, process_name, bot=bot)
        return
    
    user_data[message.chat.id]["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, _("create_user_last_name"))
    bot.register_next_step_handler(msg, process_lastname, bot=bot)

def process_lastname(message, bot):
    """Process the last name and ask for the cedula."""
    if not message.text.strip():
        msg = bot.send_message(message.chat.id, _("create_user_last_name_required"))
        bot.register_next_step_handler(msg, process_lastname, bot=bot)
        return
    
    user_data[message.chat.id]["lastname"] = message.text.strip()
    msg = bot.send_message(message.chat.id, _("create_user_cedula"))
    bot.register_next_step_handler(msg, process_cedula, bot=bot)

def process_cedula(message, bot):
    """Process the cedula and ask for the email."""
    cedula_input = message.text.strip()

    # Check if cedula is empty or not an integer
    if not cedula_input or not cedula_input.isdigit():
        msg = bot.send_message(message.chat.id, _("create_user_cedula_format"))
        bot.register_next_step_handler(msg, process_cedula, bot=bot)
        return

    # Store the valid cedula as an integer
    user_data[message.chat.id]["cedula"] = int(cedula_input)
    msg = bot.send_message(message.chat.id, _("create_user_email"))
    bot.register_next_step_handler(msg, process_email, bot=bot)

def process_email(message, bot):
    """Process the email and validate its format, then ask for the date of birth."""
    if not validate_email(message.text.lower()):
        msg = bot.send_message(message.chat.id, _("create_user_email_required"))
        bot.register_next_step_handler(msg, process_email, bot=bot)
        return
    
    user_data[message.chat.id]["email"] = message.text.lower()
    msg = bot.send_message(message.chat.id, _("create_user_date_of_birth"))
    bot.register_next_step_handler(msg, process_date_of_birth, bot=bot)

def process_date_of_birth(message, bot):
    """Process the date of birth, validate it, and then ask for the phone number."""
    date_input = message.text.strip()

    # Validate and reformat date
    try:
        # Convert from dd/mm/yyyy to yyyy-mm-dd format
        formatted_date = datetime.strptime(date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        # If the date is invalid, ask again
        msg = bot.send_message(message.chat.id, _("create_user_date_of_birth_required"))
        bot.register_next_step_handler(msg, process_date_of_birth, bot=bot)
        return
    
    # Save the correctly formatted date to user_data
    user_data[message.chat.id]["date_of_birth"] = formatted_date
    msg = bot.send_message(message.chat.id, _("create_user_phone_number"))
    bot.register_next_step_handler(msg, process_phone, bot=bot)

def process_phone(message, bot):
    """Process the phone number and then ask for the Instagram handle."""
    phone_input = message.text.strip()

    # Check if the phone number is empty or not an integer
    if not phone_input or not phone_input.isdigit():
        msg = bot.send_message(message.chat.id, _("create_user_phone_number_required"))
        bot.register_next_step_handler(msg, process_phone, bot=bot)
        return

    # Store the valid phone number as an integer
    user_data[message.chat.id]["phone"] = int(phone_input)

    # Create markup with a 'Skip' button for the next step
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = types.KeyboardButton('Skip')
    markup.row(item1)
    msg = bot.send_message(message.chat.id, _("create_user_ig"), parse_mode='Markdown', reply_markup=markup)         
    bot.register_next_step_handler(msg, process_instagram, bot=bot)


# Function to handle Instagram input and show confirmation
def process_instagram(message, bot):
    """Process the Instagram handle and then confirm user details before creation."""
    user_data[message.chat.id]["instagram"] = message.text if message.text.lower() != "skip" else None

    # Set default values for type, status, and telegram_id
    user_data[message.chat.id]["type"] = "cliente"
    user_data[message.chat.id]["estatus"] = "activo"
    user_data[message.chat.id]["telegram_id"] = message.chat.id

   # Titles dictionary to map data keys to personalized titles
    titles = {
        "name": _("create_user_title_name"),
        "lastname": _("create_user_title_last_name"),
        "cedula": _("create_user_title_cedula"),
        "email": _("create_user_title_email"),
        "date_of_birth": _("create_user_title_date_of_birth"),
        "phone": _("create_user_title_phone"),
        "instagram": _("create_user_title_ig"),
        "type": _("create_user_title_type"),
        "status": _("create_user_title_status"),
        "telegram_id": _("create_user_title_telegram_id")
    }

    # Display collected data for confirmation with personalized titles, limited to 7 fields
    user_info = "\n".join([f"{titles.get(key, key)}: {value}" 
                        for key, value in list(user_data[message.chat.id].items())[:7] if value])
    confirmation_text = _("create_user_confirm") + "\n" + user_info


    # Show confirmation options with Yes, No, and Cancel buttons
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item1 = types.KeyboardButton(_("general_yes"))
    item2 = types.KeyboardButton(_("general_no"))
    item3 = types.KeyboardButton(_("general_cancel"))
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    msg = bot.send_message(message.chat.id, confirmation_text, reply_markup=markup)
    bot.register_next_step_handler(msg, lambda msg: confirmation_handler(msg, bot))  # Provide `message` and `bot`

# Confirmation Handler
def confirmation_handler(message, bot):
    """Handle the user's confirmation choice."""
    cid = message.chat.id
    
    # Remove the reply keyboard
    markup_remove = types.ReplyKeyboardRemove()
    
    if message.text == _("general_yes"):
        # Check if the user already exists by telegram_id
        check_response = requests.get(f"{BASE_URL}/users/telegram/{cid}")

        if check_response.status_code == 200:
            # User exists, perform an update (PUT)
            response = requests.put(f"{BASE_URL}/users/telegram/{cid}", json=user_data[cid])
            if response.status_code == 200:
                bot.send_message(cid, _("create_user_success") + " 😊 " + _("create_user_updated"), reply_markup=markup_remove)
            else:
                bot.send_message(cid, f"Failed to update user. Error: {response.status_code} 😢", reply_markup=markup_remove)
        elif check_response.status_code == 404:
            # User does not exist, perform a creation (POST)
            response = requests.post(f"{BASE_URL}/users", json=user_data[cid])
            if response.status_code == 201:
                bot.send_message(cid, _("create_user_success") + " 😊", reply_markup=markup_remove)
            else:
                bot.send_message(cid, f"Failed to create user. Error: {response.status_code} 😢", reply_markup=markup_remove)
        else:
            # Handle unexpected errors (e.g., server error)
            bot.send_message(cid, f"An error occurred. Status code: {check_response.status_code} 😢", reply_markup=markup_remove)

        # Clear user data after creation or update
        user_data.pop(cid, None)

    elif message.text == _("general_no"):
        # Restart user creation process
        msg = bot.send_message(cid, _("create_user_restart"), reply_markup=markup_remove)
        bot.register_next_step_handler(msg, process_name, bot=bot)
        # bot.register_next_step_handler(msg, lambda msg: create_user(msg, bot))
        

    elif message.text == _("general_cancel"):
        # Cancel user creation process
        bot.send_message(cid, _("create_user_cancel"), reply_markup=markup_remove)
        user_data.pop(cid, None)  # Clear user data after cancellation


def update_user(bot, message):
    """Prompt to update an existing user."""
    msg = bot.send_message(message.chat.id, "Please provide the user ID to update:")
    bot.register_next_step_handler(msg, process_user_update, bot=bot)

def process_user_update(message, bot):
    user_id = message.text
    msg = bot.send_message(message.chat.id, "Provide new details in format:\n"
                                            "`name,lastname,cedula,email,date_of_birth (dd/mm/yyyy),phone,instagram,type,status,telegram_id`")
    bot.register_next_step_handler(msg, send_update_request, user_id=user_id, bot=bot)

def send_update_request(message, user_id, bot):
    updated_data = message.text.split(',')
    if len(updated_data) < 6:
        bot.send_message(message.chat.id, "Missing required fields. Please provide at least name, lastname, cedula, email, date_of_birth, and phone.")
        return

    keys = ["name", "lastname", "cedula", "email", "date_of_birth", "phone", "instagram", "type", "status", "telegram_id"]
    data = dict(zip(keys, updated_data))
    
    # Set default values if not provided
    data['type'] = data.get('type', 'cliente')
    data['status'] = data.get('status', 'ACTIVO')

    # Validate required fields
    if not all([data.get("name"), data.get("lastname"), data.get("cedula"), data.get("email"), data.get("phone")]):
        bot.send_message(message.chat.id, "Error: name, lastname, cedula, email, and phone are required fields.")
        return

    # Validate date format
    if not validate_date(data["date_of_birth"]):
        bot.send_message(message.chat.id, "Error: Date of birth must be in format dd/mm/yyyy.")
        return

    # Validate email format
    if not validate_email(data["email"]):
        bot.send_message(message.chat.id, "Error: Invalid email format.")
        return

    # Send the request to update the user
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=data)
    if response.status_code == 200:
        bot.send_message(message.chat.id, "User updated successfully!")
    else:
        bot.send_message(message.chat.id, f"Failed to update user. Error: {response.status_code}")
