import requests
from telebot import types
from telebot.types import Message
from dotenv import load_dotenv
import os
import re
from datetime import datetime

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
    msg = bot.send_message(cid, "Please provide the user ID:")
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

def create_user(bot, message):
    """Start user creation by asking for the user's name."""
    user_data[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, _("Please enter the user's name:"))
    bot.register_next_step_handler(msg, process_name, bot=bot)

def process_name(message, bot):
    """Process the user's name and ask for the last name."""
    if not message.text.strip():
        msg = bot.send_message(message.chat.id, _("Name is required. Please enter the user's name:"))
        bot.register_next_step_handler(msg, process_name, bot=bot)
        return
    
    user_data[message.chat.id]["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, _("Please enter the user's last name:"))
    bot.register_next_step_handler(msg, process_lastname, bot=bot)

def process_lastname(message, bot):
    """Process the last name and ask for the cedula."""
    if not message.text.strip():
        msg = bot.send_message(message.chat.id, _("Last name is required. Please enter the user's last name:"))
        bot.register_next_step_handler(msg, process_lastname, bot=bot)
        return
    
    user_data[message.chat.id]["lastname"] = message.text.strip()
    msg = bot.send_message(message.chat.id, _("Please enter the user's cedula:"))
    bot.register_next_step_handler(msg, process_cedula, bot=bot)

def process_cedula(message, bot):
    """Process the cedula and ask for the email."""
    if not message.text.strip():
        msg = bot.send_message(message.chat.id, _("Cedula is required. Please enter the user's cedula:"))
        bot.register_next_step_handler(msg, process_cedula, bot=bot)
        return

    user_data[message.chat.id]["cedula"] = message.text.strip()
    msg = bot.send_message(message.chat.id, _("Please enter the user's email:"))
    bot.register_next_step_handler(msg, process_email, bot=bot)

def process_email(message, bot):
    """Process the email and validate its format, then ask for the date of birth."""
    if not validate_email(message.text):
        msg = bot.send_message(message.chat.id, _("Invalid email format. Please re-enter:"))
        bot.register_next_step_handler(msg, process_email, bot=bot)
        return
    
    user_data[message.chat.id]["email"] = message.text
    msg = bot.send_message(message.chat.id, _("Please enter the user's date of birth (dd/mm/yyyy):"))
    bot.register_next_step_handler(msg, process_date_of_birth, bot=bot)

def process_date_of_birth(message, bot):
    """Process the date of birth, validate it, and then ask for the phone number."""
    if not validate_date(message.text):
        msg = bot.send_message(message.chat.id, _("Invalid date format. Please re-enter (dd/mm/yyyy):"))
        bot.register_next_step_handler(msg, process_date_of_birth, bot=bot)
        return
    
    user_data[message.chat.id]["date_of_birth"] = message.text
    msg = bot.send_message(message.chat.id, _("Please enter the user's phone number:"))
    bot.register_next_step_handler(msg, process_phone, bot=bot)

def process_phone(message, bot):
    """Process the phone number and then ask for the Instagram handle."""
    if not message.text.strip():
        msg = bot.send_message(message.chat.id, _("Phone number is required. Please enter the user's phone number:"))
        bot.register_next_step_handler(msg, process_phone, bot=bot)
        return

    user_data[message.chat.id]["phone"] = message.text.strip()
    msg = bot.send_message(message.chat.id, _("Please enter the user's Instagram handle (or type 'skip' to leave it empty):"))
    bot.register_next_step_handler(msg, process_instagram, bot=bot)

def process_instagram(message, bot):
    """Process the Instagram handle and then confirm user details before creation."""
    user_data[message.chat.id]["instagram"] = message.text if message.text.lower() != "skip" else None

    # Set default values for type, status, and telegram_id
    user_data[message.chat.id]["type"] = "cliente"
    user_data[message.chat.id]["status"] = "ACTIVO"
    user_data[message.chat.id]["telegram_id"] = message.chat.id

    # Display collected data for confirmation
    user_info = "\n".join([f"{key}: {value}" for key, value in list(user_data[message.chat.id].items())[:7] if value])
    confirmation_text = _("Please confirm the details:\n") + user_info

    # Show confirmation options with Yes, No, and Cancel buttons
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(_("Yes"), callback_data="confirm_yes"))
    markup.add(types.InlineKeyboardButton(_("No"), callback_data="confirm_no"))
    markup.add(types.InlineKeyboardButton(_("Cancel"), callback_data="confirm_cancel"))
    bot.send_message(message.chat.id, confirmation_text, reply_markup=markup)

def confirmation_handler(call, bot):
    """Handle confirmation of user creation."""
    cid = call.message.chat.id
    action = call.data.split("_")[1]

    if action == "yes":
        # Send the API request to create the user
        response = requests.post(f"{BASE_URL}/users", json=user_data[cid])
        if response.status_code == 201:
            bot.send_message(cid, _("User created successfully!"))
        else:
            bot.send_message(cid, _("Failed to create user.") + f" Error: {response.status_code}")
        user_data.pop(cid)  # Clear user data after creation

    elif action == "no":
        # Restart user creation process
        bot.send_message(cid, _("Let's try again. Please enter the user's name:"))
        bot.register_next_step_handler(call.message, process_name, bot=bot)
        user_data.pop(cid)  # Clear previous data

    elif action == "cancel":
        bot.send_message(cid, _("User creation cancelled."))
        user_data.pop(cid)  # Clear user data

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
