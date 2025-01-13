import os
from enum import Enum
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.language_handler import edit_language
from handlers.user_handler import get_user, create_user
from handlers.payment_handler import start_payment
from handlers.payment_methods_handler import show_payment_method_list, list_payment_methods_for_selection, add_payment_method_handler, delete_payment_method_handler, edit_payment_method_handler 
from handlers.plans_handler import add_plan_handler, list_plans_for_selection, delete_plan_handler, edit_plan_handler, list_plans, list_plans_customer
from handlers.locations_handler import list_locations, add_location_handler, handle_edit_location, handle_delete_location, list_locations_customer
from handlers.schedule_handler import add_schedule_handler, delete_schedule_handler, edit_schedule_handler, list_schedules, list_schedules_customer
from handlers.coaches_handler import add_coach_handler, delete_coach_handler, edit_coach_handler, list_coaches
from handlers.attendance_handler import add_attendance_handler, list_coaches_for_attendance, handle_coach_selection, list_locations_for_attendance
from deep_translator import GoogleTranslator
import requests
#import redis
# Load .env file
load_dotenv()

# Initialize Redis client
# redis_host = os.getenv('REDIS_HOST', 'localhost')
# redis_port = os.getenv('REDIS_PORT', 6380)
# try:
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
#     redis_client.ping()  # Check if the connection is successful
# except redis.ConnectionError as e:
#     print(f"Redis connection error: {e}")
#     redis_client = None

# Ensure the reports directory exists
if not os.path.exists('reports'):
    os.makedirs('reports')

def generate_user_report():
    """Fetch user data from the API and generate an Excel report."""
    response = requests.get("http://web:5000/users")
    if response.status_code == 200:
        users = response.json()
        df = pd.DataFrame(users)
        file_path = os.path.join('reports', 'user_report.xlsx')
        df.to_excel(file_path, index=False)
        return file_path
    else:
        print("Failed to fetch user data")
        return None    

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://web:5000")

class UserType(Enum):
    coach = "coach"
    administrativo = "administrativo"
    cliente = "cliente"
    owner = "owner"

def get_user_type(cid):
    """Fetch the user's type via an API request or database query."""
    # This is a placeholder function. Replace it with the actual implementation.
    response = requests.get(f"{BASE_URL}/users/{cid}")
    if response.status_code == 200:
        return UserType(response.json().get('type'))
    return UserType.cliente  # Default to 'cliente' if not found


def translate(text, target_lang='es'):
    """Translate text to the target language using GoogleTranslator."""
    if target_lang == 'es':
        return text
    return GoogleTranslator(source='auto', target=target_lang).translate(text)

def get_language_by_telegram_id(cid):
    # """Fetch the user's language preference via an API request."""
    # # Check Redis for the language preference
    # language = redis_client.get(f"language:{cid}")
    # if language:
    #     return language

    # # If not found in Redis, fetch from API
    # response = requests.get(f"{BASE_URL}/languages/{cid}")
    # if response.status_code == 200:
    #     language = response.json().get('Language', 'es')
    #     # Store the language preference in Redis
    #     redis_client.set(f"language:{cid}", language)
    #     return language

    return 'es'

@bot.message_handler(commands=['start'])
def command_start(message):
    cid = message.chat.id
    nom = message.chat.first_name
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    welcome_text = translate("Bienvenido", target_lang) + f" {nom} - {cid} " + translate("a nuestro bot,", target_lang) + f" {nom}"
    bot.send_message(cid, welcome_text)
    command_list(message)

