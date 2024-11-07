# models/user.py
from db import db  # Import db from db.py
from datetime import datetime

class PaymentMethods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(120), unique=False, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'method': self.method,
            'creation_date': self.creation_date.isoformat()
        }

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<PaymentMethod {fields}>'