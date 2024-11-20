import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv
import re

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
    item1 = types.KeyboardButton("/menu")
    markup.row(item1)
    bot.send_message(cid, _("process_canceled"), reply_markup=markup)

def sanitize_text(text):
    """
    Remove all special characters that might interfere with Telegram MarkdownV2.
    """
    # Allow only alphanumeric characters and spaces
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

# List all locations
def list_locations(bot, message):
    """
    Fetch and display the list of all available locations.
    """
    cid = message.chat.id
    response = requests.get(f"{BASE_URL}/locations")

    if response.status_code == 200:
        locations = response.json()

        if locations:
            # Build a text representation of the locations
            locations_text = f"{_('locations_available')}\n"
            for loc in locations:
                locations_text += f"*{_('locations_id')}*: {loc['id']} \n*{_('locations_locations')}*: {loc['location']} \n*{_('locations_address')}*: {loc['address']}\n"

            # Send the list of locations to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, locations_text, parse_mode="MarkdownV2", reply_markup=markup)
        else:
            bot.send_message(cid, _("locations_not_available"))
    else:
        bot.send_message(cid, _("locations_failed_fetch"))


# Add a new location
def add_location_handler(bot, message):
    """
    Start the process of adding a new location.
    """
    markup = create_cancel_markup()
    bot.send_message(message.chat.id, _('locations_name'), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: add_location_name_handler(bot, msg))


def add_location_name_handler(bot, message):
    """
    Handle the name input for the new location and ask for the address.
    """
    if message.text.strip().lower() == _("general_cancel"):
        cancel_process(bot, message)
        return

    location_name = message.text.strip()

    if not location_name:
        bot.send_message(message.chat.id, _("locations_no_empty"))
        add_location_handler(bot, message)
        return

    bot.send_message(message.chat.id, _("locations_location"))
    bot.register_next_step_handler(message, lambda msg: submit_new_location(bot, msg, location_name))


def submit_new_location(bot, message, location_name):
    """
    Submit the new location to the backend.
    """
    if message.text.strip().lower() == "cancel":
        cancel_process(bot, message)
        return

    cid = message.chat.id    

    location_address = message.text.strip()

    if not location_address:
        bot.send_message(message.chat.id, _("locations_no_empty"))
        bot.register_next_step_handler(message, lambda msg: submit_new_location(bot, msg, location_name))
        return

    data = {"location": location_name, "address": location_address}
    response = requests.post(f"{BASE_URL}/locations", json=data)
    bot.send_message(cid, _("procesing"))
    if response.status_code == 201:
        bot.send_message(message.chat.id, _("plans_success"))
        list_locations(bot, message)
    else:
        bot.send_message(message.chat.id, _("plans_fails"))


# List all locations for selection
def list_locations_for_selection(bot, message, action):
    """
    Fetch and display the list of available locations for selection.
    """
    cid = message.chat.id
    response = requests.get(f"{BASE_URL}/locations")

    if response.status_code == 200:
        locations = response.json()

        if locations:
            # Display locations for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for loc in locations:
                button = types.KeyboardButton(f"{loc['id']}: {loc['location']} ({loc['address']})")
                markup.add(button)
            markup.add(types.KeyboardButton(_("general_cancel")))
            bot.send_message(cid, _("locations_list"), reply_markup=markup)

            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_location_selection(bot, msg, locations))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_location_selection(bot, msg, locations))
        else:
            bot.send_message(cid, _("locations_not_available"))
    else:
        bot.send_message(cid, _("locations_failed_fetch"))

# Handle selecting a location to edit
def handle_edit_location_selection(bot, message, locations):
    """
    Handle the selection of a location to edit.
    """
    cid = message.chat.id
    choice = message.text

    if choice.strip().lower() == _("general_cancel"):
        cancel_process(bot, message)
        return

    try:
        location_id = int(choice.split(":")[0].strip())
        selected_location = next((loc for loc in locations if loc['id'] == location_id), None)

        if selected_location:
            bot.send_message(
                cid,
                f"{_('locations_current')} '{selected_location['location']}'. {_('locations_new')}"
            )
            bot.register_next_step_handler(message, lambda msg: handle_edit_location_name(bot, msg, selected_location))
        else:
            bot.send_message(cid, _("general_cancel"))
            list_locations_for_selection(bot, message, "edit")
    except ValueError:
        bot.send_message(cid, _('locations_invalid_selection'))
        list_locations_for_selection(bot, message, "edit")


# Handle editing the location name
def handle_edit_location_name(bot, message, location):
    """
    Handle editing the location name and proceed to address editing.
    """
    cid = message.chat.id
    new_location_name = message.text.strip()

    if new_location_name.lower() == _("general_cancel"):
        cancel_process(bot, message)
        return

    if new_location_name.lower() == "skip":
        new_location_name = location['location']

    bot.send_message(
        cid,
        f"{_('locations_current_address')} '{location['address']}'. {_('locations_new_address')}"
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
    new_address = message.text.strip()

    if new_address.lower() == _("general_cancel"):
        cancel_process(bot, message)
        return

    if new_address.lower() == "skip":
        # Keep the address unchanged
        response = requests.get(f"{BASE_URL}/locations/{location_id}")
        if response.status_code == 200:
            location = response.json()
            new_address = location['address']
        else:
            bot.send_message(cid, _("locations_failed_fetch"))
            return

    data = {"location": new_location_name, "address": new_address}
    response = requests.put(f"{BASE_URL}/locations/{location_id}", json=data)
    bot.send_message(cid, _("procesing"))

    if response.status_code == 200:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton("/menu"))
        bot.send_message(cid, _("plans_success"), reply_markup=markup)
        list_locations(bot, message)
    else:
        bot.send_message(cid, _("plans_fails"))


# Delete location handler
def handle_delete_location_selection(bot, message, locations):
    """
    Handle the selection of a location to delete.
    """
    cid = message.chat.id
    choice = message.text

    if choice.strip().lower() == _("general_cancel"):
        cancel_process(bot, message)
        return

    try:
        location_id = int(choice.split(":")[0].strip())
        selected_location = next((loc for loc in locations if loc['id'] == location_id), None)

        if selected_location:
            confirm_delete_location(bot, message, selected_location)
        else:
            bot.send_message(cid, _("plans_invalid_selection"))
            list_locations_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, _("payment_delete_action_invalid_input"))
        list_locations_for_selection(bot, message, "delete")


# Confirm delete location
def confirm_delete_location(bot, message, location):
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton("Yes"), types.KeyboardButton("Cancel"))

    bot.send_message(cid, f"{_('payment_delete_confirm')} '{location['location']}'?", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: execute_delete_location(bot, msg, location['id']))


def execute_delete_location(bot, message, location_id):
    """
    Execute the deletion of the selected location.
    """
    cid = message.chat.id

    if message.text.strip().lower() == _("general_yes"):
        response = requests.delete(f"{BASE_URL}/locations/{location_id}")
        bot.send_message(cid, _("procesing"))
        if response.status_code == 200:
            bot.send_message(cid, _("plans_success"))
        else:
            bot.send_message(cid, _("plans_fails"))
    else:
        bot.send_message(cid, _("plans_success"))

    list_locations(bot, message)


def handle_edit_location(bot, message):
    list_locations_for_selection(bot, message, "edit")


def handle_delete_location(bot, message):
    list_locations_for_selection(bot, message, "delete")
