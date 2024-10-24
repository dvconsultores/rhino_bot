# services/location_service.py
from models.locations import Locations
from db import db  # Import db from db.py

def get_all_locations():
    return Locations.query.all()

def get_location_by_id(location_id):
    return Locations.query.get(location_id)

def create_location(data):
    new_location = Locations(**data)
    db.session.add(new_location)
    db.session.commit()
    return new_location

def update_location(location_id, data):
    location = Locations.query.get(location_id)
    if location:
        for key, value in data.items():
            setattr(location, key, value)
        db.session.commit()
    return location

def delete_location(location_id):
    location = Locations.query.get(location_id)
    if location:
        db.session.delete(location)
        db.session.commit()
    return location