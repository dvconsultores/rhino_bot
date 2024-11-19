import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.language_handler import edit_language, language_middleware
from handlers.user_handler import get_user, create_user
from handlers.payment_handler import start_payment
from handlers.payment_methods_handler import show_payment_method_list, list_payment_methods_for_selection, add_payment_method_handler, delete_payment_method_handler, edit_payment_method_handler 
from handlers.plans_handler import add_plan_handler, list_plans_for_selection, delete_plan_handler, edit_plan_handler, list_plans

# Load .env file
load_dotenv()

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
@language_middleware
def command_start(message):
    cid = message.chat.id
    nom = message.chat.first_name
    bot.send_message(cid, _("welcome1") + f"{nom} - {cid}" + _("welcome2") + f"{nom}")
    command_list(message)

@bot.message_handler(commands=['menu'])
@language_middleware
def command_list(message):
    cid = message.chat.id
    help_text = _("available")

    # Set up buttons with translated text
    buttons = [
        [InlineKeyboardButton(_("register"), callback_data="create_user")],
        [InlineKeyboardButton(_("plans"), callback_data="listSwing")],
        [InlineKeyboardButton(_("locations"), callback_data="SetSignalStatus")],
        [InlineKeyboardButton(_("schedule"), callback_data="BinanceGainers")],
        [InlineKeyboardButton(_("payment"), callback_data="start_payment")],
        [InlineKeyboardButton(_("administrator"), callback_data="listAdmin")],
        [InlineKeyboardButton(_("language"), callback_data="edit_language")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(cid, help_text, reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    # print(f"Callback data received: {call.data}")  # Debug statement
    options = {
        'menu': command_list,
        'edit_language': lambda msg: edit_language(bot, msg),
        'create_user': lambda msg: create_user(bot, msg),
        'start_payment': lambda msg: start_payment(bot, msg),
        
        # Administrator options
        'listAdmin': listAdmin,
        'payment_method_menu': payment_method_menu,
        'plans_menu': plans_menu,
         # 'users_menu': users_menu,
        'locations_menu': locations_menu,
        'coaches_menu': coaches_menu,

        # Payment method options
        'show_payment_method_list': lambda msg: show_payment_method_list(bot, msg),
        'delete_payment_method_handler': lambda msg: delete_payment_method_handler(bot, msg),
        'edit_payment_method_handler': lambda msg: edit_payment_method_handler(bot, msg),
        'add_payment_method_handler': lambda msg: add_payment_method_handler(bot, msg),

        # Plans options
        'add_plan_handler': lambda msg: add_plan_handler(bot, msg),
        'delete_plan_handler': lambda msg: delete_plan_handler(bot, msg),
        'edit_plan_handler': lambda msg: edit_plan_handler(bot, msg),
        'list_plans': lambda msg: list_plans(bot, msg)
    }
    func = options.get(call.data)
    if func:
        print(f"Calling function for {call.data}")  # Debug statement
        func(call.message)
    else:
        print(f"No function found for {call.data}")  # Debug statement

def listAdmin(m):
    cid = m.chat.id
    help_text =  _("administrator_options")
    # Define the buttons
    button1 = InlineKeyboardButton(_("administrator_payment_method"), callback_data="payment_method_menu")
    button2 = InlineKeyboardButton(_("administrator_payment_plans"), callback_data="plans_menu")
    button3 = InlineKeyboardButton(_("administrator_payment_locations"), callback_data="locations_menu")
    button4 = InlineKeyboardButton(_("administrator_payment_coaches"), callback_data="coaches_menu")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

def payment_method_menu(m):
    cid = m.chat.id
    help_text =  _("administrator_options") + ' - ' + _("administrator_payment_method")
    # Define the buttons
    button1 = InlineKeyboardButton(_("general_add"), callback_data="add_payment_method_handler")
    button2 = InlineKeyboardButton(_("general_update"), callback_data="edit_payment_method_handler")
    button3 = InlineKeyboardButton(_("general_delete"), callback_data="delete_payment_method_handler")
    button4 = InlineKeyboardButton(_("general_list"), callback_data="show_payment_method_list")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)  

def payment_menu(m):
    cid = m.chat.id
    help_text =  _("administrator_options") + ' - ' + _("administrator_payment_method")
    # Define the buttons
    button1 = InlineKeyboardButton(_("general_add"), callback_data="add_payment_method_handler")
    button2 = InlineKeyboardButton(_("general_update"), callback_data="edit_payment_method_handler")
    button3 = InlineKeyboardButton(_("general_delete"), callback_data="delete_payment_method_handler")
    button4 = InlineKeyboardButton(_("general_list"), callback_data="show_payment_method_list")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)

def locations_menu(m):
    cid = m.chat.id
    help_text =  _("administrator_options") + ' - ' + _("administrator_payment_locations")
    # Define the buttons
    button1 = InlineKeyboardButton(_("general_add"), callback_data="add_payment_method_handler")
    button2 = InlineKeyboardButton(_("general_update"), callback_data="edit_payment_method_handler")
    button3 = InlineKeyboardButton(_("general_delete"), callback_data="delete_payment_method_handler")
    button4 = InlineKeyboardButton(_("general_list"), callback_data="show_payment_method_list")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

def coaches_menu(m):
    cid = m.chat.id
    help_text =  _("administrator_options") + ' - ' + _("administrator_payment_coaches")
    # Define the buttons
    button1 = InlineKeyboardButton(_("general_add"), callback_data="add_payment_method_handler")
    button2 = InlineKeyboardButton(_("general_update"), callback_data="edit_payment_method_handler")
    button3 = InlineKeyboardButton(_("general_delete"), callback_data="delete_payment_method_handler")
    button4 = InlineKeyboardButton(_("general_list"), callback_data="show_payment_method_list")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

def plans_menu(m):
    cid = m.chat.id
    help_text =  _("administrator_options") + ' - ' + _("administrator_payment_method")
    # Define the buttons
    button1 = InlineKeyboardButton(_("general_add"), callback_data="add_plan_handler")
    button2 = InlineKeyboardButton(_("general_update"), callback_data="edit_plan_handler")
    button3 = InlineKeyboardButton(_("general_delete"), callback_data="delete_plan_handler")
    button4 = InlineKeyboardButton(_("general_list"), callback_data="list_plans")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)                                 


bot.polling()
