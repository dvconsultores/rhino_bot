# models/location.py
from db import db  # Import db from db.py
from datetime import datetime

class Locations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120), unique=False, nullable=False)
    address = db.Column(db.String(120), unique=False, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Convert the Locations model instance to a dictionary."""
        return {
            'id': self.id,
            'location': self.location,
            'address': self.address,
            'creation_date': self.creation_date.isoformat()
        }

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Locations {fields}>'
