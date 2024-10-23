from db import db  # Import db from db.py
from models.users import User
from models.locations import Locations
import enum
from datetime import datetime

class Status(enum.Enum):
    activo = "Activo"
    inactivo = "Inactivo"

class LocationUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Correcting ForeignKey table names and adding user_id and location_id correctly
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Table name should match the class name 'User'
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)  # No change needed here, just ensure the table is correctly pluralized
    
    # Status column with default value
    status = db.Column(db.Enum(Status), nullable=False, default=Status.activo)
    
    # Creation date with default datetime
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('location_users', lazy=True))  # Correct the class name to 'User', not 'Users'
    location = db.relationship('Locations', backref=db.backref('location_users', lazy=True))
    
    # __repr__ method to return a string representation of the object
    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<LocationUsers {fields}>'
