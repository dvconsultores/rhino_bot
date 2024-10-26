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

def create_user(bot, message):
    """Prompt to create a new user."""
    msg = bot.send_message(message.chat.id, "Please provide the user details in the format:\n"
                                            "`name,lastname,cedula,email,date_of_birth (dd/mm/yyyy),phone,instagram,type,status,telegram_id`")
    bot.register_next_step_handler(msg, process_user_creation, bot=bot)

def process_user_creation(message, bot):
    """Process user creation from input."""
    user_data = message.text.split(',')
    if len(user_data) < 6:  # Ensure required fields are present
        bot.send_message(message.chat.id, "Missing required fields. Please provide at least name, lastname, cedula, email, date_of_birth, and phone.")
        return

    keys = ["name", "lastname", "cedula", "email", "date_of_birth", "phone", "instagram", "type", "status", "telegram_id"]
    data = dict(zip(keys, user_data))
    
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

    # Send the request to create the user
    response = requests.post(f"{BASE_URL}/users", json=data)
    if response.status_code == 201:
        bot.send_message(message.chat.id, "User created successfully!")
    else:
        bot.send_message(message.chat.id, f"Failed to create user. Error: {response.status_code}")

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