@bot.message_handler(commands=['menu'])
@bot.message_handler(commands=['menu'])
def command_list(message):
    cid = message.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    user_type = get_user_type(cid)  # Get the user's type
    help_text = translate("Aquí están los comandos disponibles:", target_lang)

    # Set up buttons based on user type
    if user_type == UserType.coach:
        buttons = [
            [InlineKeyboardButton(translate("🤖 Registrar - ✏️ Actualizar Datos", target_lang), callback_data="create_user")],
            [InlineKeyboardButton(translate("📋 Ver Planes", target_lang), callback_data="list_plans_customer")],
            [InlineKeyboardButton(translate("📍 Ver Ubicaciones", target_lang), callback_data="list_locations_customer")],
            [InlineKeyboardButton(translate("📅 Ver Horarios", target_lang), callback_data="list_schedules_customer")],
            [InlineKeyboardButton(translate("💳 Registrar Pago", target_lang), callback_data="start_payment")],
            [InlineKeyboardButton(translate("🏅 Coachs", target_lang), callback_data="add_attendance_handler")],
            # [InlineKeyboardButton(translate("🌐 Cambiar Idioma", target_lang), callback_data="edit_language")]
        ]
    elif user_type == UserType.administrativo:
        buttons = [
            [InlineKeyboardButton(translate("🤖 Registrar - ✏️ Actualizar Datos", target_lang), callback_data="create_user")],
            [InlineKeyboardButton(translate("📋 Ver Planes", target_lang), callback_data="list_plans_customer")],
            [InlineKeyboardButton(translate("📍 Ver Ubicaciones", target_lang), callback_data="list_locations_customer")],
            [InlineKeyboardButton(translate("📅 Ver Horarios", target_lang), callback_data="list_schedules_customer")],
            [InlineKeyboardButton(translate("💳 Registrar Pago", target_lang), callback_data="start_payment")],
            [InlineKeyboardButton(translate("🛠️ Administrar", target_lang), callback_data="listAdmin")],
            # [InlineKeyboardButton(translate("🌐 Cambiar Idioma", target_lang), callback_data="edit_language")]
        ]
    elif user_type == UserType.cliente:
        buttons = [
            [InlineKeyboardButton(translate("🤖 Registrar - ✏️ Actualizar Datos", target_lang), callback_data="create_user")],
            [InlineKeyboardButton(translate("📋 Ver Planes", target_lang), callback_data="list_plans_customer")],
            [InlineKeyboardButton(translate("📍 Ver Ubicaciones", target_lang), callback_data="list_locations_customer")],
            [InlineKeyboardButton(translate("📅 Ver Horarios", target_lang), callback_data="list_schedules_customer")],
            [InlineKeyboardButton(translate("💳 Registrar Pago", target_lang), callback_data="start_payment")],
            # [InlineKeyboardButton(translate("🌐 Cambiar Idioma", target_lang), callback_data="edit_language")]
        ]
    elif user_type == UserType.owner:
        buttons = [
            [InlineKeyboardButton(translate("🤖 Registrar - ✏️ Actualizar Datos", target_lang), callback_data="create_user")],
            [InlineKeyboardButton(translate("📋 Ver Planes", target_lang), callback_data="list_plans_customer")],
            [InlineKeyboardButton(translate("📍 Ver Ubicaciones", target_lang), callback_data="list_locations_customer")],
            [InlineKeyboardButton(translate("📅 Ver Horarios", target_lang), callback_data="list_schedules_customer")],
            [InlineKeyboardButton(translate("💳 Registrar Pago", target_lang), callback_data="start_payment")],
            [InlineKeyboardButton(translate("🏅 Coachs", target_lang), callback_data="add_attendance_handler")],
            [InlineKeyboardButton(translate("🛠️ Administrar", target_lang), callback_data="listAdmin")],
            # [InlineKeyboardButton(translate("🌐 Cambiar Idioma", target_lang), callback_data="edit_language")]
        ]

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(cid, help_text, reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    options = {
        'menu': command_list,
        'edit_language': lambda msg: edit_language(bot, msg),
        'create_user': lambda msg: create_user(bot, msg),
        'start_payment': lambda msg: start_payment(bot, msg),
        
        # Administrator options
        'listAdmin': listAdmin,
        'payment_method_menu': payment_method_menu,
        'plans_menu': plans_menu,
        'locations_menu': locations_menu,
        'coaches_menu': coaches_menu,
        'schedule_menu': schedule_menu,

        # Payment method options
        'show_payment_method_list': lambda msg: show_payment_method_list(bot, msg),
        'delete_payment_method_handler': lambda msg: delete_payment_method_handler(bot, msg),
        'edit_payment_method_handler': lambda msg: edit_payment_method_handler(bot, msg),
        'add_payment_method_handler': lambda msg: add_payment_method_handler(bot, msg),

        # Plans options
        'add_plan_handler': lambda msg: add_plan_handler(bot, msg),
        'delete_plan_handler': lambda msg: delete_plan_handler(bot, msg),
        'edit_plan_handler': lambda msg: edit_plan_handler(bot, msg),
        'list_plans': lambda msg: list_plans(bot, msg),
        'list_plans_customer': lambda msg: list_plans_customer(bot, msg),

        # Locations options
        'list_locations': lambda msg: list_locations(bot, msg),
        'list_locations_customer': lambda msg: list_locations_customer(bot, msg),
        'add_location_handler': lambda msg: add_location_handler(bot, msg),
        'handle_edit_location': lambda msg: handle_edit_location(bot, msg),
        'handle_delete_location': lambda msg: handle_delete_location(bot, msg),

        # Schedule options
        'add_schedule_handler': lambda msg: add_schedule_handler(bot, msg),
        'delete_schedule_handler': lambda msg: delete_schedule_handler(bot, msg),
        'edit_schedule_handler': lambda msg: edit_schedule_handler(bot, msg),
        'list_schedules': lambda msg: list_schedules(bot, msg),
        'list_schedules_customer': lambda msg: list_schedules_customer(bot, msg),

        # Coaches options
        'add_coach_handler': lambda msg: add_coach_handler(bot, msg),
        'delete_coach_handler': lambda msg: delete_coach_handler(bot, msg),
        'edit_coach_handler': lambda msg: edit_coach_handler(bot, msg),
        'list_coaches': lambda msg: list_coaches(bot, msg),

        # Attendance options
        'add_attendance_handler': lambda msg: add_attendance_handler(bot, msg),

        # Reports
        'reporte_clientes': send_user_report,
    }
    func = options.get(call.data)
    if func:
        # print(f"Calling function for {call.data}")  # Debug statement
        func(call.message)
    else:
        print(f"No function found for {call.data}")  # Debug statement

def listAdmin(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("💳 Métodos de pago", target_lang), callback_data="payment_method_menu")
    button2 = InlineKeyboardButton(translate("📋 Planes", target_lang), callback_data="plans_menu")
    button3 = InlineKeyboardButton(translate("📍 Ubicaciones", target_lang), callback_data="locations_menu")
    button4 = InlineKeyboardButton(translate("📅 Horarios", target_lang), callback_data="schedule_menu")
    button5 = InlineKeyboardButton(translate("🏅 Entrenadores", target_lang), callback_data="coaches_menu")
    button6 = InlineKeyboardButton(translate("📊 Reporte Clientes", target_lang), callback_data="reporte_clientes")
    button7 = InlineKeyboardButton(translate("📊 Reporte Pagos", target_lang), callback_data="coaches_menu")
    button8 = InlineKeyboardButton(translate("📊 Reporte Coachs", target_lang), callback_data="coaches_menu")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4], [button5], [button6], [button7], [button8]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

