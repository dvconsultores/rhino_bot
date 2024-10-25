# services/user_service.py
from models.users import User
from db import db  # Import db from db.py

def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def create_user(data):
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_user(user_id, data):
    user = User.query.get(user_id)
    if user:
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
    return user