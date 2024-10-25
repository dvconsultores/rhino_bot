import os
import multiprocessing
import time
from flask import Flask
from flask_migrate import Migrate
from flasgger import Swagger
from dotenv import load_dotenv
from db import db  # Import db from db.py

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with the Flask app
migrate = Migrate(app, db)
swagger = Swagger(app)  # Initialize Swagger

# Import models after app and db are initialized
import models

# Register blueprints
from controllers import all_blueprints
for bp in all_blueprints:
    app.register_blueprint(bp)

# Function to run the Flask app
def run_flask_app():
    os.system("gunicorn -c gunicorn_config.py app:app")

# Function to run flask in debug mode
def run_flask_app_debug():
    app.run(debug=True)    

# Function to run forever.py
def run_forever_script():
    import forever  # Import the forever.py script

if __name__ == '__main__':
    # # Start the Flask app in a separate process
    # flask_process = multiprocessing.Process(target=run_flask_app)
    # flask_process.start()

    # # Start the forever.py script in a separate process
    # forever_process = multiprocessing.Process(target=run_forever_script)
    # forever_process.start()

    # # Join processes to keep the main program running
    # flask_process.join()
    # forever_process.join()

    run_flask_app_debug()


# export FLASK_APP=app.py
# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade    
# install msgfmt in Dockerfile
# compile translations
# msgfmt telegram_bot/locales/es/LC_MESSAGES/messages.po -o telegram_bot/locales/es/LC_MESSAGES/messages.mo
# msgfmt telegram_bot/locales/en/LC_MESSAGES/messages.po -o telegram_bot/locales/en/LC_MESSAGES/messages.mo