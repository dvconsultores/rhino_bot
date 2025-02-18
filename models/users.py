# models/users.py
from db import db  # Import db from db.py
import enum
from datetime import datetime

class UserType(enum.Enum):
    coach = "coach"
    administrativo = "administrativo"
    cliente = "cliente"
    owner = "owner"

class Status(enum.Enum):
    activo = 'activo'
    inactivo = 'inactivo'    
    moroso = 'moroso'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    lastname = db.Column(db.String(120), unique=False, nullable=False)
    cedula = db.Column(db.BigInteger, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, unique=False, nullable=False)
    phone = db.Column(db.BigInteger, unique=False, nullable=False)
    instagram = db.Column(db.String(120), unique=True, nullable=True)
    type = db.Column(db.Enum(UserType), unique=False, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    estatus = db.Column(db.Enum(Status), unique=False, nullable=False, default=Status.activo)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'cedula': self.cedula,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat(),
            'phone': self.phone,
            'instagram': self.instagram,
            'type': self.type.value,
            'creation_date': self.creation_date.isoformat(),
            'telegram_id': self.telegram_id ,
            'estatus': self.estatus.value
        }

    def __repr__(self):
        fields = ', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))
        return f'<User {fields}>'
