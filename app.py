import os
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


# Function to run flask in debug mode
def run_flask_app_debug():
    app.run(debug=True)    


if __name__ == '__main__':
    run_flask_app_debug()


# export FLASK_APP=app.py
# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade    
# install msgfmt in Dockerfile
# compile translations
# ./language.sh