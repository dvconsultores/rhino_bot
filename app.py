import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from db import db  # Import db from db.py

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with the Flask app
migrate = Migrate(app, db)

# Import models after app and db are initialized
import models

# Register blueprints
from controllers import all_blueprints
for bp in all_blueprints:
    app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)

# export FLASK_APP=app.py
# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade    
# install msgfmt in Dockerfile
# compile translations
# msgfmt telegram_bot/locales/es/LC_MESSAGES/messages.po -o telegram_bot/locales/es/LC_MESSAGES/messages.mo
# msgfmt telegram_bot/locales/en/LC_MESSAGES/messages.po -o telegram_bot/locales/en/LC_MESSAGES/messages.mo