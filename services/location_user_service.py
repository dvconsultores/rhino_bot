# services/location_user_service.py
from models.location_users import LocationUsers
from db import db  # Import db from db.py

def get_all_location_users():
    return LocationUsers.query.all()

def get_location_user_by_id(location_user_id):
    return LocationUsers.query.get(location_user_id)

def create_location_user(data):
    new_location_user = LocationUsers(**data)
    db.session.add(new_location_user)
    db.session.commit()
    return new_location_user

def update_location_user(location_user_id, data):
    location_user = LocationUsers.query.get(location_user_id)
    if location_user:
        for key, value in data.items():
            setattr(location_user, key, value)
        db.session.commit()
    return location_user

def delete_location_user(location_user_id):
    location_user = LocationUsers.query.get(location_user_id)
    if location_user:
        db.session.delete(location_user)
        db.session.commit()
    return location_user