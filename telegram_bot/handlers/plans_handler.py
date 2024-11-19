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
    item1 = types.KeyboardButton("Cancel")
    markup.row(item1)
    return markup


def cancel_process(bot, message):
    """Handle the cancellation of the process."""
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("/menu")
    markup.row(item1)
    bot.send_message(cid, "Process canceled.", reply_markup=markup)


def list_plans(bot, message):
    """
    Fetch and display the list of all available plans.
    """
    cid = message.chat.id
    response = requests.get(f"{BASE_URL}/plans")

    if response.status_code == 200:
        plans = response.json()

        if plans:
            # Build a text representation of the plans
            plans_text = "*Available Plans:*\n"
            for plan in plans:
                plans_text += f"🔹 *ID*: {plan['id']} - *Name*: {plan['name']} - *Price*: ${plan['price']}\n"

            # Send the list of plans to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, plans_text, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(cid, "No plans available.")
    else:
        bot.send_message(cid, "Failed to fetch plans. Please try again later.")


# Add a new plan
def add_plan_handler(bot, message):
    """
    Start the process of adding a new plan.
    """
    markup = create_cancel_markup()
    bot.send_message(message.chat.id, "Please enter the name of the new plan:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: add_plan_name_handler(bot, msg))


def add_plan_name_handler(bot, message):
    """
    Handle the name input for the new plan and ask for the price.
    """
    if message.text.strip().lower() == "cancel":
        cancel_process(bot, message)
        return

    plan_name = message.text.strip()

    if not plan_name:
        bot.send_message(message.chat.id, "Plan name cannot be empty. Please try again.")
        add_plan_handler(bot, message)
        return

    bot.send_message(message.chat.id, "Please enter the price for the plan:")
    bot.register_next_step_handler(message, lambda msg: submit_new_plan(bot, msg, plan_name))


def submit_new_plan(bot, message, plan_name):
    """
    Submit the new plan to the backend.
    """
    if message.text.strip().lower() == "cancel":
        cancel_process(bot, message)
        return

    try:
        plan_price = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Invalid price. Please enter a valid number.")
        bot.register_next_step_handler(message, lambda msg: submit_new_plan(bot, msg, plan_name))
        return

    data = {"name": plan_name, "price": plan_price}
    response = requests.post(f"{BASE_URL}/plans", json=data)

    if response.status_code == 201:
        bot.send_message(message.chat.id, "Plan added successfully!")
        list_plans(bot, message)
    else:
        bot.send_message(message.chat.id, "Failed to add the plan. Please try again.")


# List all plans for selection
def list_plans_for_selection(bot, message, action):
    """
    Fetch and display the list of available plans for selection.
    """
    cid = message.chat.id
    response = requests.get(f"{BASE_URL}/plans")

    if response.status_code == 200:
        plans = response.json()

        if plans:
            # Display plans for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for plan in plans:
                button = types.KeyboardButton(f"{plan['id']}: {plan['name']} (${plan['price']})")
                markup.add(button)
            markup.add(types.KeyboardButton("Cancel"))
            bot.send_message(cid, "Select a plan to proceed:", reply_markup=markup)

            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_plan_selection(bot, msg, plans))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_plan_selection(bot, msg, plans))
        else:
            bot.send_message(cid, "No plans available.")
    else:
        bot.send_message(cid, "Failed to fetch plans. Please try again later.")

def handle_edit_plan_selection(bot, message, plans):
    """
    Handle the selection of a plan to edit.
    """
    cid = message.chat.id
    choice = message.text

    if choice.strip().lower() == "cancel":
        cancel_process(bot, message)
        return

    try:
        # Extract plan ID from the selected option
        plan_id = int(choice.split(":")[0].strip())
        selected_plan = next((p for p in plans if p['id'] == plan_id), None)

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Skip")

        if selected_plan:
            bot.send_message(
                cid,
                f"Enter the new name for the plan '{selected_plan['name']}' or type 'skip' to keep it unchanged:"
                , reply_markup=markup
            )
            bot.register_next_step_handler(message, lambda msg: handle_edit_plan_name(bot, msg, selected_plan))
        else:
            bot.send_message(cid, "Invalid selection. Please try again.")
            list_plans_for_selection(bot, message, "edit")
    except (ValueError, IndexError):
        bot.send_message(cid, "Invalid input. Please try again.")
        list_plans_for_selection(bot, message, "edit")

