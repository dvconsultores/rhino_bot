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

def list_plans(bot, message):
    """
    Fetch and display the list of all available plans.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/plans")

    if response.status_code == 200:
        plans = response.json()

        if plans:
            # Build a text representation of the plans
            plans_text = translate("Planes disponibles:", target_lang) + "\n"
            for plan in plans:
                plans_text += f"🔹 *{translate('ID del plan:', target_lang)}*: {plan['id']} - *{translate('Nombre del plan:', target_lang)}*: {plan['name']} - *{translate('Precio del plan:', target_lang)}*: ${plan['price']}\n"

            # Send the list of plans to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, plans_text, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(cid, translate("No hay planes disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los planes.", target_lang))

def list_plans_customer(bot, message):
    """
    Fetch and display the list of all available plans.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/plans")

    if response.status_code == 200:
        plans = response.json()

        if plans:
            # Build a text representation of the plans
            plans_text = translate("Planes disponibles:", target_lang) + "\n\n"
            for plan in plans:
                plans_text += f"🔹 *{plan['name']} \n *{translate('Precio:', target_lang)}*: ${plan['price']}\n\n"

            # Send the list of plans to the user
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton("/menu"))
            bot.send_message(cid, plans_text, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(cid, translate("No hay planes disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los planes.", target_lang))        

def add_plan_handler(bot, message):
    """
    Start the process of adding a new plan.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = create_cancel_markup(target_lang)
    bot.send_message(message.chat.id, translate("Por favor, ingrese el nombre del plan:", target_lang), reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: add_plan_name_handler(bot, msg))

def add_plan_name_handler(bot, message):
    """
    Handle the name input for the new plan and ask for the price.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    plan_name = message.text.strip()

    if not plan_name:
        bot.send_message(message.chat.id, translate("El nombre del plan no puede estar vacío.", target_lang))
        add_plan_handler(bot, message)
        return

    bot.send_message(message.chat.id, translate("Por favor, ingrese el precio del plan:", target_lang))
    bot.register_next_step_handler(message, lambda msg: submit_new_plan(bot, msg, plan_name))

def submit_new_plan(bot, message, plan_name):
    """
    Submit the new plan to the backend.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        plan_price = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, translate("El precio del plan no puede estar vacío.", target_lang))
        bot.register_next_step_handler(message, lambda msg: submit_new_plan(bot, msg, plan_name))
        return

    data = {"name": plan_name, "price": plan_price}
    response = requests.post(f"{BASE_URL}/plans", json=data)

    if response.status_code == 201:
        bot.send_message(message.chat.id, translate("Plan creado con éxito.", target_lang))
        list_plans(bot, message)
    else:
        bot.send_message(message.chat.id, translate("Error al crear el plan.", target_lang))

def list_plans_for_selection(bot, message, action):
    """
    Fetch and display the list of available plans for selection.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    response = requests.get(f"{BASE_URL}/plans")

    if response.status_code == 200:
        plans = response.json()

        if plans:
            # Display plans for selection with a ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for plan in plans:
                button = types.KeyboardButton(f"{plan['id']}: {plan['name']} (${plan['price']})")
                markup.add(button)
            markup.add(types.KeyboardButton(translate("Cancelar", target_lang)))
            bot.send_message(cid, translate("Seleccione un plan:", target_lang), reply_markup=markup)

            # Register the next step handler based on the action (edit or delete)
            if action == "delete":
                bot.register_next_step_handler(message, lambda msg: handle_delete_plan_selection(bot, msg, plans))
            elif action == "edit":
                bot.register_next_step_handler(message, lambda msg: handle_edit_plan_selection(bot, msg, plans))
        else:
            bot.send_message(cid, translate("No hay planes disponibles.", target_lang))
    else:
        bot.send_message(cid, translate("Error al obtener los planes.", target_lang))

def handle_edit_plan_selection(bot, message, plans):
    """
    Handle the selection of a plan to edit.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        # Extract plan ID from the selected option
        plan_id = int(choice.split(":")[0].strip())
        selected_plan = next((p for p in plans if p['id'] == plan_id), None)

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(translate("Omitir", target_lang))

        if selected_plan:
            bot.send_message(
                cid,
                f"{translate('✏️ Actualizar nombre del plan:', target_lang)} '{selected_plan['name']}' {translate('o ingrese un nuevo nombre:', target_lang)}",
                reply_markup=markup
            )
            bot.register_next_step_handler(message, lambda msg: handle_edit_plan_name(bot, msg, selected_plan))
        else:
            bot.send_message(cid, translate("Selección de plan inválida.", target_lang))
            list_plans_for_selection(bot, message, "edit")
    except (ValueError, IndexError):
        bot.send_message(cid, translate("Selección de plan inválida.", target_lang))
        list_plans_for_selection(bot, message, "edit")

def handle_edit_plan_name(bot, message, plan):
    """
    Handle the name update for the selected plan.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    new_name = message.text.strip()

    if new_name.lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    if new_name.lower() == translate("Omitir", target_lang).lower():
        new_name = plan['name']

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(translate("Omitir", target_lang))

    bot.send_message(
        cid,
        f"{translate('✏️ Actualizar precio del plan:', target_lang)} '{new_name}' {translate('o ingrese un nuevo precio:', target_lang)}",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, lambda msg: submit_edit_plan(bot, msg, plan, new_name))

def submit_edit_plan(bot, message, plan, new_name):
    """
    Submit the updated plan details to the backend.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    try:
        new_price = float(message.text.strip()) if message.text.strip().lower() != translate("Omitir", target_lang).lower() else plan['price']
        bot.send_message(cid, translate("Procesando...", target_lang))
        data = {"name": new_name, "price": new_price}
        response = requests.put(f"{BASE_URL}/plans/{plan['id']}", json=data)

        if response.status_code == 200:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            item1 = types.KeyboardButton("/menu")
            markup.row(item1)
            bot.send_message(cid, translate("Plan actualizado con éxito.", target_lang), reply_markup=markup)
        else:
            bot.send_message(cid, translate("Error al ✏️ Actualizar el plan.", target_lang))
    except ValueError:
        bot.send_message(cid, translate("El precio del plan no puede estar vacío.", target_lang))
        bot.register_next_step_handler(message, lambda msg: submit_edit_plan(bot, msg, plan, new_name))

    # Return to the list of plans
    list_plans(bot, message)

def handle_delete_plan_selection(bot, message, plans):
    """
    Handle the selection of a plan to delete.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    choice = message.text

    if choice.strip().lower() == translate("Cancelar", target_lang).lower():
        cancel_process(bot, message)
        return

    try:
        # Extract plan ID from the selected option
        plan_id = int(choice.split(":")[0].strip())
        selected_plan = next((p for p in plans if p['id'] == plan_id), None)

        if selected_plan:
            confirm_delete_plan(bot, message, selected_plan)
        else:
            bot.send_message(cid, translate("Selección de plan inválida.", target_lang))
            list_plans_for_selection(bot, message, "delete")
    except ValueError:
        bot.send_message(cid, translate("Selección de plan inválida.", target_lang))
        list_plans_for_selection(bot, message, "delete")

def confirm_delete_plan(bot, message, selected_plan):
    """
    Confirm the deletion of the selected plan.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(types.KeyboardButton(translate("Sí", target_lang)), types.KeyboardButton(translate("Cancelar", target_lang)))

    # Send the confirmation message
    bot.send_message(cid, f"{translate('¿Está seguro de que desea eliminar el plan', target_lang)} '{selected_plan['name']}'?", reply_markup=markup)

    # Register the next step handler to capture the confirmation response
    bot.register_next_step_handler(message, lambda msg: handle_delete_plan_confirmation(bot, msg, selected_plan['id']))

def handle_delete_plan_confirmation(bot, message, plan_id):
    """
    Handle delete confirmation and execute deletion.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    if message.text == translate("Sí", target_lang):
        delete_plan(bot, message, plan_id)
    else:
        bot.send_message(cid, translate("Proceso cancelado.", target_lang))

def delete_plan(bot, message, plan_id):
    """
    Perform deletion.
    """
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)
    bot.send_message(cid, translate("Procesando...", target_lang))
    response = requests.delete(f"{BASE_URL}/plans/{plan_id}")

    if response.status_code == 200:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1 = types.KeyboardButton("/menu")
        markup.row(item1)
        bot.send_message(cid, translate("Plan eliminado con éxito.", target_lang), reply_markup=markup)
    else:
        bot.send_message(cid, translate("Error al eliminar el plan.", target_lang))

    # Return to the list of plans
    list_plans(bot, message)

def edit_plan_handler(bot, message):
    list_plans_for_selection(bot, message, "edit")

def delete_plan_handler(bot, message):
    list_plans_for_selection(bot, message, "delete")

