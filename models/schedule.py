# models/schedule.py
from db import db  # Import db from db.py
import enum
from models.locations import Locations
from datetime import datetime

class DaysOfWeek(enum.Enum):
    monday = "Lunes"
    tuesday = "Martes"
    wednesday = "Miercoles"
    thursday = "Jueves"
    friday = "Viernes"
    saturday = "Sabado"
    sunday = "Domingo"

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    days = db.Column(db.Enum(DaysOfWeek), nullable=False)
    time_init = db.Column(db.Time, nullable=False)
    time_end = db.Column(db.Time, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    location = db.relationship('Location', backref=db.backref('schedules', lazy=True))

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<Schedule {fields}>'