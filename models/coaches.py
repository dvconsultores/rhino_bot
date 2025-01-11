from db import db  # Import db from db.py
from datetime import datetime

class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(120), unique=True, nullable=False)
    names = db.Column(db.String(120), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    location = db.relationship('Locations', backref=db.backref('coaches', lazy=True))

    def to_dict(self):
        """Convert the Coach model instance to a dictionary."""
        return {
            'id': self.id,
            'cedula': self.cedula,
            'names': self.names,
            'location_id': self.location_id,
            'location_name': self.location.location if self.location else None,
            'creation_date': self.creation_date.isoformat()
        }

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Coach {fields}>'