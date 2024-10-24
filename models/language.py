# models/user.py
from db import db  # Import db from db.py
from datetime import datetime


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_telegram = db.Column(db.BigInteger, unique=True, nullable=False)
    Language = db.Column(db.String(2), unique=False, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Language {fields}>'