@bot.callback_query_handler(func=lambda call: call.data == "reporte_clientes")
def send_user_report(call):
    """Handle the button click to generate and send the user report."""
    cid = call.message.chat.id
    file_path = generate_user_report()
    if file_path:
        with open(file_path, 'rb') as file:
            bot.send_document(cid, file)
    else:
        bot.send_message(cid, "Error generating the report.")

def payment_method_menu(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang) + ' - ' + translate("Métodos de pago", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("➕ Crear", target_lang), callback_data="add_payment_method_handler")
    button2 = InlineKeyboardButton(translate("✏️ Actualizar", target_lang), callback_data="edit_payment_method_handler")
    button3 = InlineKeyboardButton(translate("🗑️ Eliminar", target_lang), callback_data="delete_payment_method_handler")
    button4 = InlineKeyboardButton(translate("📋 Listar", target_lang), callback_data="show_payment_method_list")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)  

def payment_menu(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang) + ' - ' + translate("Métodos de pago", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("➕ Crear", target_lang), callback_data="add_payment_method_handler")
    button2 = InlineKeyboardButton(translate("✏️ Actualizar", target_lang), callback_data="edit_payment_method_handler")
    button3 = InlineKeyboardButton(translate("🗑️ Eliminar", target_lang), callback_data="delete_payment_method_handler")
    button4 = InlineKeyboardButton(translate("📋 Listar", target_lang), callback_data="show_payment_method_list")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)

def locations_menu(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang) + ' - ' + translate("Ubicaciones", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("➕ Crear", target_lang), callback_data="add_location_handler")
    button2 = InlineKeyboardButton(translate("✏️ Actualizar", target_lang), callback_data="handle_edit_location")
    button3 = InlineKeyboardButton(translate("🗑️ Eliminar", target_lang), callback_data="handle_delete_location")
    button4 = InlineKeyboardButton(translate("📋 Listar", target_lang), callback_data="list_locations")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

def coaches_menu(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang) + ' - ' + translate("Entrenadores", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("➕ Crear", target_lang), callback_data="add_coach_handler")
    button2 = InlineKeyboardButton(translate("✏️ Actualizar", target_lang), callback_data="edit_coach_handler")
    button3 = InlineKeyboardButton(translate("🗑️ Eliminar", target_lang), callback_data="delete_coach_handler")
    button4 = InlineKeyboardButton(translate("📋 Listar", target_lang), callback_data="list_coaches")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

def plans_menu(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang) + ' - ' + translate("Planes", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("➕ Crear", target_lang), callback_data="add_plan_handler")
    button2 = InlineKeyboardButton(translate("✏️ Actualizar", target_lang), callback_data="edit_plan_handler")
    button3 = InlineKeyboardButton(translate("🗑️ Eliminar", target_lang), callback_data="delete_plan_handler")
    button4 = InlineKeyboardButton(translate("📋 Listar", target_lang), callback_data="list_plans")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup) 

def schedule_menu(m):
    cid = m.chat.id
    target_lang = get_language_by_telegram_id(cid)  # Get the user's language preference
    help_text = translate("Opciones de administrador", target_lang) + ' - ' + translate("Horarios", target_lang)
    # Define the buttons
    button1 = InlineKeyboardButton(translate("➕ Crear", target_lang), callback_data="add_schedule_handler")
    button2 = InlineKeyboardButton(translate("✏️ Actualizar", target_lang), callback_data="edit_schedule_handler")
    button3 = InlineKeyboardButton(translate("🗑️ Eliminar", target_lang), callback_data="delete_schedule_handler")
    button4 = InlineKeyboardButton(translate("📋 Listar", target_lang), callback_data="list_schedules")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4]]
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)                                    

bot.polling()