def handle_edit_plan_name(bot, message, plan):
    """
    Handle the name update for the selected plan.
    """
    cid = message.chat.id
    new_name = message.text.strip()

    if new_name.lower() == "cancel":
        cancel_process(bot, message)
        return

    if new_name.lower() == "skip":
        new_name = plan['name']

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Skip")    

    bot.send_message(
        cid,
        f"Enter the new price for the plan '{new_name}' or type 'skip' to keep it unchanged:"
        , reply_markup=markup
    )
    bot.register_next_step_handler(message, lambda msg: submit_edit_plan(bot, msg, plan, new_name))

def submit_edit_plan(bot, message, plan, new_name):
    """
    Submit the updated plan details to the backend.
    """
    cid = message.chat.id
    try:
        new_price = float(message.text.strip()) if message.text.strip().lower() != "skip" else plan['price']

        data = {"name": new_name, "price": new_price}
        response = requests.put(f"{BASE_URL}/plans/{plan['id']}", json=data)

        if response.status_code == 200:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            item1 = types.KeyboardButton(("/menu"))
            markup.row(item1)
            bot.send_message(cid, "Plan updated successfully.", reply_markup=markup)
        else:
            bot.send_message(cid, "Failed to update the plan. Please try again later.")
    except ValueError:
        bot.send_message(cid, "Invalid price. Please enter a valid number.")
        bot.register_next_step_handler(message, lambda msg: submit_edit_plan(bot, msg, plan, new_name))

    # Return to the list of plans
    list_plans_for_selection(bot, message, "edit")


# Handler for selecting a plan to delete
def handle_delete_plan_selection(bot, message, plans):
    cid = message.chat.id
    choice = message.text

    if choice.strip().lower() == "cancel":
        cancel_process(bot, message)
        return

    try:
        # Extract plan ID from the selected option
        plan_id = int(choice.split(":")[0].strip())
        selected_plan = next((p for p in plans if p['id'] == plan_id), None)

        if selected_plan:
            confirm_delete_plan(bot, message, selected_plan)
        else:
            bot.send_message(cid, "Invalid selection. Please try again.")
            list_plans_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, "Invalid input. Please try again.")
        list_plans_for_selection(bot, message, "delete")


# Confirmation for plan deletion
def confirm_delete_plan(bot, message, selected_plan):
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton("Yes"), types.KeyboardButton("Cancel"))

    # Send the confirmation message
    bot.send_message(cid, f"Are you sure you want to delete the plan '{selected_plan['name']}'?", reply_markup=markup)

    # Register the next step handler to capture the confirmation response
    bot.register_next_step_handler(message, lambda msg: handle_delete_plan_confirmation(bot, msg, selected_plan['id']))


# Handle delete confirmation and execute deletion
def handle_delete_plan_confirmation(bot, message, plan_id):
    cid = message.chat.id

    if message.text.strip().lower() == "yes":
        delete_plan(bot, message, plan_id)
    else:
        bot.send_message(cid, "Plan deletion canceled.")
        list_plans_for_selection(bot, message, "delete")


# Perform deletion
def delete_plan(bot, message, plan_id):
    cid = message.chat.id
    bot.send_message(cid, "Processing...")

    response = requests.delete(f"{BASE_URL}/plans/{plan_id}")

    if response.status_code == 200:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton(("/menu"))
        markup.row(item1)
        bot.send_message(cid, "Plan deleted successfully.", reply_markup=markup)
    else:
        bot.send_message(cid, "Failed to delete the plan. Please try again later.")

    # Return to the list of plans
    list_plans_for_selection(bot, message, "delete")


def edit_plan_handler(bot, message):
    list_plans_for_selection(bot, message, "edit")

def delete_plan_handler(bot, message):
    list_plans_for_selection(bot, message, "delete")

