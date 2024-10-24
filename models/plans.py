# models/user.py
from db import db  # Import db from db.py
from datetime import datetime

class Plans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<User {fields}>'