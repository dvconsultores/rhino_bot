# models/schedule.py
from db import db  # Import db from db.py
import enum
from models.locations import Locations
from datetime import datetime

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    days = db.Column(db.String(120), unique=False, nullable=False)
    time_init = db.Column(db.String(120), unique=False, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    location = db.relationship('Locations', backref=db.backref('schedule', lazy=True))

    def to_dict(self):
        """Convert the Schedule model instance to a dictionary."""
        try:
            location_name = self.location.location if self.location else None
        except sqlalchemy.orm.exc.DetachedInstanceError:
            location_name = None

        return {
            'id': self.id,
            'location_id': self.location_id,
            'location_name': location_name,
            'days': self.days,
            'time_init': self.time_init,
            'creation_date': self.creation_date.isoformat()
        }

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Schedule {fields}>'